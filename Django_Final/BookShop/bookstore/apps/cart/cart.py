from decimal import Decimal
from django.conf import settings
from store.models import Book
from merchandise.models import Product


class Cart(object):
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, item, item_type='book'):
        item_id = f"{item_type}_{item.id}"  # Prefix the ID with the item type
        
        if item_id not in self.cart:
            if item_type == 'book':
                self.cart[item_id] = {'quantity': 0, 'price': str(item.price), 'type': item_type}
            elif item_type == 'merchandise':
                if item.on_sale and item.sale_price:
                    self.cart[item_id] = {'quantity': 0, 'price': str(item.sale_price), 'type': item_type}
                else:
                    self.cart[item_id] = {'quantity': 0, 'price': str(item.price), 'type': item_type}
                
            self.cart[item_id]['quantity'] = 1
        else:    
            if self.cart[item_id]['quantity'] < 10:
                self.cart[item_id]['quantity'] += 1

        self.save()

    def update(self, item, quantity, item_type='book'):
        item_id = f"{item_type}_{item.id}"
        if item_id in self.cart:
            self.cart[item_id]['quantity'] = quantity
            self.save()

    def save(self):
        self.session[settings.CART_SESSION_ID] = self.cart
        self.session.modified = True

    def remove(self, item, item_type='book'):
        item_id = f"{item_type}_{item.id}"
        if item_id in self.cart:
            del self.cart[item_id]
            self.save()

    def __iter__(self):
        # Group item_ids by type
        book_ids = []
        merchandise_ids = []
        
        for item_id in self.cart.keys():
            item_type, id_part = item_id.split('_', 1)
            if item_type == 'book':
                book_ids.append(int(id_part))
            elif item_type == 'merchandise':
                merchandise_ids.append(int(id_part))
        
        # Fetch books
        if book_ids:
            books = Book.objects.filter(id__in=book_ids)
            for book in books:
                item_id = f"book_{book.id}"
                self.cart[item_id]['book'] = book
                self.cart[item_id]['item'] = book  # Unified item reference
        
        # Fetch merchandise products
        if merchandise_ids:
            products = Product.objects.filter(id__in=merchandise_ids)
            for product in products:
                item_id = f"merchandise_{product.id}"
                self.cart[item_id]['merchandise'] = product
                self.cart[item_id]['item'] = product  # Unified item reference
        
        # Yield all items
        for item in self.cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())

    def clear(self):
        del self.session[settings.CART_SESSION_ID]
        self.session.modified = True
        
