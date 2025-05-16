from django.urls import path
from . import views

app_name = 'merchandise'

urlpatterns = [
    path('', views.merchandise_home, name='merchandise_home'),
    path('category/<slug:category_slug>/', views.merchandise_home, name='merchandise_by_category'),
    path('product/<int:id>/<slug:slug>/', views.product_detail, name='product_detail'),
    path('product/<int:id>/', views.product_detail_fallback, name='product_detail_fallback'),
] 