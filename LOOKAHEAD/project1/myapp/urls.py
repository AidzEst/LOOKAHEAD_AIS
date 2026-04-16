from django.urls import path
from . import views

urlpatterns = [
    path('', views.homepage, name = "homepage"),
    path('homepage/', views.homepage, name = "homepage"),
    path('login/', views.loginpage, name = "loginpage"),
    path('inventory/', views.inventory, name='inventory'),
    path('inventory/history/<int:product_id>/', views.product_history, name='product_history'),
    path('categories/', views.categories, name = 'categories'),
    path('salesorder/',         views.sales_order,         name='salesorder'),
    path('salesorder/create/',  views.create_sales_order,  name='create_sales_order'),
    path('purchaseorder/', views.purchase_order, name = 'purchaseorder'),
    path('employees/', views.employees, name = 'employees'),
    path('dashboard/', views.dashboard, name = 'dashboard'),
    path('membership/', views.membership_page, name = 'membership'),
    path('restock/', views.restock_page, name = 'restock'),
    path('restock/create/', views.restock_create, name='restock_create'),
    path('sales_report/', views.sales_report, name = 'sales_report'),

    #---ACCOUNTING---
    path("receipts/", views.receipts, name = 'receipts'),
    path("salesjournal/", views.salesjournal, name = 'salesjournal'),
    path("purchasejournal/", views.purchasejournal, name = 'purchasejournal'),
    path("expenses/", views.expensepage, name = 'expenses' ),
    path("trialbalance/", views.trialbalance, name = 'trialbalance'),
    path("pnlstatement/", views.pnlstatement, name = 'pnlstatement'),
    path("restockjournal/", views.restock_journal, name = 'restockjournal'),
]