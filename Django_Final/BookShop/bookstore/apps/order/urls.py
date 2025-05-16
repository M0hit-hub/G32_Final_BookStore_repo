from django.urls import path
from . import views


app_name = 'order'

urlpatterns = [
    path('create/', views.order_create, name='order_create'),
    path('list/', views.order_list, name='order_list'),
    path('details/<int:id>/', views.order_details, name='order_details'),
    path('pdf/<int:id>/', views.pdf.as_view(), name='order_pdf'),
    path('track/', views.track_order_input, name='track_order_input'),
    path('track-order/', views.track_order, name='track_order'),
    path('track-shipment/<int:order_id>/', views.track_shipment_view, name='track_shipment'),
]


