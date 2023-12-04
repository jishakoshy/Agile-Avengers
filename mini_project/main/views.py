from audioop import reverse
from decimal import Decimal
from gettext import translation
import re
# from django.http import Http404, JsonResponse
# from socket import AddressFamily
from django.contrib.auth import logout
from django.shortcuts import render,redirect,get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
# from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from .models import Customer , Product, Subimage, Category, Cart, Address, OrderItem, Order, Wishlist,Wallet,Transaction
from django.contrib.auth import authenticate,login
from django.contrib.auth.models import User,auth
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect, HttpResponseServerError
from django.db.models import Q,Sum
from django.views.decorators.cache import never_cache
from twilio.rest import Client
import pyotp
from datetime import datetime, timedelta
import random
import string
from .otpfun import sent_otp
from django.http import JsonResponse
import razorpay,json
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt


# Otp view
@never_cache
def verify_otp(request):
    if request.method == 'POST':
        verify_otp = request.POST.get('otp')

        if 'username' in request.session:
            username = request.session['username']
        else:
            messages.error(request, 'Username not found in session')
            return redirect('loginn')

        otp_secret_key = request.session['otp_secret_key']
        otp_valid_until = request.session['otp_valid_date']

        password_reset_otp = request.GET.get('password_reset')
        print(f'password_reset_otp: {password_reset_otp}')
        if password_reset_otp:
            # Handle OTP for password reset
            if sent_otp(request):  # Send OTP for password reset
                # Store the username and OTP secret for password reset
                request.session['username_for_reset'] = username
                request.session['otp_secret_key_for_reset'] = otp_secret_key
                return render(request, 'password_reset.html', {'otp_sent': True})
            else:
                messages.error(request, 'Error sending OTP for password reset')
                return redirect('loginn')  # Redirect back to login if OTP sending fails

        # Handle OTP for login
        if otp_secret_key and otp_valid_until:
            valid_until = datetime.fromisoformat(otp_valid_until)
            if valid_until > datetime.now():
                totp = pyotp.TOTP(otp_secret_key, interval=60)
                if totp.verify(verify_otp):
                    user = get_object_or_404(Customer, email=username)
                    login(request, user)
                    del request.session['otp_secret_key']
                    del request.session['otp_valid_date']
                    return redirect('home')
                else:
                    messages.error(request, 'Invalid one time password')
            else:
                messages.error(request, 'one time password expired')
        else:
            messages.error(request, 'something went wrong')

    return render(request, 'userside/otp.html')

# Otp view
# @never_cache
# def verify_otp(request):
#     if request.method == 'POST':
#         verify_otp = request.POST.get('verify_otp') 

#         if 'username' in request.session:
#             username = request.session['username']
#         else:
#             messages.error(request, 'Username not found in session')
#             return redirect('user_view')

#         otp_secret_key = request.session['otp_secret_key']
#         otp_valid_until = request.session['otp_valid_date']
#         if otp_secret_key and otp_valid_until:
#             valid_until = datetime.fromisoformat(otp_valid_until)
#             if valid_until > datetime.now():
#                 totp = pyotp.TOTP(otp_secret_key, interval = 60)
#                 if totp.verify(verify_otp):
#                     user = get_object_or_404(oddityFindsUser, email = username)
#                     login(request, user)
#                     del request.session['otp_secret_key']
#                     del request.session['otp_valid_date']
#                     return redirect('home')
#                 else:
#                     messages.error(request, 'Invalid one time password')                    
#             else:
#                 messages.error(request, 'one time password expired')
#         else:
#             messages.error(request, 'something went wrong')
#     return render(request, 'otp.html')



def Sign_up(request):
    if request.method == 'POST':
        first_name = request.POST['fname']
        last_name = request.POST['lname']
        email = request.POST['email']
        password = request.POST['password']
        cpassword = request.POST['cpassword']
        phone_number = request.POST['phone_number']

        if Customer.objects.filter(email=email).exists():
            messages.error(request, 'This email is already registered.')
            return redirect('sign_up')

        if password != cpassword:
            messages.error(request, 'Passwords do not match.')
            return redirect('sign_up')

        if not re.match(r'^[6-9]\d{9}$', phone_number):
            messages.error(request, 'Please enter a valid 10-digit phone number starting with 6-9.')
            return redirect('sign_up')

        customer = Customer(first_name=first_name, last_name=last_name, email=email, phone_number=phone_number)
        customer.set_password(password) 
        customer.save()
        login(request, customer)  
        messages.success(request, 'Account created successfully. You are now logged in.')
        userwallet = Wallet.objects.create(user= customer)

        return redirect('loginn')

    return render(request, 'userside/signup.html')



# User login:--------------------------------------|||||
def loginn(request):  
    if request.method == 'POST':
        username = request.POST['email']
        password = request.POST['password']

        user = authenticate(request, email=username, password = password)

        if user is not None:
            print("user found")               
            if user.is_active:
                print("user Active")
                if sent_otp(request):
                    print("Otp sent")
                    request.session['username'] = username
                    return redirect('verify_otp')
            else:
                messages.error(request, 'you are blocked')          
        else:
            messages.error(request, 'Invalid email or password.')

    return render(request, 'userside/login.html')


def Home(request):
    product = Product.objects.filter(deleted=False, is_varient = False)
    return render(request,'userside/home.html', {'products':product})

    

# @login_required
def signout(request):
    logout(request)
    return redirect('home') 

# def signout(request):
#     if 'username' in request.session:
#         request.session.flush()
#     return redirect(loginn)     

def Shop(request):
    product = Product.objects.filter(deleted=False, is_varient = False)
    return render(request,'userside/shop.html' , {'products': product})

def Product_detail(request,product_id):
    product = Product.objects.get(id = product_id)
    subimage = Subimage.objects.filter(products_id = product)
    variants = Product.objects.filter(Name=product.Name)
    sizes = []
    for item in variants:
        sizes.append(item.size)
    print("Available sizes are ",sizes)
    if request.method == 'POST':
        size = request.POST['size']
        product = Product.objects.filter(Name = product.Name , size = size).first()
    return render(request,'userside/productdetail.html',{'product':product , 'subimg' : subimage, "sizes":sizes})
# search
def search_products(request):
    query = request.GET.get('q', '')
    products = Product.objects.filter(Name__icontains=query)
    context = {'products': products, 'query': query}
    return render(request, 'userside/category.html', context)

# filter
def category_filter(request, category_id):
    category = Category.objects.get(pk=category_id)
    products = Product.objects.filter(category=category, status=True, deleted=False)
    return render(request, 'userside/category.html', {'products': products})

@login_required
def add_to_cart(request, product_id):
    user = request.user
    product = Product.objects.get(id=product_id)

    cart_item, created = Cart.objects.get_or_create(user=user, product=product)
    # if created:
    #     cart_item.quantity += 1
    #     cart_item.save()

    items = Cart.objects.filter(user=user)
    return render(request, 'userside/cartmanage.html', {'items': items})

# wishlist
def wishlist_view(request):
    if request.user.is_authenticated:       
        wishlist_items = Wishlist.objects.filter(user=request.user)
    else:
        wishlist_items = []  

    context = {
        'wishlist_items': wishlist_items,
    }
    return render(request, 'userside/wishlist.html', context)

@login_required
def add_to_wishlist(request, product_id):
    user = request.user
    product = get_object_or_404(Product, id=product_id)

    if Wishlist.objects.filter(user=user, product=product).exists():
        messages.warning(request, f'{product.Name} is already in your wishlist.')
    else:
        Wishlist.objects.create(user=user, product=product)
        messages.success(request, f'{product.Name} added to your wishlist successfully.')

    return redirect('wishlist')

@login_required
def cart(request):
    cart_items = Cart.objects.filter(user=request.user)
    subtotal = sum(item.product.price * item.quantity for item in cart_items)

    context = {
        'items': cart_items,
        'subtotal': subtotal,
    }

    return render(request, 'userside/cartmanage.html', context)


def remove_from_cart(request, product_id):
    product = Product.objects.get(pk=product_id)
    user = request.user
    cart_item = Cart.objects.get(user=user, product=product)
    cart_item.delete()
    return redirect('cart')

def update_quantity(request, product_id):
    product = Product.objects.get(pk=product_id)
    cart = Cart.objects.get(user=request.user, product=product)
    quantity = int(request.GET.get('quantity'))
   
    cart.quantity = quantity
    cart.save()
    return redirect('cart')

# checkout page:-
# @login_required
# def checkout_view(request):
#     cart_items = Cart.objects.filter(user=request.user)
#     address = Address.objects.filter(customer=request.user).first()
#     subtotal = sum(item.product.price * item.quantity for item in cart_items)
#     shipping = Decimal('50.00')
#     total = subtotal + shipping
    
#     order = Order.objects.create(customer=request.user, total_amount=total, payment_method='YourPaymentMethodHere')

#     # Create order items for each item in the cart
#     for cart_item in cart_items:
#         OrderItem.objects.create(order=order, product=cart_item.product, quantity=cart_item.quantity, product_price=cart_item.product.price)
#         # cart_item.product.quantity -= cart_item.quantity
#         # cart_item.product.save()

#     cart_items.delete()
#     orders = OrderItem.objects.filter(order=order)
#     print("Current orders", orders)
    
#     client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET_KEY))
#     razorpay_order = client.order.create({
#         'amount': int(total * 100),  
#         'currency': 'INR',  
#         'payment_capture': 1 
#     })

#     order.razorpay_order_id = razorpay_order['id']
#     order.save()
#     context = {
#         'items': orders,
#         'address':address,
#         'subtotal': subtotal,
#         'shipping': shipping,
#         'total': total,
#         'order': order,
#         'razorpay_order_id': razorpay_order['id'],
#         'razorpay_key': settings.RAZORPAY_API_KEY,
        
#     }

#     return render(request, 'userside/checkout.html', context)


# @login_required
# def checkout_view(request):
#     cart_items = Cart.objects.filter(user=request.user)
#     address = Address.objects.filter(customer=request.user).first()
#     subtotal = sum(item.product.price * item.quantity for item in cart_items)
#     shipping = Decimal('50.00')
#     total = subtotal + shipping
#     payment_method = request.GET.get('payment_method', 'Default Payment Method')

#     order = Order.objects.create(customer=request.user, total_amount=total, payment_method=payment_method)

#     for cart_item in cart_items:
#         OrderItem.objects.create(order=order, product=cart_item.product, quantity=cart_item.quantity, product_price=cart_item.product.price)

#     cart_items.delete()
#     orders = OrderItem.objects.filter(order=order)
    
#     client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET_KEY))
#     razorpay_order = client.order.create({
#         'amount': int(total * 100),  
#         'currency': 'INR',  
#         'payment_capture': 1 
#     })

#     order.razorpay_order_id = razorpay_order['id']
#     order.save()
#     context = {
#         'items': orders,
#         'address': address,
#         'subtotal': subtotal,
#         'shipping': shipping,
#         'total': total,
#         'order': order,
#         'razorpay_order_id': razorpay_order['id'],
#         'razorpay_key': settings.RAZORPAY_API_KEY,
#     }

#     return render(request, 'userside/checkout.html', context)

# -----------------------------------------quantity updation on admin happening here-----------
from django.db import transaction

@login_required
def checkout_view(request):
    cart_items = Cart.objects.filter(user=request.user)
    address = Address.objects.filter(customer=request.user).first()
    subtotal = sum(item.product.price * item.quantity for item in cart_items)
    shipping = Decimal('50.00')
    total = subtotal + shipping
    payment_method = request.GET.get('payment_method', 'cod')

    with transaction.atomic():

        order = Order.objects.create(customer=request.user, total_amount=total, payment_method=payment_method)

        for cart_item in cart_items:
            OrderItem.objects.create(order=order, product=cart_item.product, quantity=cart_item.quantity,
                                     product_price=cart_item.product.price)

            product = Product.objects.get(id=cart_item.product.id)
            product.quantity -= cart_item.quantity
            product.save()

        cart_items.delete()

        client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET_KEY))
        razorpay_order = client.order.create({
            'amount': int(total * 100),
            'currency': 'INR',
            'payment_capture': 1
        })

        order.razorpay_order_id = razorpay_order['id']
        order.save()

    context = {
        'address': address,
        'subtotal': subtotal,
        'shipping': shipping,
        'total': total,
        'order': order,
        'razorpay_order_id': razorpay_order['id'],
        'razorpay_key': settings.RAZORPAY_API_KEY,
    }

    return render(request, 'userside/checkout.html', context)

@csrf_exempt
def payment_success(request):
    return render(request, "userside/payment_success.html")


@login_required
def orderaddress(request):
    user_addresses = request.user.addresses.all()  
    user = Customer.objects.get(email = request.user)
    order = Order.objects.filter(customer=user).order_by('-order_date').first()
    orderitem = OrderItem.objects.filter(order = order)
    subtotal = order.total_amount
    shipping = Decimal('50.00')
    total = subtotal + shipping
    if request.method == 'POST':
        selected_address_id = request.POST.get('selected_address')
        if selected_address_id:
            selected_address = Address.objects.get(id=selected_address_id)

            request.user.selected_address = selected_address 
            request.user.save()
        con = {
            'item': orderitem,
            'address':selected_address,
            'subtotal': subtotal ,
            'shipping': shipping,
            'total': total,
            'order': order,
        }
        return render(request, 'userside/checkout.html', con)  
    context = {
        'addresses': user_addresses,
    }
    return render(request, 'userside/orderaddress.html', context)


def order_add_addre(request):
    user = request.user
    cus = Customer.objects.get(email = user)
    if request.method == 'POST':
        
        address = request.POST.get('address')
        city = request.POST.get('city')
        post = request.POST.get('postalCode')

        sav = Address.objects.create(customer=cus, address=address, city=city, postalcode=post)
        sav.save()
        return redirect('orderaddress') 
    return render(request,'userside/ord_add_address.html')


# order management
def order_success(request, order_id):
    order = Order.objects.get(id=order_id)
    order_items = order.items.all() 
    context = {
        'order': order,
        'order_items': order_items,
    }
    return render(request, 'userside/ordermanage.html', context)


# orderlist cancel and wallet balance

# from .models import Transaction

# def cancelorder(request, order_id):
#     order = get_object_or_404(Order, id=order_id)
#     if not order.cancel:
#         order.cancel = True
#         order.save()
#         # Create a refund transaction
#         refund_amount = order.total_amount
#         refund_transaction = Transaction.objects.create(
#             user=request.user,
#             amount=-refund_amount,
#             transaction_type='Refund',
#             transaction_balance=request.user.wallet.balance - refund_amount,
#         )
#         # Update user's wallet balance
#         request.user.wallet.balance -= refund_amount
#         request.user.wallet.save()

#     return redirect("userprofile")


# cancel order and return order and wallet refund
def cancelorder(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if not order.cancel:
        order.cancel = True
        order.save()

        refund_amount = order.total_amount
        refund_transaction = Transaction.objects.create(
            user=request.user,
            amount=refund_amount,
            transaction_type='Refund',
            transaction_balance=request.user.wallet.balance + refund_amount,  
            related_order=order,
        )

        request.user.wallet.balance += refund_amount
        request.user.wallet.save()
    return redirect("userprofile")

def return_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    if not order.returned and order.status == 'Delivered':
        order.returned = True
        order.save()

        refund_amount = order.total_amount  
        refund_transaction = Transaction.objects.create(
            user=request.user,
            amount=refund_amount,
            transaction_type='Refund',
            transaction_balance=request.user.wallet.balance + refund_amount,
            related_order=order,
        )

        request.user.wallet.balance += refund_amount
        request.user.wallet.save()

    return redirect('userprofile')


# user profile -----------------------------------------------------------------------------------------
@login_required
def userprofile(request):
    user = request.user  
    orders = Order.objects.filter(customer=user)
    context = {
        'user': user,
        'orders': orders,
    }
    return render(request, 'userside/userprofile.html', context)

@login_required
def user_edit(request):
    user = request.user

    if request.method == 'POST':
        new_first_name = request.POST.get('new_first_name')
        new_last_name = request.POST.get('new_last_name')
        new_email = request.POST.get('new_email')
        new_phone_number = request.POST.get('new_phone_number')

        user.first_name = new_first_name
        user.last_name = new_last_name
        user.email = new_email
        user.phone_number = new_phone_number
        user.save()

        return redirect('userprofile')

    context = {
        'user': user,
    }
    return render(request, 'userside/USER-PROF-EDIT.html', context)


def remove_address(request, address_id):
    address = get_object_or_404(Address, id=address_id)
    address.delete()
    messages.success(request, 'Address removed successfully.')
    return redirect('viewaddress')

def add_addresses(request):
    user = request.user
    cus = Customer.objects.get(email = user)
    if request.method == 'POST':
        
        address = request.POST.get('address')
        city = request.POST.get('city')
        post = request.POST.get('postalCode')

        sav = Address.objects.create(customer=cus, address=address, city=city, postalcode=post)
        sav.save()
        return redirect('userprofile') 
    return render(request,'userside/2userprofile.html')

def edit_address(request, address_id):
    address = get_object_or_404(Address, id=address_id)

    if request.method == 'POST':
        new_address = request.POST.get('editAddress')
        new_city = request.POST.get('editCity')
        new_postalcode = request.POST.get('editPostalCode')

        address.address = new_address
        address.city = new_city
        address.postalcode = new_postalcode
        address.save()

        return redirect('viewaddress')
    return render(request, 'userside/userEditaddress.html', {'address': address})


@login_required
def view_address(request):
    user = request.user
    addresses = Address.objects.filter(customer=user)
    return render(request, 'userside/savedadd.html', {'address': addresses})


def view_order(request, order_id):
    my_user = request.user
    order = get_object_or_404(Order, pk=order_id, customer=request.user) 
    context = {'order': order  }
    return render(request, 'userside/user_order_view.html', context)


def get_product_quantity(request, product_id, qty):
    product = get_object_or_404(Product, id=product_id)
    print(product_id, qty)
    quantity = product.quantity
    return JsonResponse({'success': True, 'quantity': quantity})


# wallet
def wallet(request):
    user = request.user
    userd = Customer.objects.get(email=user)
    transactions = Transaction.objects.filter(user=user).order_by('-timestamp')
    return render(request, 'userside/wallet.html', {'user': userd, 'transactions': transactions})






# @login_required(login_url='user_view')
# def wallet(request):
#     user = request.user
#     userd = Customer.objects.get(email = user)
#     return render(request, 'userside/wallet.html' ,{'user': userd})

# def deposit_wallet(request):
#     if request.method == 'POST':
#         amount = request.POST.get('amount')
#         amount = Decimal(amount)


#         client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET_KEY))
#         razorpay_order = client.order.create({
#             'amount': int(amount * 100),
#             'currency': 'INR',
#             'payment_capture': 1
#         })
#         # order.razorpay_order_id = razorpay_order['id']
#         # order.save()

#         wallet = Wallet.objects.get(user=request.user)
#         wallet.balance += amount
#         wallet.save()

#         context = {
#             'total': amount,
#             'razorpay_order_id': razorpay_order['id'],
#             'razorpay_key': settings.RAZORPAY_API_KEY,
#         }

#         return render(request, 'userside/wallet.html', context)
#     return redirect('wallet_view')







