from django.shortcuts import render

def home(request):
    return render(request, 'landing/index.html')

def features(request):
    return render(request, 'landing/features.html')

def about(request):
    return render(request, 'landing/about.html')

def contact(request):
    return render(request, 'landing/contact.html')