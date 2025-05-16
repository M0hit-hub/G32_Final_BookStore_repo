from django.db import models

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=120)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    source = models.CharField(max_length=10, default='django')

    class Meta:
        db_table = 'contact_messages'
        app_label = 'portal'
        managed = True

    def __str__(self):
        return f"{self.name} - {self.created_at}"