from django.contrib import admin
from .models import Order, OrderItem, Shipment

class OrderItemList(admin.TabularInline):
	model = OrderItem
	extra = 0

class OrderList(admin.ModelAdmin):
	list_display = ['id', 'customer', 'name', 'email', 'phone', 'address', 'division',
	                'zip_code', 'payment_method', 'account_no', 'totalbook', 'created', 'updated', 'paid', 'get_status']
	list_filter = ['paid']
	exclude = ['name', 'email', 'phone']
	inlines = [OrderItemList]

	def get_status(self, obj):
		try:
			return obj.shipment.status
		except Shipment.DoesNotExist:
			return "No Shipment"

	get_status.short_description = 'Shipment Status'

admin.site.register(Order, OrderList)
admin.site.register(OrderItem)

# ✅ Shipment admin with status update
@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
	list_display = ('order', 'status', 'updated_at')
	list_filter = ('status',)
	search_fields = ('order__id',)
