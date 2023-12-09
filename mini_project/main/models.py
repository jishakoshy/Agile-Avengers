# from ctypes import addressof
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


class Address(models.Model):
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE, related_name='addresses')
    address = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    postalcode= models.IntegerField(default=1)

    def __str__(self):
        return f"{self.address}"

class Customer(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    phone_number = models.CharField(max_length=15, default='')

    selected_address = models.OneToOneField('Address', null=True, blank=True, on_delete=models.SET_NULL, related_name='selected_address_for_customer')

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  
    
    def __str__(self):
        return self.email
    
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        blank=True,
        related_name='main_customuser_user_permissions',  
    )
    groups = models.ManyToManyField(
        'auth.Group',
        blank=True,
        related_name='main_customuser_groups',  
    )

class Wishlist(models.Model):
    user = models.ForeignKey('Customer', on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)

    def __str__(self):
        return f"Wishlist for {self.user} - {self.product}"

class Cart(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    user = models.ForeignKey('Customer', on_delete=models.CASCADE)
    quantity = models.IntegerField( default = 1, null=True) 
    
    def __str__(self):
        return f"Cart for {self.user}"


class Product(models.Model):
    category = models.ForeignKey('Category', on_delete=models.CASCADE)
    Name  = models.CharField(max_length= 50)
    description  = models.TextField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image  = models.ImageField(upload_to='media/')
    subimg = models.ManyToManyField("Subimage", blank= True)
    status = models.BooleanField(default=True)
    deleted = models.BooleanField(default=False)
    quantity = models.PositiveIntegerField(default=0)
    size = models.IntegerField(choices= [(7,'7'),(8,'8'),(9,'9')],null=True, blank=True, default=None)
    is_varient = models.BooleanField(default=False)
    def __str__(self):
        return self.Name

class Sale(models.Model):
    date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)  

class Subimage(models.Model):
    products = models.ForeignKey(Product, on_delete=models.CASCADE)
    image   = models.ImageField(upload_to='subimage_media/')

class Category(models.Model):
    Name  = models.CharField(max_length= 50)
    description = models.TextField()
    status = models.BooleanField()

    def soft_delete(self):
        self.status = False  
        self.save()

class Order(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Shipping', 'Shipping'),
        ('Delivered', 'Delivered'),
        ('Return', 'Return'),
        ('Reject', 'Reject'),
    ]
    payment_option = models.CharField(max_length=225,default='cod')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    order_date = models.DateTimeField(auto_now_add=True)
    razorpay_order_id = models.CharField(max_length=225,default=None, blank=True, null=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    cancel = models.BooleanField(default=False)
    returned = models.BooleanField(default=False)
    # delivered = models.BooleanField(default=False)
    def __str__(self):
        return f"Order #{self.pk} by {self.customer}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    product_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity}x {self.product.Name} in Order #{self.order.pk}"

class Wallet(models.Model):
    user = models.OneToOneField(Customer, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2,default=0.0)

    def _str_(self):
        return f"Wallet for {self.user.first_name}"

# models.py
class Transaction(models.Model):
    user = models.ForeignKey(Customer, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
    transaction_balance = models.DecimalField(max_digits=10, decimal_places=2)  # Use DecimalField for precision
    transaction_type = models.CharField(max_length=20, choices=(('Deposit', 'Deposit'), ('Withdrawal', 'Withdrawal'), ('Refund', 'Refund')))
    related_order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.transaction_type} of ${self.amount} for {self.user.first_name}"


