from django.shortcuts import HttpResponse, render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.views import View
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from cart.cart import Cart
from .models import Order, OrderItem, Shipment
from .forms import OrderCreateForm
from .pdfcreator import renderPdf

# ------------------------- Order Create -----------------------------
def order_create(request):
    cart = Cart(request)
    if request.user.is_authenticated:
        customer = get_object_or_404(User, id=request.user.id)
        form = OrderCreateForm(request.POST or None, initial={"name": customer.first_name, "email": customer.email})
        
        if request.method == 'POST':
            if form.is_valid():
                order = form.save(commit=False)
                order.customer = customer
                order.payable = cart.get_total_price()
                order.totalbook = len(cart)
                order.save()

                # Create Shipment object right after saving the order
                shipment = Shipment.objects.create(
                    order=order,
                    tracking_number=f"TRACK-{order.id}-{order.transaction_id}"[:20]
                )

                for item in cart:
                    if 'book' in item:
                        OrderItem.objects.create(
                            order=order,
                            book=item['book'],
                            item_type='book',
                            price=item['price'],
                            quantity=item['quantity']
                        )
                    elif 'merchandise' in item:
                        OrderItem.objects.create(
                            order=order,
                            merchandise=item['merchandise'],
                            item_type='merchandise',
                            price=item['price'],
                            quantity=item['quantity']
                        )

                cart.clear()
                # Add a success message with the order ID
                messages.success(request, f"Your order #{order.id} has been placed successfully. You can track your order status using this ID.")
                return render(request, 'order/successfull.html', {'order': order, 'shipment': shipment})
            else:
                messages.error(request, "Fill out your information correctly.")

        if len(cart) > 0:
            return render(request, 'order/order.html', {"form": form})
        else:
            return redirect('store:books')
    else:
        return redirect('store:signin')


# ------------------------- Order List -----------------------------
def order_list(request):
    my_order = Order.objects.filter(customer_id=request.user.id).order_by('-created')
    paginator = Paginator(my_order, 5)
    page = request.GET.get('page')
    myorder = paginator.get_page(page)

    return render(request, 'order/list.html', {"myorder": myorder})

# ------------------------- Order Details -----------------------------
def order_details(request, id):
    order_summary = get_object_or_404(Order, id=id)

    if order_summary.customer_id != request.user.id:
        return redirect('store:index')

    orderedItem = OrderItem.objects.filter(order_id=id)
    
    # Get the shipment information
    try:
        shipment = Shipment.objects.get(order=order_summary)
    except Shipment.DoesNotExist:
        shipment = None
    
    context = {
        "o_summary": order_summary,
        "o_item": orderedItem,
        "shipment": shipment
    }
    return render(request, 'order/details.html', context)

# ------------------------- PDF Export -----------------------------
class pdf(View):
    def get(self, request, id):
        query = get_object_or_404(Order, id=id)
        context = {
            "order": query
        }
        article_pdf = renderPdf('order/pdf.html', context)
        return HttpResponse(article_pdf, content_type='application/pdf')

# ------------------------- Track Order Input -----------------------------
def track_order_input(request):
    if request.method == "POST":
        order_id = request.POST.get("order_id")
        if not order_id:
            messages.error(request, "Please enter an order ID.")
            return render(request, 'order/track_order_input.html')
            
        try:
            order_id = int(order_id)
            return redirect('order:track_shipment', order_id=order_id)
        except ValueError:
            messages.error(request, "Please enter a valid numeric Order ID.")
            return render(request, 'order/track_order_input.html')
    
    return render(request, 'order/track_order_input.html')

# ------------------------- Track Order -----------------------------
def track_order(request):
    # This function is now mainly for backward compatibility
    if request.method == "POST":
        order_id = request.POST.get("order_id")
        
        if not order_id or not order_id.isdigit():
            messages.error(request, "Please enter a valid numeric Order ID.")
            return redirect('order:track_order_input')
        
        # Redirect to the new tracking page
        return redirect('order:track_shipment', order_id=int(order_id))
    
    # If no POST data, redirect to input page
    return redirect('order:track_order_input')

# ------------------------- Track Shipment -----------------------------
def track_shipment_view(request, order_id):
    try:
        # First check if the order exists at all
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            messages.error(request, "No order found with that ID.")
            return redirect('order:track_order_input')

        # If user is logged in, check if this is their order
        if request.user.is_authenticated and order.customer != request.user:
            messages.warning(request, "This order belongs to another customer. You can only track your own orders when logged in.")
            return redirect('order:track_order_input')

        # Get the shipment information
        try:
            shipment = Shipment.objects.get(order=order)
        except Shipment.DoesNotExist:
            messages.error(request, "No shipment information found for this order.")
            return redirect('order:track_order_input')

        # Define the standard tracking steps
        steps = ['Order Placed', 'Processing', 'Shipped', 'Out for Delivery', 'Delivered']
        
        # Normalize the status for display and comparison
        current_status = shipment.get_status_display()
        
        # Find the current step index
        try:
            current_index = next((i for i, step in enumerate(steps) if step.lower() == current_status.lower()), -1)
            if current_index == -1:
                # If status not found in steps, use it as is but show a warning
                messages.warning(request, f"The order has a custom status: {current_status}")
                completed_steps = []
            else:
                # All steps up to and including the current one are completed
                completed_steps = steps[:current_index+1]
        except Exception as e:
            messages.error(request, f"Error processing tracking steps: {str(e)}")
            completed_steps = []

        # Get all items in the order
        order_items = OrderItem.objects.filter(order=order)
        
        # Calculate the estimated delivery date (7 days from order date for simplicity)
        from datetime import timedelta
        estimated_delivery = order.created + timedelta(days=7)
        
        context = {
            'order': order,
            'shipment': shipment,
            'steps': steps,
            'current_status': current_status,
            'completed_steps': completed_steps,
            'order_items': order_items,
            'estimated_delivery': estimated_delivery
        }
        
        return render(request, 'order/track_shipment.html', context)
        
    except Exception as e:
        messages.error(request, f"Error tracking shipment: {str(e)}")
        return redirect('order:track_order_input')

