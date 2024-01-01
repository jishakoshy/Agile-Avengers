from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Customer,Wallet

# from django.core.mail import send_mail
# from django.conf import settings

# def createProfile(sender, instance, created, **kwargs):
#     if created:
#         user = instance
#         profile = Customer.objects.create(
#             user = user, 
#             username = user.username,
#             email = user.email,
#             name = user.first_name
#             )


@receiver(post_save, sender=Customer)
def create_user_wallet(sender, instance, created, **kwargs):

    if created and not instance.is_staff:
        Wallet.objects.get_or_create(user=instance)





