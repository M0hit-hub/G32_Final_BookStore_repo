from django.db import models
from store.models import Book
from django.contrib.auth.models import User
from merchandise.models import Product


class Order(models.Model):
	customer = models.ForeignKey(User, on_delete = models.CASCADE)
	name = models.CharField(max_length=30)
	email = models.EmailField()
	phone = models.CharField(max_length=16)
	address = models.CharField(max_length=150)
	division = models.CharField(max_length=20)
	zip_code = models.CharField(max_length=30)
	payment_method = models.CharField(max_length = 20)
	account_no = models.CharField(max_length = 20)
	transaction_id = models.IntegerField()
	payable = models.IntegerField()
	totalbook = models.IntegerField()
	created = models.DateTimeField(auto_now_add=True)
	updated = models.DateTimeField(auto_now=True)
	paid = models.BooleanField(default=False)

	class Meta:
		ordering = ('-created', )

	def __str__(self):
		return 'Order {}'.format(self.id)

	def get_total_cost(self):
		return sum(item.get_cost() for item in self.items.all())


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, null=True, blank=True)
    merchandise = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    item_type = models.CharField(max_length=20, choices=[('book', 'Book'), ('merchandise', 'Merchandise')], default='book')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        if self.item_type == 'book' and self.book:
            return f'Book: {self.book.name}'
        elif self.item_type == 'merchandise' and self.merchandise:
            return f'Merchandise: {self.merchandise.name}'
        return f'Order Item {self.id}'

    def get_cost(self):
        return self.price * self.quantity

    def get_item_name(self):
        if self.item_type == 'book' and self.book:
            return self.book.name
        elif self.item_type == 'merchandise' and self.merchandise:
            return self.merchandise.name
        return "Unknown Item"

    def get_item_image(self):
        if self.item_type == 'book' and self.book:
            return self.book.coverpage.url
        elif self.item_type == 'merchandise' and self.merchandise and self.merchandise.image:
            return self.merchandise.image.url
        return None


from django.utils import timezone

ORDER_STATUS = [
    ('order placed', 'Order Placed'),
    ('processing', 'Processing'),
    ('shipped', 'Shipped'),
    ('out for delivery', 'Out for Delivery'),
    ('delivered', 'Delivered'),
]

class Shipment(models.Model):
    order = models.OneToOneField('Order', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='order placed')
    tracking_number = models.CharField(max_length=50, blank=True, null=True)
    carrier = models.CharField(max_length=50, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.order.id} - {self.status}"


