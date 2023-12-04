from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Customer,Wallet


@receiver(post_save, sender=Customer)
def create_user_wallet(sender, instance, created, **kwargs):

    if created and not instance.is_staff:
        Wallet.objects.get_or_create(user=instance)
