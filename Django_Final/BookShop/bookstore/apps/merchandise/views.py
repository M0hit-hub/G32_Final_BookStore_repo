from django.shortcuts import render, get_object_or_404, redirect
from .models import Category, Product

def merchandise_home(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)
    
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    
    # Filter products for display
    new_products = products.filter(is_new=True)
    sale_products = products.filter(on_sale=True)
    
    context = {
        'category': category,
        'categories': categories,
        'products': products,
        'new_products': new_products,
        'sale_products': sale_products
    }
    
    return render(request, 'merchandise/merchandise.html', context)

def product_detail(request, id, slug):
    product = get_object_or_404(Product, id=id, slug=slug, available=True)
    
    context = {
        'product': product
    }
    
    return render(request, 'merchandise/product_detail.html', context)

def product_detail_fallback(request, id):
    product = get_object_or_404(Product, id=id, available=True)
    return redirect('merchandise:product_detail', id=product.id, slug=product.slug)
