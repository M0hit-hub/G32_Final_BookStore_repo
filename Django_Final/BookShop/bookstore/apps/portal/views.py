from django.shortcuts import render
from django.http import HttpResponseServerError, JsonResponse
from .utils import is_flask_server_running
from django.core.mail import send_mail
from django.conf import settings
from .models import ContactMessage
from django.db import connections

def home(request):
    """
    View for the landing page that shows options to open the bookstore or merchandise portal
    """
    return render(request, 'portal/index.html')

def about(request):
    if not is_flask_server_running():
        return render(request, 'service_unavailable.html')
    return render(request, 'about.html')

def contact(request):
    if not is_flask_server_running():
        return render(request, 'service_unavailable.html')
        
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        
        if name and email and message:
            try:
                # Save to MySQL database
                new_contact = ContactMessage(
                    name=name,
                    email=email,
                    message=message,
                    source='django'
                )
                new_contact.save(using='contact_db')
                
                # Send email
                send_mail(
                    subject=f'New Contact Message from {name}',
                    message=f'From: {name}\nEmail: {email}\n\nMessage:\n{message}',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.CONTACT_EMAIL],
                    fail_silently=False,
                )
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'message': 'Your message has been sent successfully!'
                    })
                
            except Exception as e:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'message': 'An error occurred while sending your message. Please try again.'
                    })
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': 'Please fill in all required fields.'
                })
    
    return render(request, 'contact.html')