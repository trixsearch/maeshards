from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    # Item Management
    path('items/', views.item_list, name='item_list'),
    path('items/add/', views.add_item, name='add_item'),
    path('items/edit/<int:item_id>/', views.edit_item, name='edit_item'),
    path('items/delete/<int:item_id>/', views.delete_item, name='delete_item'),
    
    # Invoice Management
    path('invoice/create/', views.create_invoice, name='create_invoice'),
    path('invoice/add-items/', views.add_invoice_items, name='add_invoice_items'),
    path('invoice/finalize/', views.finalize_invoice, name='finalize_invoice'),
    path('invoice/<int:invoice_id>/', views.invoice_detail, name='invoice_detail'),
    path('invoice/history/', views.invoice_history, name='invoice_history'),
    path('sales-report/', views.sales_report, name='sales_report'),
    
    # AJAX Endpoints
    path('search-items/', views.search_items, name='search_items'),
     path('item-search/', views.item_search, name='item_search'),
]