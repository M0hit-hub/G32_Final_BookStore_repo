from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order, Shipment

@receiver(post_save, sender=Order)
def create_shipment_for_new_order(sender, instance, created, **kwargs):
    if created:
        Shipment.objects.create(order=instance)
