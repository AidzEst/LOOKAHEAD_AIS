from django.db import models
from datetime import date

# Create your models here.

class category(models.Model):
    category_id = models.AutoField(primary_key=True)
    category_name = models.CharField()

    def __str__(self):
        return self.category_name
    
class product(models.Model):
    product_id = models.AutoField(primary_key=True)
    product_name = models.CharField(max_length=255)
    quantity = models.IntegerField()
    category = models.ForeignKey(category, on_delete=models.CASCADE)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    shipment_date = models.DateField()

    def __str__(self):
        return self.product_name

class login_info(models.Model):
    empid = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    contact = models.CharField(max_length=15, default='N/A')
    sex = models.CharField(max_length=10, default='Unknown')
    dob = models.DateField(default=date(2000, 1, 1))  # Default Date of Birth
    hired_date = models.DateField(default=date.today)  # Default to today
    salary = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    address = models.CharField(max_length=255, blank=True)
    password = models.CharField(max_length=128, default='changeme')

    def __str__(self):
        return self.name

    def __str__(self):
        return self.empname

class purchaseorder(models.Model):
    purchase_id = models.IntegerField(primary_key=True)
    product_id = models.IntegerField()
    purchase_item_name = models.CharField()
    purchase_quantity = models.IntegerField()
    purchase_cost = models.DecimalField(max_digits=10, decimal_places=2)
    purchase_total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    purchase_shipment_date = models.DateField(null=True, blank=True)
    is_archived   = models.BooleanField(default=False)
    return_reason = models.TextField(null=True, blank=True)

class salesorder(models.Model):
    sales_id = models.AutoField(primary_key=True) 
    receipt_id = models.IntegerField()
    product_id = models.IntegerField()
    employee_id = models.IntegerField()
    sales_quantity = models.IntegerField()
    sales_price = models.DecimalField(max_digits=10, decimal_places=2)
    sales_discount = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    sales_amount = models.DecimalField(max_digits=12, decimal_places=2)
    is_archived   = models.BooleanField(default=False)
    return_reason = models.TextField(null=True, blank=True)

class receipt(models.Model):
    receipt_id  = models.AutoField(primary_key=True)
    member_id   = models.CharField(max_length=50, null=True, blank=True)
    employee_id = models.IntegerField()
    discount    = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    date        = models.DateField()

    def __str__(self):
        return f"Receipt #{self.receipt_id}"

class membership(models.Model):
    member_id   = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=100)
    points = models.IntegerField(null=True, blank=True)
    contactnumber = models.CharField(max_length=11, null=True, blank=True)
    address = models.CharField(max_length=255)
    date = models.DateField(null=True, blank=True)

class expenses(models.Model):
    expense_id = models.AutoField(primary_key=True)
    expense_date = models.DateField()
    expense_description = models.CharField(max_length=255)
    expense_amount = models.IntegerField()
    expense_category = models.CharField(max_length=255)

class RestockOrder(models.Model):
    restock_id       = models.CharField(max_length=20, unique=True, editable=False)
    product          = models.ForeignKey('product', on_delete=models.CASCADE, db_column='product_id')
    employee         = models.ForeignKey('login_info', on_delete=models.SET_NULL, null=True, db_column='empid', to_field='empid')
    restock_quantity = models.PositiveIntegerField()
    unit_cost        = models.DecimalField(max_digits=10, decimal_places=2)
    total_cost       = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    restock_date     = models.DateField()
    
    def save(self, *args, **kwargs):
        self.total_cost = self.unit_cost * self.restock_quantity
        if not self.restock_id:
            last = RestockOrder.objects.order_by('-id').first()
            next_num = (last.id + 1) if last else 1
            self.restock_id = f'RST-{str(next_num).zfill(4)}'
        super().save(*args, **kwargs)

    def __str__(self):
        return self.restock_id
