from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

class Customer(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    phone_number = models.CharField(max_length=15, default='')
    # Add any additional fields you need

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # Add any other fields required for user creation

    def __str__(self):
        return self.email
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        blank=True,
        related_name='customuser_user_permissions',  # Custom related_name
    )
    groups = models.ManyToManyField(
        'auth.Group',
        blank=True,
        related_name='customuser_groups',  # Custom related_name
    )
# Your other models remain unchanged

class Product(models.Model):
    category = models.ForeignKey('Category', on_delete=models.CASCADE)
    Name  = models.CharField(max_length= 50)
    description  = models.TextField(max_length=200)
    quantity = models.IntegerField()
    price = models.IntegerField()
    image  = models.ImageField(upload_to='media/')
    subimg = models.ManyToManyField("Subimage", blank= True)
    status = models.BooleanField(default=True)
    deleted = models.BooleanField(default=False)

class Subimage(models.Model):
    products = models.ForeignKey(Product, on_delete=models.CASCADE)
    image   = models.ImageField(upload_to='subimage_media/')

class Category(models.Model):
    Name  = models.CharField(max_length= 50)
    description = models.TextField(default= True)
    status = models.BooleanField(default= True)

    























# class Customer(models.Model):
#     first_name = models.CharField(max_length=50)
#     last_name = models.CharField(max_length=50)
#     email = models.EmailField(unique=True)
#     password = models.CharField(max_length=15, default='')
#     is_staff = models.BooleanField(default=False)
#     is_active = models.BooleanField(default=True)
#     phone_number = models.CharField(max_length=15, default='')
#     # otp = models.CharField(max_length=6, blank=True)
#     # is_verified = models.BooleanField(default=False)
   


# class Product(models.Model):
#     category = models.ForeignKey('Category', on_delete=models.CASCADE)
#     Name  = models.CharField(max_length= 50)
#     description  = models.TextField(max_length=200)
#     quantity = models.IntegerField()
#     price = models.IntegerField()
#     image  = models.ImageField(upload_to='media/')
#     subimg = models.ManyToManyField("Subimage", blank= True)
#     status = models.BooleanField(default=True)
#     deleted = models.BooleanField(default=False)


    
# class Subimage(models.Model):
#     products = models.ForeignKey(Product, on_delete=models.CASCADE)
#     image   = models.ImageField(upload_to='subimage_media/')

# class Category(models.Model):
#     Name  = models.CharField(max_length= 50)
#     description = models.TextField(default= True)
#     status = models.BooleanField(default= True)



