from django.shortcuts import render, redirect, get_object_or_404
from .models import Item, Invoice, InvoiceItem
from .forms import ItemForm, InvoiceForm, AddItemForm
from django.http import JsonResponse
from django.db.models import Q
from django.utils import timezone
from django.db.models import Sum, Count, F, ExpressionWrapper, FloatField,DecimalField
from django.db.models.functions import TruncMonth, TruncYear
from .models import Sale, InventoryLoss
from datetime import timedelta,datetime
import calendar
import json
import random
from django.views.decorators.csrf import csrf_exempt


def home(request):
    # Total items count
    total_items = Item.objects.count()
    
    # Inventory value
    total_value = Item.objects.aggregate(
        total_value=Sum(F('price') * F('quantity'))
    )['total_value'] or 0
    
    # Low stock items (quantity < 10)
    low_stock_count = Item.objects.filter(quantity__lt=10).count()
    low_stock_items = Item.objects.filter(quantity__lt=10).order_by('quantity')[:5]
    
    # Today's invoices
    today = timezone.now().date()
    today_invoices = Invoice.objects.filter(date__date=today).count()
    
    # Today's sales
    today_sales = Invoice.objects.filter(date__date=today).aggregate(
        total_sales=Sum('total')
    )['total_sales'] or 0
    
    # New items this week
    one_week_ago = timezone.now() - timedelta(days=7)
    new_items_this_week = Item.objects.filter(created_at__gte=one_week_ago).count()
    
    # Value change percentage (placeholder)
    value_change_percent = 8.5
    
    # Stock distribution data (by category - placeholder)
    stock_distribution_labels = ['Office Supplies', 'Paper Products', 'Writing Instruments', 'Desk Accessories']
    stock_distribution_data = [35, 25, 30, 10]
    
    # Monthly sales data
    monthly_sales_labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
    monthly_sales_data = [125000, 142000, 138000, 158000, 175000, 142580]
    
    # Recent activities
    recent_activities = [
        {
            'type': 'Invoice',
            'title': f'Invoice #INV-{timezone.now().strftime("%Y%m%d")}-8A3F2D created',
            'description': f'₹12,450 • Customer: Rohan Enterprises',
            'timestamp': timezone.now() - timedelta(hours=2),
            'icon': 'receipt',
            'color': 'success'
        },
        {
            'type': 'Inventory',
            'title': 'Added new item: Premium Leather Journals',
            'description': f'Quantity: 50 • Price: ₹850',
            'timestamp': timezone.now() - timedelta(hours=5),
            'icon': 'box',
            'color': 'primary'
        },
        {
            'type': 'Restock',
            'title': 'Restocked: Gel Pens (Black)',
            'description': 'Added 200 units • New stock: 250',
            'timestamp': timezone.now() - timedelta(days=1, hours=4),
            'icon': 'arrow-repeat',
            'color': 'info'
        },
        {
            'type': 'Invoice',
            'title': f'Invoice #INV-{(timezone.now() - timedelta(days=1)).strftime("%Y%m%d")}-5B2C9A created',
            'description': f'₹8,720 • Customer: Sharma & Sons',
            'timestamp': timezone.now() - timedelta(days=1, hours=12),
            'icon': 'receipt',
            'color': 'success'
        },
        {
            'type': 'Low Stock',
            'title': 'Low stock alert: A4 Printing Paper',
            'description': 'Only 2 packs remaining',
            'timestamp': timezone.now() - timedelta(days=2),
            'icon': 'exclamation-triangle',
            'color': 'warning'
        }
    ]
    
    # Prepare data for JSON serialization
    context = {
        'total_items': total_items,
        'total_value': total_value,
        'low_stock_count': low_stock_count,
        'low_stock_items': low_stock_items,
        'today_invoices': today_invoices,
        'today_sales': today_sales,
        'new_items_this_week': new_items_this_week,
        'value_change_percent': value_change_percent,
        'stock_distribution_labels': json.dumps(stock_distribution_labels),
        'stock_distribution_data': json.dumps(stock_distribution_data),
        'monthly_sales_labels': json.dumps(monthly_sales_labels),
        'monthly_sales_data': json.dumps(monthly_sales_data),
        'recent_activities': recent_activities,
    }
    
    return render(request, 'home.html', context)
# Item CRUD Views
def item_list(request):
    items = Item.objects.all()
    total_value = sum(item.price * item.quantity for item in items)
    low_stock_count = items.filter(quantity__lt=10, quantity__gt=0).count()
    out_of_stock_count = items.filter(quantity=0).count()
    
    return render(request, 'khata/item_list.html', {
        'items': items,
        'total_value': total_value,
        'low_stock_count': low_stock_count,
        'out_of_stock_count': out_of_stock_count
    })

def add_item(request):
    if request.method == 'POST':
        form = ItemForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('item_list')
    else:
        form = ItemForm()
    return render(request, 'khata/item_form.html', {'form': form})

def edit_item(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    if request.method == 'POST':
        form = ItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect('item_list')
    else:
        form = ItemForm(instance=item)
    return render(request, 'khata/item_form.html', {'form': form})

def delete_item(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    if request.method == 'POST':
        item.delete()
        return redirect('item_list')
    return render(request, 'khata/delete_confirm.html', {'item': item})

# Similar views for update/delete items

# Invoice Views
#  

@csrf_exempt
def create_invoice(request):
    if request.method == 'POST':
        try:
            # Parse form data
            customer_name = request.POST.get('customer_name', 'Walk-in Customer')
            customer_phone = request.POST.get('customer_phone', '')
            customer_address = request.POST.get('customer_address', '')
            
            # Create invoice
            invoice = Invoice.objects.create(
                invoice_number=generate_invoice_number(),
                customer_name=customer_name,
                customer_phone=customer_phone,
                customer_address=customer_address,
                subtotal=float(request.POST.get('subtotal', 0)),
                tax_amount=float(request.POST.get('tax', 0)),
                discount_amount=float(request.POST.get('discount', 0)),
                total=float(request.POST.get('total', 0)),
                date=timezone.now()
            )
            
            # Add invoice items
            invoice_items = json.loads(request.POST.get('invoice_items', '[]'))
            for item_data in invoice_items:
                item = Item.objects.get(id=item_data['id'])
                InvoiceItem.objects.create(
                    invoice=invoice,
                    item=item,
                    quantity=item_data['quantity'],
                    unit_price=item_data['price']
                )
                
                # Update inventory
                item.quantity -= item_data['quantity']
                item.save()
            
            return JsonResponse({'success': True, 'invoice_id': invoice.id})
        
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    else:
        # GET request - show form
        today = timezone.now()
        invoice_number = f"INV-{today.strftime('%Y%m%d')}-{random.randint(1000, 9999)}"
        popular_items = Item.objects.filter(quantity__gt=0).order_by('-created_at')[:10]
        
        return render(request, 'khata/create_invoice.html', {
            'today': today,
            'invoice_number': invoice_number,
            'popular_items': popular_items
        })
    
def generate_invoice_number():
    date_str = timezone.now().strftime("%Y%m%d")
    random_str = ''.join(random.choices("ABCDEFGHJKLMNPQRSTUVWXYZ23456789", k=6))
    return f"INV-{date_str}-{random_str}"

def invoice_history(request):
    invoices = Invoice.objects.all().order_by('-date')
    return render(request, 'khata/invoice_history.html', {'invoices': invoices})

def invoice_detail(request, invoice_id):
    invoice = Invoice.objects.get(id=invoice_id)
    return render(request, 'khata/invoice_detail.html', {'invoice': invoice})


def add_invoice_items(request):
    invoice_id = request.session.get('current_invoice')
    if not invoice_id:
        return JsonResponse({
            'success': False, 
            'error': 'No active invoice found. Please create an invoice first.'
        })
    
    invoice = get_object_or_404(Invoice, id=invoice_id)
    
    if request.method == 'POST':
        try:
            # Get and validate input data
            item_id = request.POST.get('item_id')
            quantity = request.POST.get('quantity')
            
            if not item_id:
                return JsonResponse({
                    'success': False, 
                    'error': 'Item ID is required'
                })
            
            if not quantity:
                return JsonResponse({
                    'success': False, 
                    'error': 'Quantity is required'
                })
            
            try:
                item_id = int(item_id)
                quantity = int(quantity)
            except ValueError:
                return JsonResponse({
                    'success': False, 
                    'error': 'Invalid item ID or quantity'
                })
            
            if quantity <= 0:
                return JsonResponse({
                    'success': False, 
                    'error': 'Quantity must be greater than 0'
                })
            
            # Get the item
            try:
                item = Item.objects.get(id=item_id)
            except Item.DoesNotExist:
                return JsonResponse({
                    'success': False, 
                    'error': 'Item not found'
                })
            
            # Check stock availability
            if quantity > item.quantity:
                return JsonResponse({
                    'success': False, 
                    'error': f'Only {item.quantity} units available in stock'
                })
                
            # Create or update invoice item
            invoice_item, created = InvoiceItem.objects.get_or_create(
                invoice=invoice,
                item=item,
                defaults={'quantity': quantity, 'unit_price': item.price}
            )
            
            if not created:
                invoice_item.quantity += quantity
                invoice_item.save()
            
            # Update invoice totals
            invoice.subtotal = sum(
                i.quantity * i.unit_price 
                for i in invoice.items.all()
            )
            invoice.save()
            
            return JsonResponse({
                'success': True,
                'item_name': item.name,
                'quantity': invoice_item.quantity,
                'total_price': float(invoice_item.total_price),
                'new_subtotal': float(invoice.subtotal)
            })
            
        except Exception as e:
            print(f"Error in add_invoice_items: {str(e)}")  # For debugging
            return JsonResponse({
                'success': False, 
                'error': f'Server error: {str(e)}'
            })
    
    # GET request handling
    items = Item.objects.filter(quantity__gt=0)
    return render(request, 'khata/add_items.html', {
        'invoice': invoice,
        'items': items
    })

def finalize_invoice(request):
    invoice_id = request.session.get('current_invoice')
    invoice = get_object_or_404(Invoice, id=invoice_id)
    
    if request.method == 'POST':
        tax_type = request.POST.get('tax_type')
        tax_value = float(request.POST.get('tax_value', 0))
        discount_type = request.POST.get('discount_type')
        discount_value = float(request.POST.get('discount_value', 0))
        
        # Calculate tax
        if tax_type == 'percent':
            tax_amount = (invoice.subtotal * tax_value) / 100
        else:
            tax_amount = tax_value
        
        # Calculate discount
        if discount_type == 'percent':
            discount_amount = (invoice.subtotal * discount_value) / 100
        else:
            discount_amount = discount_value
        
        # Update invoice
        invoice.tax_amount = tax_amount
        invoice.discount_amount = discount_amount
        invoice.total = invoice.subtotal + tax_amount - discount_amount
        invoice.save()
        
        # Update inventory
        for item in invoice.items.all():
            item_obj = item.item
            item_obj.quantity -= item.quantity
            item_obj.save()
        
        del request.session['current_invoice']
        return redirect('invoice_detail', invoice_id=invoice.id)
    
    return render(request, 'khata/finalize_invoice.html', {'invoice': invoice})

def invoice_detail(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    return render(request, 'khata/invoice_detail.html', {'invoice': invoice})

def search_items(request):
    query = request.GET.get('q', '')
    items = Item.objects.filter(name__icontains=query, quantity__gt=0)[:10]
    results = [{
        'id': item.id,
        'name': item.name,
        'price': str(item.price),
        'quantity': item.quantity
    } for item in items]
    return JsonResponse({'items': results})

def item_search(request):
    query = request.GET.get('q', '')
    results = []
    
    if len(query) >= 3:  # Only search when at least 3 characters
        items = Item.objects.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query),
            quantity__gt=0
        )[:10]  # Limit to 10 results
        
        results = [
            {
                'id': item.id,
                'name': item.name,
                'price': str(item.price),
                'quantity': item.quantity
            } 
            for item in items
        ]
    
    return JsonResponse({'results': results})

def sales_report(request):
    # Get current month
    now = timezone.now()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # Calculate totals
    sales = Sale.objects.filter(sale_date__gte=month_start)
    revenue = sales.aggregate(total=Sum('total_price'))['total'] or 0
    
    # Calculate profit (revenue - cost of goods sold)
    profit_data = sales.annotate(
        cost=ExpressionWrapper(F('product__cost_price') * F('quantity'), output_field=DecimalField())
    ).aggregate(
        total_cost=Sum('cost'),
        total_revenue=Sum('total_price')
    )
    profit = (profit_data['total_revenue'] or 0) - (profit_data['total_cost'] or 0)
    
    # Calculate losses
    losses = InventoryLoss.objects.filter(loss_date__gte=month_start)
    total_loss = losses.aggregate(total=Sum('loss_value'))['total'] or 0
    
    # Daily sales data for chart
    daily_sales = sales.annotate(day=TruncMonth('sale_date')).values('day').annotate(
        daily_revenue=Sum('total_price')
    ).order_by('day')
    
    # Prepare chart data
    days_in_month = calendar.monthrange(now.year, now.month)[1]
    labels = [str(day) for day in range(1, days_in_month + 1)]
    revenue_data = [0] * days_in_month
    
    for sale in daily_sales:
        day_index = sale['day'].day - 1
        if day_index < len(revenue_data):
            revenue_data[day_index] = float(sale['daily_revenue'])
    
    # Loss breakdown by category
    loss_categories = losses.values('reason').annotate(
        total=Sum('loss_value')
    ).order_by('-total')
    
    # Prepare context
    context = {
        'current_month': now.strftime("%B %Y"),
        'revenue': revenue,
        'profit': profit,
        'total_loss': total_loss,
        'chart_labels': labels,
        'revenue_data': revenue_data,
        'loss_categories': [item['reason'] for item in loss_categories],
        'loss_values': [float(item['total']) for item in loss_categories],
    }
    
    return render(request, 'khata/sales_report.html', context)