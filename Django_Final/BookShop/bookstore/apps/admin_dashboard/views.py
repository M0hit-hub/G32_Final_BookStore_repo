from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.contrib import messages
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.db.models import Sum, Count, F, ExpressionWrapper, DecimalField, Q
from django.db.models.functions import TruncMonth
from store.models import Book, Category, Writer
from merchandise.models import Product, Category as MerchCategory
from order.models import Order, OrderItem, Shipment
from django.utils import timezone
from datetime import timedelta
import json
from django.template.loader import render_to_string

def is_admin(user):
    return user.is_staff or user.is_superuser

@login_required
@user_passes_test(is_admin)
def dashboard(request):
    # Get counts for statistics
    total_users = User.objects.count()
    
    # Get actual counts from models
    total_books = Book.objects.count()
    total_orders = Order.objects.count()
    total_products = Product.objects.count()
    
    # Recent users - last 5 registered
    recent_users = User.objects.order_by('-date_joined')[:5]
    
    # Recent orders - last 5 placed
    recent_orders = Order.objects.order_by('-created')[:5]
    
    # Set active page for sidebar highlighting
    active_page = 'dashboard'
    
    context = {
        'total_users': total_users,
        'total_books': total_books,
        'total_orders': total_orders,
        'total_products': total_products,
        'recent_users': recent_users,
        'recent_orders': recent_orders,
        'active_page': active_page,
    }
    
    return render(request, 'admin_dashboard/dashboard.html', context)

@login_required
@user_passes_test(is_admin)
def user_list(request):
    """View to list all users with pagination"""
    users = User.objects.all().order_by('-date_joined')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        users = users.filter(username__icontains=search_query) | users.filter(email__icontains=search_query)
    
    # Pagination
    paginator = Paginator(users, 10)  # Show 10 users per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Set active page for sidebar highlighting
    active_page = 'users'
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'active_page': active_page,
    }
    
    return render(request, 'admin_dashboard/user_list.html', context)

@login_required
@user_passes_test(is_admin)
def user_detail(request, user_id):
    """View to show detailed information about a specific user"""
    user = get_object_or_404(User, id=user_id)
    
    # Get books added by this user (assuming books have a user/author field)
    # If your Book model doesn't have a user field, you'll need to adjust this
    user_books = Book.objects.filter(writer__name=user.username) if hasattr(Book, 'writer') else []
    
    # Get products added by this user (if applicable)
    # If your Product model doesn't have a user field, you'll need to adjust this
    user_products = Product.objects.filter(category__name=user.username) if hasattr(Product, 'category') else []
    
    # Get orders placed by this user
    user_orders = Order.objects.filter(customer=user).order_by('-created')
    
    # Set active page for sidebar highlighting
    active_page = 'users'
    
    context = {
        'user_detail': user,
        'user_books': user_books,
        'user_products': user_products,
        'user_orders': user_orders,
        'active_page': active_page,
    }
    
    return render(request, 'admin_dashboard/user_detail.html', context)

@login_required
@user_passes_test(is_admin)
def user_edit(request, user_id):
    """View to edit a user"""
    user = get_object_or_404(User, id=user_id)
    
    # Don't allow editing superuser accounts if you're not a superuser
    if user.is_superuser and not request.user.is_superuser:
        messages.error(request, "You don't have permission to edit a superuser account.")
        return redirect('admin_dashboard:user_detail', user_id=user.id)
    
    if request.method == 'POST':
        # Process the form data
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        is_active = request.POST.get('is_active') == 'on'
        is_staff = request.POST.get('is_staff') == 'on'
        
        # Update user data
        user.username = username
        user.email = email
        user.first_name = first_name
        user.last_name = last_name
        user.is_active = is_active
        
        # Only superusers can change staff status
        if request.user.is_superuser:
            user.is_staff = is_staff
        
        # Update password if provided
        password = request.POST.get('password')
        if password and password.strip():
            user.set_password(password)
        
        user.save()
        messages.success(request, f"User '{user.username}' updated successfully.")
        return redirect('admin_dashboard:user_detail', user_id=user.id)
    
    # Set active page for sidebar highlighting
    active_page = 'users'
    
    context = {
        'user_obj': user,  # Use user_obj to avoid conflict with request.user
        'active_page': active_page,
    }
    
    return render(request, 'admin_dashboard/user_edit.html', context)

@login_required
@user_passes_test(is_admin)
def user_delete(request, user_id):
    """View to delete a user"""
    user = get_object_or_404(User, id=user_id)
    
    # Don't allow deleting superuser accounts if not a superuser
    if user.is_superuser and not request.user.is_superuser:
        messages.error(request, "You don't have permission to delete a superuser account.")
        return redirect('admin_dashboard:user_list')
    
    # Don't allow self-deletion
    if user == request.user:
        messages.error(request, "You cannot delete your own account.")
        return redirect('admin_dashboard:user_list')
    
    if request.method == 'POST':
        username = user.username
        user.delete()
        messages.success(request, f"User '{username}' has been deleted.")
        return redirect('admin_dashboard:user_list')
    
    # Set active page for sidebar highlighting
    active_page = 'users'
    
    context = {
        'user_obj': user,  # Use user_obj to avoid conflict with request.user
        'active_page': active_page,
    }
    
    return render(request, 'admin_dashboard/user_delete.html', context)

@login_required
@user_passes_test(is_admin)
def user_bulk_action(request):
    """Process bulk actions on users"""
    if request.method == 'POST':
        action = request.POST.get('bulk_action')
        selected_ids = request.POST.getlist('selected_users')
        
        if not selected_ids:
            messages.error(request, "No users selected.")
            return redirect('admin_dashboard:user_list')
        
        users = User.objects.filter(id__in=selected_ids)
        
        # Filter out superusers if current user is not a superuser
        if not request.user.is_superuser:
            users = users.exclude(is_superuser=True)
        
        # Remove self from the list to prevent self-actions
        users = users.exclude(id=request.user.id)
        
        count = users.count()
        
        if action == 'activate':
            users.update(is_active=True)
            messages.success(request, f"{count} users activated successfully.")
        elif action == 'deactivate':
            users.update(is_active=False)
            messages.success(request, f"{count} users deactivated successfully.")
        elif action == 'delete':
            deleted = 0
            for user in users:
                user.delete()
                deleted += 1
            messages.success(request, f"{deleted} users deleted successfully.")
        else:
            messages.error(request, "Invalid action.")
    
    return redirect('admin_dashboard:user_list')

@login_required
@user_passes_test(is_admin)
def product_list(request):
    """View to list all products with pagination"""
    # Get both books and merchandise products
    books = Book.objects.all().order_by('-created')
    products = Product.objects.all().order_by('-created')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        books = books.filter(name__icontains=search_query)
        products = products.filter(name__icontains=search_query)
    
    # Filter by type
    product_type = request.GET.get('type', 'all')
    if product_type == 'book':
        products = []
    elif product_type == 'merchandise':
        books = []
    
    # Pagination for books
    book_paginator = Paginator(books, 10)
    book_page = request.GET.get('book_page')
    book_page_obj = book_paginator.get_page(book_page)
    
    # Pagination for products
    product_paginator = Paginator(products, 10)
    product_page = request.GET.get('product_page')
    product_page_obj = product_paginator.get_page(product_page)
    
    # Stats for cards
    total_books = Book.objects.count()
    total_merchandise = Product.objects.count()
    low_stock_count = Book.objects.filter(stock__lt=5).count() + Product.objects.filter(stock__lt=5).count()
    out_of_stock_count = Book.objects.filter(stock=0).count() + Product.objects.filter(stock=0).count()
    
    # Set active page for sidebar highlighting
    active_page = 'products'
    
    context = {
        'book_page_obj': book_page_obj,
        'product_page_obj': product_page_obj,
        'search_query': search_query,
        'product_type': product_type,
        'active_page': active_page,
        'total_books': total_books,
        'total_merchandise': total_merchandise,
        'low_stock_count': low_stock_count,
        'out_of_stock_count': out_of_stock_count,
    }
    
    return render(request, 'admin_dashboard/product_list.html', context)

@login_required
@user_passes_test(is_admin)
def order_list(request):
    """View to list all orders with pagination"""
    orders = Order.objects.all().order_by('-created')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        orders = orders.filter(transaction_id__icontains=search_query) | orders.filter(customer__username__icontains=search_query)
    
    # Pagination
    paginator = Paginator(orders, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Stats for cards
    total_orders = orders.count()
    paid_orders = orders.filter(paid=True).count()
    pending_orders = orders.filter(paid=False).count()
    total_revenue = orders.filter(paid=True).aggregate(total=Sum('payable'))['total'] or 0
    
    # Set active page for sidebar highlighting
    active_page = 'orders'
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'active_page': active_page,
        'total_orders': total_orders,
        'paid_orders': paid_orders,
        'pending_orders': pending_orders,
        'total_revenue': total_revenue,
    }
    
    return render(request, 'admin_dashboard/order_list.html', context)

@login_required
@user_passes_test(is_admin)
def order_detail(request, order_id):
    """View to show detailed information about a specific order"""
    order = get_object_or_404(Order, id=order_id)
    order_items = OrderItem.objects.filter(order=order)
    
    # Get or create shipment information
    shipment, created = Shipment.objects.get_or_create(order=order)
    
    # Determine the status index for progress visualization
    from order.models import ORDER_STATUS
    status_list = [s[0] for s in ORDER_STATUS]
    shipment_status_index = status_list.index(shipment.status)
    
    # Set active page for sidebar highlighting
    active_page = 'orders'
    
    context = {
        'order': order,
        'order_items': order_items,
        'shipment': shipment,
        'shipment_status_index': shipment_status_index,
        'active_page': active_page,
        'ORDER_STATUS': ORDER_STATUS,
    }
    
    return render(request, 'admin_dashboard/order_detail.html', context)

@login_required
@user_passes_test(is_admin)
def update_order_status(request, order_id):
    """Update order status and shipment information"""
    order = get_object_or_404(Order, id=order_id)
    shipment, created = Shipment.objects.get_or_create(order=order)
    
    if request.method == 'POST':
        status = request.POST.get('status')
        tracking_number = request.POST.get('tracking_number', shipment.tracking_number)
        carrier = request.POST.get('carrier', shipment.carrier)
        paid = request.POST.get('paid') == 'on'
        
        shipment.status = status
        shipment.tracking_number = tracking_number
        shipment.carrier = carrier
        shipment.save()
        
        # Update order payment status
        order.paid = paid
        order.save()
        
        messages.success(request, f"Order #{order.id} status updated successfully.")
        return redirect('admin_dashboard:order_detail', order_id=order.id)
    
    # If it's a GET request, provide the status options for rendering a form
    from order.models import ORDER_STATUS
    context = {
        'order': order,
        'shipment': shipment,
        'status_options': ORDER_STATUS,
        'active_page': 'orders',
    }
    return render(request, 'admin_dashboard/update_order_status.html', context)

@login_required
@user_passes_test(is_admin)
def sales_analytics(request):
    """View to display sales analytics"""
    # Get date range filter
    period = request.GET.get('period', '30days')
    
    if period == '7days':
        start_date = timezone.now() - timedelta(days=7)
        title = 'Last 7 Days Sales'
    elif period == '30days':
        start_date = timezone.now() - timedelta(days=30)
        title = 'Last 30 Days Sales'
    elif period == 'year':
        start_date = timezone.now() - timedelta(days=365)
        title = 'Last Year Sales'
    else:  # all time
        start_date = timezone.datetime(1970, 1, 1, tzinfo=timezone.utc)
        title = 'All Time Sales'
    
    # Get orders in the date range
    orders = Order.objects.filter(created__gte=start_date)
    
    # Calculate total revenue
    total_revenue = orders.aggregate(Sum('payable'))['payable__sum'] or 0
    
    # Calculate sales by month
    monthly_sales = (
        orders
        .annotate(month=TruncMonth('created'))
        .values('month')
        .annotate(total=Sum('payable'))
        .order_by('month')
    )
    
    # Calculate product category distribution
    order_items = OrderItem.objects.filter(order__in=orders)
    book_items = order_items.filter(item_type='book')
    merchandise_items = order_items.filter(item_type='merchandise')
    
    book_revenue = book_items.aggregate(total=Sum(F('price') * F('quantity')))['total'] or 0
    merchandise_revenue = merchandise_items.aggregate(total=Sum(F('price') * F('quantity')))['total'] or 0
    
    # Prepare data for charts
    months = [entry['month'].strftime('%b %Y') for entry in monthly_sales]
    sales_values = [float(entry['total']) for entry in monthly_sales]
    
    # Calculate top selling products
    top_books = (
        book_items
        .values('book__name')
        .annotate(total=Sum(F('price') * F('quantity')))
        .order_by('-total')[:5]
    )
    
    top_merchandise = (
        merchandise_items
        .values('merchandise__name')
        .annotate(total=Sum(F('price') * F('quantity')))
        .order_by('-total')[:5]
    )
    
    # Calculate paid vs pending orders
    paid_orders = orders.filter(paid=True).count()
    pending_orders = orders.filter(paid=False).count()
    
    context = {
        'active_page': 'sales_analytics',
        'title': title,
        'period': period,
        'total_revenue': total_revenue,
        'total_orders': orders.count(),
        'months': json.dumps(months),
        'sales_values': json.dumps(sales_values),
        'book_revenue': book_revenue,
        'merchandise_revenue': merchandise_revenue,
        'top_books': top_books,
        'top_merchandise': top_merchandise,
        'paid_orders': paid_orders,
        'pending_orders': pending_orders,
    }
    
    return render(request, 'admin_dashboard/sales_analytics.html', context)

@login_required
@user_passes_test(is_admin)
def inventory_report(request):
    """View to display inventory reports"""
    # Get low stock books (less than 5 items)
    low_stock_books = Book.objects.filter(stock__lt=5).order_by('stock')
    
    # Get low stock merchandise (less than 5 items)
    low_stock_merchandise = Product.objects.filter(stock__lt=5).order_by('stock')
    
    # Get out of stock items
    out_of_stock_books = Book.objects.filter(stock=0)
    out_of_stock_merchandise = Product.objects.filter(stock=0)
    
    # Get book categories with count
    book_categories = (
        Category.objects.filter(book__isnull=False)
        .distinct()
        .annotate(book_count=Count('book'))
        .order_by('-book_count')
    )
    
    # Get merchandise categories with count
    merch_categories = (
        MerchCategory.objects.filter(products__isnull=False)
        .distinct()
        .annotate(merch_count=Count('products'))
        .order_by('-merch_count')
    )
    
    # Get top writers by book count
    top_writers = (
        Writer.objects.annotate(book_count=Count('book'))
        .order_by('-book_count')[:10]
    )
    
    context = {
        'active_page': 'inventory_report',
        'low_stock_books': low_stock_books,
        'low_stock_merchandise': low_stock_merchandise,
        'out_of_stock_books': out_of_stock_books,
        'out_of_stock_merchandise': out_of_stock_merchandise,
        'book_categories': book_categories,
        'merch_categories': merch_categories,
        'top_writers': top_writers,
    }
    
    return render(request, 'admin_dashboard/inventory_report.html', context)

@login_required
@user_passes_test(is_admin)
def customer_analytics(request):
    """View to display customer analytics"""
    # Get top customers by order count
    top_customers_by_orders = (
        User.objects.annotate(order_count=Count('order'))
        .filter(order_count__gt=0)
        .order_by('-order_count')[:10]
    )
    
    # Get top customers by revenue
    top_customers_by_revenue = (
        User.objects.annotate(total_spent=Sum('order__payable'))
        .filter(total_spent__isnull=False)
        .order_by('-total_spent')[:10]
    )
    
    # Get recent signups (last 30 days)
    recent_signups = User.objects.filter(
        date_joined__gte=timezone.now() - timedelta(days=30)
    ).order_by('-date_joined')
    
    # Calculate user growth
    months = []
    user_counts = []
    for i in range(11, -1, -1):  # 12 months
        month_start = timezone.now() - timedelta(days=30 * (i + 1))
        month_end = timezone.now() - timedelta(days=30 * i)
        month_name = month_end.strftime('%b %Y')
        count = User.objects.filter(
            date_joined__gte=month_start,
            date_joined__lt=month_end
        ).count()
        if count == 0:
            count = 5 + (i % 4) * 3  # Just for demo
        months.append(month_name)
        user_counts.append(count)

    # Mock stats for demo
    total_customers = 120
    new_customers = 15
    new_customer_growth = 8.5
    average_order_value = 75.20
    aov_growth = 2.3
    customer_retention_rate = 62.5
    retention_growth = 1.2
    customer_lifetime_value = 320.50
    clv_growth = 3.1
    customer_acquisition_cost = 25.75
    cac_growth = -1.8
    purchase_frequency = 2.7
    frequency_growth = 0.9

    # Mock data for charts
    time_labels = months
    new_customers_data = [int(10 + (i % 5) * 2) for i in range(12)]
    total_customers_data = [sum(new_customers_data[:i+1]) for i in range(12)]
    segment_labels = ["New", "Occasional", "Regular", "Loyal"]
    segment_data = [30, 40, 35, 15]
    frequency_labels = ["1", "2-3", "4-6", "7+"]
    frequency_data = [50, 40, 20, 10]
    geo_labels = ["USA", "UK", "India", "Canada", "Australia"]
    geo_data = [40, 25, 20, 15, 10]
    cohort_data = [
        {"month": "Jan 2024", "size": 20, "retention": [100, 60, 40, 30, 20, 10]},
        {"month": "Feb 2024", "size": 18, "retention": [100, 55, 35, 25, 15, 8]},
        {"month": "Mar 2024", "size": 22, "retention": [100, 65, 45, 35, 25, 12]},
    ]
    top_customers = [
        {"initials": "JD", "full_name": "John Doe", "email": "john@example.com", "orders_count": 12, "total_spent": 950.50, "avg_order": 79.21, "last_purchase": timezone.now(), "join_date": timezone.now() - timedelta(days=400), "loyalty_color": "success", "loyalty_level": "Gold"},
        {"initials": "JS", "full_name": "Jane Smith", "email": "jane@example.com", "orders_count": 10, "total_spent": 820.00, "avg_order": 82.00, "last_purchase": timezone.now(), "join_date": timezone.now() - timedelta(days=300), "loyalty_color": "info", "loyalty_level": "Silver"},
    ]

    context = {
        'active_page': 'customer_analytics',
        'top_customers_by_orders': top_customers_by_orders,
        'top_customers_by_revenue': top_customers_by_revenue,
        'recent_signups': recent_signups,
        'months': json.dumps(months),
        'user_counts': json.dumps(user_counts),
        'total_customers': total_customers,
        'new_customers': new_customers,
        'new_customer_growth': new_customer_growth,
        'average_order_value': average_order_value,
        'aov_growth': aov_growth,
        'customer_retention_rate': customer_retention_rate,
        'retention_growth': retention_growth,
        'customer_lifetime_value': customer_lifetime_value,
        'clv_growth': clv_growth,
        'customer_acquisition_cost': customer_acquisition_cost,
        'cac_growth': cac_growth,
        'purchase_frequency': purchase_frequency,
        'frequency_growth': frequency_growth,
        'time_labels': json.dumps(time_labels),
        'new_customers_data': json.dumps(new_customers_data),
        'total_customers_data': json.dumps(total_customers_data),
        'segment_labels': json.dumps(segment_labels),
        'segment_data': json.dumps(segment_data),
        'frequency_labels': json.dumps(frequency_labels),
        'frequency_data': json.dumps(frequency_data),
        'geo_labels': json.dumps(geo_labels),
        'geo_data': json.dumps(geo_data),
        'cohort_data': cohort_data,
        'top_customers': top_customers,
    }
    
    return render(request, 'admin_dashboard/customer_analytics.html', context)

@login_required
@user_passes_test(is_admin)
def quick_edit_product(request):
    """Handle quick edit requests for products from the product management page"""
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        product_type = request.POST.get('product_type')
        name = request.POST.get('name')
        price = request.POST.get('price')
        stock = request.POST.get('stock')
        status = request.POST.get('status') == '1'  # Convert to boolean
        
        try:
            if product_type == 'book':
                # Update book
                from store.models import Book
                book = get_object_or_404(Book, id=product_id)
                
                # Update fields
                book.name = name
                book.price = price
                book.stock = stock
                book.status = status
                book.save()
                
                messages.success(request, f"Book '{name}' updated successfully")
            
            elif product_type == 'merchandise':
                # Update merchandise product
                from merchandise.models import Product
                product = get_object_or_404(Product, id=product_id)
                
                # Update fields
                product.name = name
                product.price = price
                product.stock = stock
                product.available = status
                product.save()
                
                messages.success(request, f"Product '{name}' updated successfully")
                
            else:
                messages.error(request, "Invalid product type")
                
        except Exception as e:
            messages.error(request, f"Error updating product: {str(e)}")
        
        # Redirect back to products page
        return redirect('admin_dashboard:product_list')
        
    # If not POST request, redirect to products page
    return redirect('admin_dashboard:product_list')

@login_required
@user_passes_test(is_admin)
def order_analytics(request):
    """
    View for the order analytics dashboard.
    """
    # In a real application, you would calculate these values from the database
    context = {
        'total_orders': 567,
        'order_growth': 12.5,
        'avg_order_value': 85.42,
        'aov_growth': 3.2,
        'conversion_rate': 2.8,
        'conversion_change': 0.5,
        'repeat_customers': 35,
        'repeat_growth': 4.7,
        'top_customers': [
            {'name': 'John Doe', 'orders': 12, 'total_spent': 984.50, 'last_order': '2023-06-15'},
            {'name': 'Jane Smith', 'orders': 8, 'total_spent': 754.20, 'last_order': '2023-06-10'},
            {'name': 'Robert Johnson', 'orders': 7, 'total_spent': 625.75, 'last_order': '2023-06-08'},
            {'name': 'Emily Brown', 'orders': 6, 'total_spent': 512.30, 'last_order': '2023-06-05'},
            {'name': 'Michael Wilson', 'orders': 5, 'total_spent': 435.60, 'last_order': '2023-06-02'},
        ]
    }
    return render(request, 'admin_dashboard/order_analytics.html', context)

@login_required
@user_passes_test(is_admin)
def bulk_update_order_status(request):
    """Handle bulk actions for orders"""
    if request.method == 'POST':
        action = request.POST.get('action')
        order_ids = request.POST.getlist('order_ids')
        
        if not order_ids:
            messages.error(request, "No orders selected.")
            return redirect('admin_dashboard:order_list')
        
        orders = Order.objects.filter(id__in=order_ids)
        count = orders.count()
        
        if action == 'mark_paid':
            orders.update(paid=True)
            # Also update shipment status if needed
            for order in orders:
                shipment, created = Shipment.objects.get_or_create(order=order)
                if shipment.status == 'order placed':
                    shipment.status = 'processing'
                    shipment.save()
            messages.success(request, f"{count} orders marked as paid.")
        elif action == 'mark_pending':
            orders.update(paid=False)
            messages.success(request, f"{count} orders marked as pending.")
        else:
            messages.error(request, "Invalid action.")
        
    return redirect('admin_dashboard:order_list')

@login_required
@user_passes_test(is_admin)
def book_edit_modal(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    if request.method == 'POST':
        book.name = request.POST.get('name')
        book.price = request.POST.get('price')
        book.save()
        return JsonResponse({'success': True})
    html = render_to_string('admin_dashboard/modals/book_edit_modal.html', {'book': book}, request=request)
    return JsonResponse({'success': False, 'html': html})

@login_required
@user_passes_test(is_admin)
def book_delete_modal(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    if request.method == 'POST':
        book.delete()
        return JsonResponse({'success': True})
    html = render_to_string('admin_dashboard/modals/book_delete_modal.html', {'book': book}, request=request)
    return JsonResponse({'success': False, 'html': html})

@login_required
@user_passes_test(is_admin)
def book_price_modal(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    if request.method == 'POST':
        book.price = request.POST.get('price')
        book.save()
        return JsonResponse({'success': True})
    html = render_to_string('admin_dashboard/modals/book_price_modal.html', {'book': book}, request=request)
    return JsonResponse({'success': False, 'html': html})


