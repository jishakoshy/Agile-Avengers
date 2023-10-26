from django.contrib.auth import logout
from django.shortcuts import render,redirect,get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
# from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from .models import Customer , Product ,Subimage, Category
from django.contrib.auth import authenticate,login
from django.contrib.auth.models import User
from django.http import HttpResponse

from django.db.models import Q

# from twilio.rest import Client
import random
import string



def Sign_up(request):
    if request.method == 'POST':
        first_name = request.POST['fname']
        last_name = request.POST['lname']
        email = request.POST['email']
        password = request.POST['password']
        cpassword = request.POST['cpassword']
        phone_number = request.POST['phone_number']

        # Check if the user with the provided email already exists using the Customer model
        if Customer.objects.filter(email=email).exists():
            messages.error(request, 'This email is already registered.')
            return redirect('sign_up')

        # Check if passwords match
        if password != cpassword:
            messages.error(request, 'Passwords do not match.')
            return redirect('sign_up')

        # Create a new user using the Customer model
        customer = Customer(first_name=first_name, last_name=last_name, email=email, phone_number=phone_number)
        customer.set_password(password)  # Set the password securely
        customer.save()
        login(request, customer)  # Log in the user
        messages.success(request, 'Account created successfully. You are now logged in.')
        return redirect('home')

    return render(request, 'signup.html')


# login:--------------------------------------|||||

def loginn(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, 'Login successful.')
            return redirect('home')
        else:
            messages.error(request, 'Invalid email or password.')

    return render(request, 'login.html')

@login_required
def Home(request):
    product = Product.objects.filter(deleted=False)
    return render(request,'home.html', {'products':product})


def signout(request):
    logout(request)
    return redirect('home')     

def Product_detail(request,product_id):
    product = Product.objects.get(id = product_id)
    subimage = Subimage.objects.filter(products_id = product)
       
    return render(request,'productdetail.html',{'product':product , 'subimg' : subimage})

def search_products(request):
    query = request.GET.get('q', '')
    products = Product.objects.filter(Name__icontains=query)
    context = {'products': products, 'query': query}
    return render(request, 'category.html', context)


# Admin Side:
def Admin_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('admin_dashboard')
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'admin-login.html')
        
def Admin_dash(request):
    return render(request, 'admindash.html')


def Productlist(request):
    if request.method == 'POST':
        search_query = request.POST.get('search')
        products = Product.objects.filter(Q(Name__icontains=search_query) & ~Q(deleted=True))
    else:
        products = Product.objects.filter(deleted=False)
    categories = Category.objects.all()
    return render(request, 'adminproductview.html', {'product': products, 'cat': categories})

def Add_category(request):
    if request.method == 'POST':
        name = request.POST['name']
        description = request.POST['discription']
        category= Category.objects.create(Name = name , description = description )
        category.save()
    
    cate = Category.objects.all()
    return render(request,'add_category.html' , {'category' : cate})
    

def Admin_edit(request,id):
    product = Product.objects.get(id=id)
    category = Category.objects.all()
    productCat = product.category
    
    if request.method == 'POST':
        category_name = request.POST.get('category')
        
        try:
            category = Category.objects.get(id=category_name)
            # product.category = category
            product = Product.objects.get(id=id)
        except Category.DoesNotExist:
            pass

        product.Name = request.POST['name']
        product.quantity = request.POST['quantity']
        product.price = request.POST['price']

        product.save()
        return redirect('productview')
    
    return render(request,'admin_edit.html',{'editpro':product,'cat': category,'prodcat':productCat})
   

def Admin_delete(request,id):
    product = get_object_or_404(Product, id=id)
    product.deleted = True
    product.save()
    return redirect('productview')

def Add_product(request):
    if request.method == 'POST':
        Name = request.POST['name']
        description = request.POST['discription']
        quantity = request.POST['quantity']
        price = request.POST['price']
        image = request.FILES['image']
        if 'category' in request.POST:
            category_name = request.POST['category']
            try:
                category = Category.objects.get(Name=category_name)
            except Category.DoesNotExist:
                category = None
        
        else:
            
            category = None
        
        product = Product.objects.create(Name = Name, description = description, quantity  = quantity, price =price, image= image , category = category)

        product.save()
        for file in request.FILES.getlist('subimages'):
            Subimage.objects.create(products = product, image = file )
        messages.success(request, 'product added Sucessfully')
    
    cat = Category.objects.all()
    return render(request,'addproduct.html', {'category' : cat})


# def Admin_search(request):


def user_management(request):
    users = Customer.objects.all()

    return render(request, 'admin_user_manage.html', {'users': users})

def block_user(request, user_id):
    # Retrieve the user by their ID
    user = Customer.objects.get(pk=user_id)
    user.is_active = False
    user.save()
    messages.success(request, f'User {user.first_name} {user.last_name} has been blocked.')
    return redirect('user_management')

def unblock_user(request, user_id):
    # Retrieve the user by their ID
    user = Customer.objects.get(pk=user_id)
    user.is_active = True
    user.save()
    messages.success(request, f'User {user.first_name} {user.last_name} has been unblocked.')
    return redirect('user_management')

