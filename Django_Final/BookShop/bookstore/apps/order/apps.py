from django.apps import AppConfig


class OrderConfig(AppConfig):
    name = 'order'




class YourAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'order'  # <-- yaha apne app ka exact naam daalna

    def ready(self):
        import order.signals  # <-- yaha bhi wahi naam
