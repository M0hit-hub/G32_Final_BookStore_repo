from django.core.management.base import BaseCommand
from django.utils.text import slugify
from merchandise.models import Category, Product

class Command(BaseCommand):
    help = 'Creates sample merchandise categories and products'

    def handle(self, *args, **options):
        # Create Categories
        categories = [
            {
                'name': 'Coffee',
                'slug': 'coffee',
            },
            {
                'name': 'Mugs',
                'slug': 'mugs',
            },
            {
                'name': 'Apparel',
                'slug': 'apparel',
            },
            {
                'name': 'Stationery',
                'slug': 'stationery',
            },
        ]

        created_categories = []
        for category_data in categories:
            category, created = Category.objects.get_or_create(
                name=category_data['name'],
                slug=category_data['slug']
            )
            created_categories.append(category)
            status = 'Created' if created else 'Already exists'
            self.stdout.write(self.style.SUCCESS(f"{status}: Category '{category.name}'"))

        # Create Products
        products = [
            # Coffee Products
            {
                'category': 'coffee',
                'name': 'Bookworm Blend - Ground Coffee',
                'slug': 'bookworm-blend-ground-coffee',
                'description': 'A smooth, medium-roast coffee perfect for reading sessions. This artisanal blend combines Ethiopian and Colombian beans for a flavor profile with notes of chocolate and light citrus.',
                'price': 14.99,
                'stock': 50,
                'is_new': True,
                'on_sale': False,
            },
            {
                'category': 'coffee',
                'name': 'Literary Brew - Whole Beans',
                'slug': 'literary-brew-whole-beans',
                'description': 'Our premium dark roast coffee made from 100% Arabica beans. This bold and rich blend has hints of caramel and a smooth finish that will keep you turning pages all night.',
                'price': 16.99,
                'stock': 35,
                'is_new': False,
                'on_sale': True,
                'sale_price': 13.99,
            },
            # Mugs
            {
                'category': 'mugs',
                'name': 'Book Lovers Ceramic Mug',
                'slug': 'book-lovers-ceramic-mug',
                'description': 'A large 16oz ceramic mug perfect for your favorite hot beverage. Features a wraparound design with famous literary quotes and book illustrations.',
                'price': 18.99,
                'stock': 25,
                'is_new': True,
                'on_sale': False,
            },
            {
                'category': 'mugs',
                'name': 'Chapter Travel Tumbler',
                'slug': 'chapter-travel-tumbler',
                'description': 'This insulated 20oz travel tumbler keeps your drinks hot or cold for hours. Perfect for readers on the go with a spill-proof lid and comfortable grip.',
                'price': 24.99,
                'stock': 15,
                'is_new': False,
                'on_sale': False,
            },
            # Apparel
            {
                'category': 'apparel',
                'name': 'Bibliophile T-Shirt',
                'slug': 'bibliophile-tshirt',
                'description': 'A comfortable 100% cotton t-shirt with our exclusive "Bibliophile" design. Available in multiple sizes and colors.',
                'price': 22.99,
                'stock': 40,
                'is_new': False,
                'on_sale': False,
            },
            {
                'category': 'apparel',
                'name': 'Reading Socks',
                'slug': 'reading-socks',
                'description': 'Ultra-cozy reading socks with non-slip grips. These plush socks are perfect for curling up with a good book on cold days.',
                'price': 12.99,
                'stock': 30,
                'is_new': True,
                'on_sale': True,
                'sale_price': 9.99,
            },
            # Stationery
            {
                'category': 'stationery',
                'name': 'Literary Quotes Journal',
                'slug': 'literary-quotes-journal',
                'description': 'A beautiful hardcover journal featuring famous literary quotes. Contains 200 pages of high-quality paper perfect for writing or sketching.',
                'price': 19.99,
                'stock': 20,
                'is_new': False,
                'on_sale': False,
            },
            {
                'category': 'stationery',
                'name': 'Bookshop Bookmark Set',
                'slug': 'bookshop-bookmark-set',
                'description': 'A set of 5 magnetic bookmarks featuring unique designs inspired by classic books. These durable bookmarks won\'t damage your pages.',
                'price': 8.99,
                'stock': 45,
                'is_new': True,
                'on_sale': False,
            },
        ]

        for product_data in products:
            category_slug = product_data.pop('category')
            category = Category.objects.get(slug=category_slug)
            
            product, created = Product.objects.get_or_create(
                category=category,
                slug=product_data['slug'],
                defaults=product_data
            )
            
            status = 'Created' if created else 'Already exists'
            self.stdout.write(self.style.SUCCESS(f"{status}: Product '{product.name}'"))

        self.stdout.write(self.style.SUCCESS('Sample merchandise data created successfully!')) 