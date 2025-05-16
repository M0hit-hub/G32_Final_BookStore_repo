# BookShop Project Structure

```
bookstore/
├── apps/                    # All Django applications
│   ├── cart/               # Shopping cart functionality
│   ├── merchandise/        # Merchandise shop
│   ├── mylandingpage/      # Landing page
│   ├── order/             # Order processing
│   ├── portal/            # Main portal
│   ├── search/            # Search functionality
│   └── store/             # Book store
├── static/                 # Static files
│   ├── css/               # CSS files
│   ├── js/                # JavaScript files
│   ├── fonts/             # Font files
│   ├── images/            # Image files
│   └── img/               # Additional images
├── templates/             # Global templates
│   ├── base.html         # Base template
│   ├── about.html        # About page
│   └── contact.html      # Contact page
├── media/                 # User-uploaded files
│   ├── bookpage/         # Book images
│   ├── merchandise/      # Merchandise images
│   ├── category/         # Category images
│   ├── coverpage/        # Cover images
│   ├── slide/            # Slider images
│   └── writer/           # Writer images
├── manage.py             # Django management script
├── requirements.txt      # Project dependencies
└── settings.py          # Project settings
```

## Organization Guidelines

1. All Django apps should be placed in the `apps` directory
2. Static files should be organized in the `static` directory
3. Global templates should be in the `templates` directory
4. User-uploaded files should be in the `media` directory
5. Each app should have its own templates directory for app-specific templates
6. Each app should have its own static directory for app-specific static files 