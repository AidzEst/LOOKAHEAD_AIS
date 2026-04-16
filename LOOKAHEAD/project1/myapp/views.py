from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from .models import login_info, product, category, purchaseorder, salesorder, receipt, membership, expenses, RestockOrder
import json
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta
from django.views.decorators.http import require_POST
from django.db import transaction
from django.db.models import Sum, Avg
from django.db.models.functions import TruncDate
from django.views.decorators.csrf import csrf_exempt


# HELPER FUNCTION (GLOBAL USER)
def get_logged_in_user(request):
    name = request.session.get('name')
    if not name:
        return None
    try:
        return login_info.objects.get(name=name)
    except login_info.DoesNotExist:
        return None


# JSON ENCODER
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)


# INVENTORY
def inventory(request):
    user = get_logged_in_user(request)

    all_products = product.objects.all()
    return render(request, 'final_inventory.html', {
        'products': all_products,
        'user': user
    })

# CATEGORIES
def categories(request):
    user = get_logged_in_user(request)
    all_categories = category.objects.all()

    if request.method == "POST":
        category_name_input = request.POST.get("categoryname")
        if category_name_input:
            new_category = category(category_name=category_name_input)
            new_category.save()

    return render(request, 'final_category.html', {
        'categories': all_categories,
        'user': user
    })


# PURCHASE ORDER
def purchase_order(request):
    user = get_logged_in_user(request)

    all_porders = purchaseorder.objects.all()
    all_categories = category.objects.all()

    latest_purchase = purchaseorder.objects.order_by('-purchase_id').first()
    next_purchase_id = latest_purchase.purchase_id + 1 if latest_purchase else 1

    latest_product = product.objects.order_by('-product_id').first()
    next_product_id = latest_product.product_id + 1 if latest_product else 1

    if request.method == "POST":
        purchase_id_input = request.POST.get("purchaseid")
        product_id_input = request.POST.get("productid")
        product_name_input = request.POST.get("itemname")
        qty = request.POST.get("qty")
        price = request.POST.get("price")
        shipdate = request.POST.get("shipdate")
        categor = request.POST.get("option_category")

        int_qty = int(qty)
        float_price = float(price)
        markup_price = float_price + (float_price * 0.10)
        total_cost = int_qty * markup_price

        try:
            category_instance = category.objects.get(category_id=categor)
        except category.DoesNotExist:
            category_instance = None

        new_product = product(
            product_id=product_id_input,
            product_name=product_name_input,
            quantity=int_qty,
            purchase_price=markup_price,
            shipment_date=shipdate,
            category_id=category_instance.category_id if category_instance else None,
        )
        new_product.save()

        new_purchase_order = purchaseorder(
            purchase_id=purchase_id_input,
            product_id=new_product.product_id,
            purchase_item_name=product_name_input,
            purchase_quantity=int_qty,
            purchase_cost=float_price,
            purchase_total_cost=total_cost,
            purchase_shipment_date=shipdate
        )
        new_purchase_order.save()

    return render(request, 'final_purchaseorder.html', {
        'purchaseorder': all_porders,
        'next_purchase_id': next_purchase_id,
        'next_product_id': next_product_id,
        'categories': all_categories,
        'user': user
    })


# EMPLOYEES
def employees(request):
    user = get_logged_in_user(request)

    all_employees = login_info.objects.all()

    latest_emp = login_info.objects.order_by('-empid').first()
    next_empid = latest_emp.empid + 1 if latest_emp else 1

    if request.method == "POST":
        finalname = request.POST.get("inputname")
        inputposition = request.POST.get("position")
        inputcontact = request.POST.get("contactnumber")
        inputsex = request.POST.get("sex")
        inputdob = request.POST.get("dob")
        inputdh = request.POST.get("dh")
        inputsa = request.POST.get("sa")
        inputaddress = request.POST.get("address")
        inputpass = request.POST.get("password")

        login_info_new = login_info(
            empid=next_empid,
            name=finalname,
            position=inputposition,
            contact=inputcontact,
            sex=inputsex,
            dob=inputdob,
            hired_date=inputdh,
            salary=inputsa,
            password=inputpass,
            address=inputaddress   
        )
        login_info_new.save()
        return redirect('employees')

    return render(request, 'final_employees.html', {
        'employeeinfo': all_employees,
        'new_id': next_empid,
        'user': user
    })


# MEMBERSHIP
def membership_page(request):
    user = get_logged_in_user(request)

    all_members = membership.objects.all()

    latest_member = membership.objects.order_by('-member_id').first()
    if latest_member:
        number = int(latest_member.member_id[1:])
        next_member_id = f"M{number + 1:03d}"
    else:
        next_member_id = "M001"

    if request.method == "POST":
        new_member = membership(
            member_id=next_member_id,
            name=request.POST.get("member_name"),
            points=0,
            date=request.POST.get("input_date"),
            address=request.POST.get("inputaddress"),
            contactnumber=request.POST.get("contactnumber")
        )
        new_member.save()

        return redirect('membership_page')

    return render(request, 'final_membership.html', {
        'membership': all_members,
        'next_member_id': next_member_id,
        'user': user
    })


# LOGIN
def loginpage(request):
    if request.method == "POST":
        name = request.POST.get("username")
        password = request.POST.get("password")

        try:
            user = login_info.objects.get(name=name)

            if user.password == password:
                request.session['name'] = user.name
                return redirect("dashboard")
            else:
                return render(request, "final_login.html", {"error": "Wrong password"})
        except login_info.DoesNotExist:
            return render(request, "final_login.html", {"error": "User not found"})

    return render(request, "final_login.html")


# DASHBOARD
def dashboard(request):
    user = get_logged_in_user(request)
    if not user:
        return redirect('loginpage')

    recent_sales = salesorder.objects.order_by('-receipt_id')[:5][::-1]
    recent_purchases = purchaseorder.objects.order_by('-purchase_id')[:5][::-1]

    sales_count = salesorder.objects.count()
    purchase_count = purchaseorder.objects.count()

    sales_sum = salesorder.objects.aggregate(total=Sum('sales_amount'))['total'] or 0
    purchase_sum = purchaseorder.objects.aggregate(total=Sum('purchase_total_cost'))['total'] or 0

    net_revenue = sales_sum

    return render(request, 'final_dashboard.html', {
        'user': user,
        'sales': recent_sales,
        'purchases': recent_purchases,
        'totalsales': sales_count,
        'totalpurchases': purchase_count,
        'netrevenue': net_revenue
    })


# ACCOUNTING PAGES
def receipts(request):
    return render(request, 'accounting_receipts.html', {
        'reciept_list': receipt.objects.all(),
        'user': get_logged_in_user(request)
    })

def salesjournal(request):
    sales_order = salesorder.objects.all()
    products = product.objects.all()
    employees = login_info.objects.all()

    return render(request, 'accounting_salesjournal.html', {
        'user': get_logged_in_user(request),
        'sales': sales_order,
        'product': products,
        'employee': employees})

def purchasejournal(request):
    all_purchases = purchaseorder.objects.all()
    products = product.objects.all()
    return render(request, 'accounting_purchasejournal.html', {
        'user': get_logged_in_user(request),
        'purchases': all_purchases,
        'product': products,
        })

def expensepage(request):
        # Get the latest expense to show next ID (optional, for display only)
    latest_expense = expenses.objects.order_by('-expense_id').first()
    next_expense = latest_expense.expense_id + 1 if latest_expense else 1

    if request.method == "POST":
        # Get form data
        date = request.POST.get("inputdate")
        category = request.POST.get("categoryinput")
        description = request.POST.get("descriptioninput")
        amount = request.POST.get("inputamount")

        # Convert amount to float safely
        try:
            amount = float(amount)
        except (TypeError, ValueError):
            amount = 0.0

        # Save new expense to database
        expenses.objects.create(
            expense_date=date,
            expense_description=description,
            expense_category=category,
            expense_amount=amount
        )

    # Get all expenses to display in template
    all_expenses = expenses.objects.all()

    return render(request, "accounting_expenses.html", {
        'user': get_logged_in_user(request),   # your existing user function
        'expense_id': next_expense,            # optional display
        'expenses': all_expenses               # pass expenses list to template
    })

def trialbalance(request):
    prod_list = product.objects.all()  # fetch all products
    for p in prod_list:
        total_value = sum(p.quantity * p.purchase_price for p in prod_list)

    sales_sum = salesorder.objects.aggregate(total=Sum('sales_amount'))['total'] or 0 
    purchase_sum = purchaseorder.objects.aggregate(total=Sum('purchase_total_cost'))['total'] or 0 
    expenses_sum = expenses.objects.aggregate(total=Sum('expense_amount'))['total']
    restock_sum = RestockOrder.objects.aggregate(total=Sum('total_cost'))['total']

    return render(request, "accounting_trialbalance.html", {
        'user': get_logged_in_user(request),
        'totalsales': float(sales_sum),
        'totalpurchases': float(purchase_sum),
        'totalexpenses': expenses_sum,
        'inventory': float(total_value),
        'restock': float(restock_sum)
    })

def pnlstatement(request):
    prod_list = product.objects.all()  # fetch all products
    for p in prod_list:
        total_value = sum(p.quantity * p.purchase_price for p in prod_list)

    sales_sum = salesorder.objects.aggregate(total=Sum('sales_amount'))['total'] or 0 
    purchase_sum = purchaseorder.objects.aggregate(total=Sum('purchase_total_cost'))['total'] or 0 
    expenses_sum = expenses.objects.aggregate(total=Sum('expense_amount'))['total']
    restock_sum = RestockOrder.objects.aggregate(total=Sum('total_cost'))['total']

    return render(request, 'accounting_pnlstatement.html', {
        'user': get_logged_in_user(request),
        'totalsales': float(sales_sum),
        'totalpurchases': float(purchase_sum),
        'totalexpenses': expenses_sum,
        'inventory': float(total_value),
        'restock': float(restock_sum)
    })

def homepage(request):
    return render(request, 'homepage.html', {'user': get_logged_in_user(request)})


# SALES ORDER (API)
def create_sales_order(request):
    try:
        body = json.loads(request.body)

        member_id = body.get("member_id") or None
        employee_id = int(body["employee_id"])
        discount = float(body.get("discount", 0))
        items = body.get("items", [])

        if not items:
            return JsonResponse({"error": "No items provided."}, status=400)

        with transaction.atomic():
            product_ids = [int(i["product_id"]) for i in items]
            products = product.objects.select_for_update().filter(product_id__in=product_ids)
            product_map = {p.product_id: p for p in products}

            for item in items:
                pid = int(item["product_id"])
                qty = int(item["quantity"])

                if product_map[pid].quantity < qty:
                    return JsonResponse({"error": "Insufficient stock"}, status=400)

            new_receipt = receipt.objects.create(
                member_id=member_id,
                employee_id=employee_id,
                discount=discount,
                date=timezone.now().date()
            )

            rows = []
            for item in items:
                pid = int(item["product_id"])
                qty = int(item["quantity"])
                price = float(item["price"])

                rows.append(salesorder(
                    receipt_id=new_receipt.receipt_id,
                    product_id=pid,
                    employee_id=employee_id,
                    sales_quantity=qty,
                    sales_price=price,
                    sales_amount=price * qty
                ))

                p = product_map[pid]
                p.quantity -= qty
                p.save()

            salesorder.objects.bulk_create(rows)

        return JsonResponse({"success": True})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# SALES ORDER PAGE
def sales_order(request):
    user = get_logged_in_user(request)

    products = product.objects.all()
    empinfo = login_info.objects.all()
    salesorders = salesorder.objects.all().order_by('-receipt_id')

    products_json = json.dumps([
        {
            "product_id": str(p.product_id),
            "product_name": p.product_name,
            "purchase_price": float(p.purchase_price),
            "quantity": p.quantity,
        }
        for p in products
    ])

    return render(request, "final_salesorder.html", {
        "salesorder": salesorders,
        "products": products,
        "products_json": products_json,
        "empinfo": empinfo,
        "user": user
    })

def restock_page(request):
    restockorders = RestockOrder.objects.select_related('product', 'employee').all().order_by('-id')
    products      = product.objects.all()
    empinfo       = login_info.objects.all()

    products_json = json.dumps([
        {
            'product_id':     p.product_id,
            'product_name':   p.product_name,
            'purchase_price': float(p.purchase_price),
            'quantity':       p.quantity,
        }
        for p in products
    ])

    last = RestockOrder.objects.order_by('-id').first()
    next_num = (last.id + 1) if last else 1
    next_restock_id = f'RST-{str(next_num).zfill(4)}'

    context = {
        'restockorders':   restockorders,
        'products':        products,
        'empinfo':         empinfo,
        'products_json':   products_json,
        'next_restock_id': next_restock_id,
        'user': get_logged_in_user(request)
    }
    return render(request, 'final_restock.html', context)


@require_POST
def restock_create(request):
    try:
        data = json.loads(request.body)

        employee_id  = data.get('employee_id')
        restock_date = data.get('date')
        items        = data.get('items', [])

        if not items:
            return JsonResponse({'success': False, 'error': 'No items provided.'}, status=400)

        created_ids = []

        with transaction.atomic():
            for item in items:
                product_id = item.get('product_id')
                quantity   = int(item.get('quantity', 0))
                unit_cost  = float(item.get('unit_cost', 0))

                if not product_id or quantity < 1 or unit_cost < 0:
                    return JsonResponse({'success': False, 'error': f'Invalid item data: {item}'}, status=400)

                try:
                    p = product.objects.get(product_id=product_id)
                except product.DoesNotExist:
                    return JsonResponse({'success': False, 'error': f'Product {product_id} not found.'}, status=404)

                employee = None
                if employee_id:
                    try:
                        employee = login_info.objects.get(empid=employee_id)
                    except login_info.DoesNotExist:
                        pass

                restock = RestockOrder(
                    product          = p,
                    employee         = employee,
                    restock_quantity = quantity,
                    unit_cost        = unit_cost,
                    restock_date     = restock_date,
                )
                restock.save()
                created_ids.append(restock.restock_id)

        return JsonResponse({
            'success':    True,
            'restock_id': created_ids[0] if len(created_ids) == 1 else created_ids,
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

def restock_journal(request):
    all_restock = RestockOrder.objects.all()
    products = product.objects.all()
    employees = login_info.objects.all()

    return render(request, 'accounting_restockjournal.html', {
        'user': get_logged_in_user(request),
        'restock': all_restock,
        'product':    products,
        'employee': employees,
    })

def sales_report(request):
    period = request.GET.get('period', None)
    now = timezone.now().date()

    if period:
        if period == 'daily':
            start = now
        elif period == 'weekly':
            start = now - timedelta(days=7)
        elif period == 'yearly':
            start = now.replace(month=1, day=1)
        else:
            start = now - timedelta(days=7)

        receipt_ids = receipt.objects.filter(date__gte=start).values_list('receipt_id', flat=True)
        orders      = salesorder.objects.filter(receipt_id__in=receipt_ids)

        items_sold   = orders.aggregate(total=Sum('sales_quantity'))['total'] or 0
        transactions = receipt_ids.count()
        avg_sales    = orders.aggregate(avg=Avg('sales_amount'))['avg'] or 0
        top_items    = (
            orders.values('product_id')
            .annotate(qty=Sum('sales_quantity'))
            .order_by('-qty')[:5]
        )

        # --- DAILY: show each receipt as a single point today ---
        if period == 'daily':
            receipt_list = receipt.objects.filter(date=now).values('receipt_id')
            date_totals = {}
            for r in receipt_list:
                rid = r['receipt_id']
                total = salesorder.objects.filter(receipt_id=rid).aggregate(
                    t=Sum('sales_amount')
                )['t'] or 0
                label = f'Receipt #{rid}'
                date_totals[label] = date_totals.get(label, 0) + float(total)

            chart_labels = list(date_totals.keys())
            chart_values = list(date_totals.values())

        # --- WEEKLY: show each day of the past 7 days ---
        elif period == 'weekly':
            date_totals = {}
            for i in range(6, -1, -1):  # 6 days ago → today
                day = now - timedelta(days=i)
                day_str = day.strftime('%a %d')  # e.g. "Mon 07"
                day_receipts = receipt.objects.filter(date=day).values_list('receipt_id', flat=True)
                total = salesorder.objects.filter(receipt_id__in=day_receipts).aggregate(
                    t=Sum('sales_amount')
                )['t'] or 0
                date_totals[day_str] = float(total)

            chart_labels = list(date_totals.keys())
            chart_values = list(date_totals.values())

        # --- YEARLY: show each month of the current year ---
        elif period == 'yearly':
            import calendar
            date_totals = {}
            for month in range(1, 13):  # Jan → Dec
                month_name = calendar.month_abbr[month]  # e.g. "Jan"
                month_receipts = receipt.objects.filter(
                    date__year=now.year,
                    date__month=month
                ).values_list('receipt_id', flat=True)
                total = salesorder.objects.filter(receipt_id__in=month_receipts).aggregate(
                    t=Sum('sales_amount')
                )['t'] or 0
                date_totals[month_name] = float(total)

            chart_labels = list(date_totals.keys())
            chart_values = list(date_totals.values())

        return JsonResponse({
            'items_sold'   : items_sold,
            'transactions' : transactions,
            'avg_sales'    : f'₱{avg_sales:.2f}',
            'top_items'    : list(top_items),
            'chart_labels' : chart_labels,
            'chart_values' : chart_values,
        })

    return render(request, 'final_sales_report.html', {
        'user': get_logged_in_user(request),
    })

def product_history(request, product_id):
    purchases = list(
        purchaseorder.objects.filter(product_id=product_id).values(
            'purchase_id', 'purchase_quantity', 'purchase_cost',
            'purchase_total_cost', 'purchase_shipment_date'
        )
    )
    sales_qs = salesorder.objects.filter(product_id=product_id).select_related()
    sales = []
    for s in sales_qs:
        try:
            r = receipt.objects.get(receipt_id=s.receipt_id)
            date = str(r.date)
        except receipt.DoesNotExist:
            date = '—'
        sales.append({
            'sales_id': s.sales_id,
            'sales_quantity': s.sales_quantity,
            'sales_price': str(s.sales_price),
            'sales_discount': str(s.sales_discount),
            'sales_amount': str(s.sales_amount),
            'date': date,
        })
    return JsonResponse({'purchases': purchases, 'sales': sales})