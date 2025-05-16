from django.urls import path
from . import views

app_name = 'admin_dashboard'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('users/', views.user_list, name='user_list'),
    path('users/<int:user_id>/', views.user_detail, name='user_detail'),
    path('users/<int:user_id>/edit/', views.user_edit, name='user_edit'),
    path('users/<int:user_id>/delete/', views.user_delete, name='user_delete'),
    path('users/bulk-action/', views.user_bulk_action, name='user_bulk_action'),
    path('products/', views.product_list, name='product_list'),
    path('products/quick-edit/', views.quick_edit_product, name='quick_edit_product'),
    path('orders/', views.order_list, name='order_list'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path('orders/<int:order_id>/update-status/', views.update_order_status, name='update_order_status'),
    path('orders/bulk-update-status/', views.bulk_update_order_status, name='bulk_update_order_status'),
    path('analytics/sales/', views.sales_analytics, name='sales_analytics'),
    path('analytics/inventory/', views.inventory_report, name='inventory_report'),
    path('analytics/customers/', views.customer_analytics, name='customer_analytics'),
    path('analytics/orders/', views.order_analytics, name='order_analytics'),
    path('book/<int:book_id>/edit-modal/', views.book_edit_modal, name='book_edit_modal'),
    path('book/<int:book_id>/delete-modal/', views.book_delete_modal, name='book_delete_modal'),
    path('book/<int:book_id>/price-modal/', views.book_price_modal, name='book_price_modal'),
]