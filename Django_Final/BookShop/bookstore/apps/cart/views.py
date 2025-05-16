from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from store.models import Book, Category
from merchandise.models import Product
from .cart import Cart
from django.contrib import messages
from django.http import JsonResponse

def cart_add(request, bookid):
	if not request.user.is_authenticated:
		if request.headers.get('x-requested-with') == 'XMLHttpRequest':
			return JsonResponse({'error': 'signin_required', 'message': 'Please sign in to add books to your cart.'}, status=401)
		messages.info(request, 'Please sign in to add books to your cart.')
		return redirect('store:signin')
	cart = Cart(request)
	book = get_object_or_404(Book, id=bookid)
	cart.add(item=book, item_type='book')
	if request.headers.get('x-requested-with') == 'XMLHttpRequest':
		return JsonResponse({'success': True, 'message': 'Added to cart'})
	return redirect('store:index')

def merchandise_add(request, product_id):
	if not request.user.is_authenticated:
		messages.info(request, 'Please sign in to add merchandise to your cart.')
		return redirect('store:signin')
	cart = Cart(request)
	product = get_object_or_404(Product, id=product_id)
	cart.add(item=product, item_type='merchandise')
	return redirect('merchandise:merchandise_home')

def cart_update(request, bookid, quantity):
	cart = Cart(request)
	book = get_object_or_404(Book, id=bookid)
	if request.method == 'POST':
		try:
			quantity = int(request.POST.get('quantity', quantity))
		except (TypeError, ValueError):
			quantity = 1
	cart.update(item=book, quantity=quantity, item_type='book')
	return redirect('cart:cart_details')

def merchandise_update(request, product_id, quantity):
	cart = Cart(request)
	product = get_object_or_404(Product, id=product_id)
	if request.method == 'POST':
		try:
			quantity = int(request.POST.get('quantity', quantity))
		except (TypeError, ValueError):
			quantity = 1
	cart.update(item=product, quantity=quantity, item_type='merchandise')
	return redirect('cart:cart_details')

def cart_remove(request, bookid):
    cart = Cart(request)
    book = get_object_or_404(Book, id=bookid)
    cart.remove(item=book, item_type='book')
    return redirect('cart:cart_details')

def merchandise_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(item=product, item_type='merchandise')
    return redirect('cart:cart_details')

def total_cart(request):
	return render(request, 'cart/totalcart.html')

def cart_summary(request):
	return render(request, 'cart/summary.html')

def cart_details(request):
	cart = Cart(request)
	context = {
		"cart": cart,
	}
	return render(request, 'cart/cart.html', context)

