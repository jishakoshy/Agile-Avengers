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
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings




# Otp view
# @never_cache
# def verify_otp(request):
#     if request.method == 'POST':
#         verify_otp = request.POST.get('verify_otp') 

#         if 'username' in request.session:
#             username = request.session['username']
#         else:
#             messages.error(request, 'Username not found in session')
#             return redirect('loginn')

#         otp_secret_key = request.session['otp_secret_key']
#         otp_valid_until = request.session['otp_valid_date']
#         if otp_secret_key and otp_valid_until:
#             valid_until = datetime.fromisoformat(otp_valid_until)
#             if valid_until > datetime.now():
#                 totp = pyotp.TOTP(otp_secret_key, interval=60)
#                 print("Generated OTP:", totp.now())
#                 print("Entered OTP:", verify_otp)

#                 if verify_otp and totp.verify(verify_otp):
#                     user = get_object_or_404(Customer, email=username)
#                     login(request, user)
#                     del request.session['otp_secret_key']
#                     del request.session['otp_valid_date']
#                     return redirect('home')
#                 else:
#                     messages.error(request, 'Invalid one-time password')                    
#             else:
#                 messages.error(request, 'One-time password expired')
#         else:
#             messages.error(request, 'Something went wrong')
#     return render(request, 'userside/otp.html')

# def loginn(request):  
#     if request.method == 'POST':
#         username = request.POST['email']
#         password = request.POST['password']

#         user = authenticate(request, email=username, password=password)

#         if user is not None:
#             print("User found")               
#             if user.is_active:
#                 print("User active")
#                 if sent_otp(request):
#                     print("OTP sent")
#                     request.session['username'] = username
#                     return redirect('verify_otp')
#             else:
#                 messages.error(request, 'You are blocked')          
#         else:
#             messages.error(request, 'Invalid email or password.')

#     return render(request, 'userside/login.html')

@never_cache
def loginn(request):
    if request.user.is_authenticated:
        return redirect('home')  
    if request.method == 'POST':
        username = request.POST['email']
        password = request.POST['password']

        user = authenticate(request, email=username, password=password)

        if user is not None:
            print("User found")               
            if user.is_active:
                login(request, user)
                request.session['username'] = username
                return redirect('home')
            else:
                messages.error(request, 'You are blocked')          
        else:
            messages.error(request, 'Invalid email or password.')

    return render(request, 'userside/login.html')

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
        else:
            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-z]+.com$' , email):
                messages.error(request, 'Enter email correctly.')
                return redirect('sign_up')

 
        if not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$', password):
            messages.error(request, 'Password must contain at least one uppercase letter, one lowercase letter, one digit, and one special character.')
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
# def loginn(request):  
#     if request.method == 'POST':
#         username = request.POST['email']
#         password = request.POST['password']

#         user = authenticate(request, email=username, password = password)

#         if user is not None:
#             print("user found")               
#             if user.is_active:
#                 print("user Active")
#                 if sent_otp(request):
#                     print("Otp sent")
#                     request.session['username'] = username
#                     return redirect('verify_otp')
#             else:
#                 messages.error(request, 'you are blocked')          
#         else:
#             messages.error(request, 'Invalid email or password.')

#     return render(request, 'userside/login.html')

@never_cache
def Home(request):   
    product = Product.objects.filter(deleted=False, is_varient = False)
    return render(request,'userside/home.html', {'products':product})

    

def signout(request):
    logout(request)
    return redirect('home') 

# def signout(request):
#     if 'username' in request.session:
#         request.session.flush()
#     return redirect(loginn)     

@never_cache
def Shop(request):
    product = Product.objects.filter(deleted=False, is_varient = False)
    return render(request,'userside/shop.html' , {'products': product})

@never_cache
def Product_detail(request,product_id):
    product = Product.objects.get(id = product_id)
    subimage = Subimage.objects.filter(products_id = product)
    variants = Product.objects.filter(Name=product.Name)
    sizes = []
    for item in variants:
        sizes.append(item.size)
    
    if request.method == 'POST':
        size = request.POST['size']
        product = Product.objects.filter(Name = product.Name , size = size).first()
    return render(request,'userside/productdetail.html',{'product':product , 'subimg' : subimage, "sizes":sizes})

@never_cache
# search
def search_products(request):
    query = request.GET.get('q', '')
    products = Product.objects.filter(Name__icontains=query)
    context = {'products': products, 'query': query}
    return render(request, 'userside/category.html', context)

# filter by category 
# def category_filter(request, category_id):
#     category = Category.objects.get(pk=category_id)
#     products = Product.objects.filter(category=category, status=True, deleted=False)
#     return render(request, 'userside/shop.html', {'products': products})

# # filter by min and max price
# def filter_products_by_price(request):
#     min_price = request.GET.get('min_price')
#     max_price = request.GET.get('max_price')

#     if min_price and max_price:
#         products = Product.objects.filter(price__gte=min_price, price__lte=max_price)
#     else:
#         products = Product.objects.all()
#     return render(request, 'userside/shop.html', {'products': products})


def category_filter(request, category_id):
    category = Category.objects.get(pk=category_id)
    products = Product.objects.filter(category=category, status=True, deleted=False)
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price and max_price:
        products = products.filter(price__gte=min_price, price__lte=max_price)
    return render(request, 'userside/shop.html', {'products': products, 'selected_category': category})


def filter_products_by_price(request):
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    category_id = request.GET.get('category_id')
   
    if category_id:
        category = get_object_or_404(Category, pk=category_id)
        products = Product.objects.filter(category=category, status=True, deleted=False)
    else:
        products = Product.objects.all()
    if min_price and max_price:
        products = products.filter(price__gte=min_price, price__lte=max_price)
        return render(request, 'userside/shop.html', {'products': products})
    return render(request, 'userside/shop.html', {'products': products, 'selected_category': category})
   

# add to cart
# @login_required
# def add_to_cart(request, product_id):
#     user = request.user
#     product = Product.objects.get(id=product_id)
#     cart_item, created = Cart.objects.get_or_create(user=user, product=product)
#     items = Cart.objects.filter(user=user)
#     return redirect('home')  

@login_required
def add_to_cart(request, product_id):
    user = request.user
    product = Product.objects.get(id=product_id)

    cart_item, created = Cart.objects.get_or_create(user=user, product=product)

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect('home')


# wishlist
@login_required
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

    return redirect('home')

@login_required
def delete_from_wishlist(request, item_id):
    item = get_object_or_404(Wishlist, id=item_id)
    item.delete()
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

def update_quantity(request, product_id, quantity):     
    product = Product.objects.get(id=product_id)
    cart = Cart.objects.get(user=request.user, product=product)
   
    cart.quantity = quantity
    if quantity > product.quantity:
        messages.warning(request,"limit exceeded")
    cart.save()
    cart_items = Cart.objects.filter(user=request.user)
    subtotal = sum(item.product.price * item.quantity for item in cart_items)

    return JsonResponse({'success': True, 'quantity': product.quantity, 'subtotal': subtotal})
  



# ------------------------quantity updation on admin happening here-----------

# from django.db import transaction
# @login_required
# def checkout_view(request):
#     cart_items = Cart.objects.filter(user=request.user)
#     address = Address.objects.filter(customer=request.user).first()
#     subtotal = sum(item.product.price * item.quantity for item in cart_items)
#     shipping = Decimal('50.00')
#     total = subtotal + shipping

#     if request.method == "POST":
#         payment = request.POST['payment_method']
#         if payment == 'cod':
#             order = Order.objects.create(customer=request.user, total_amount=total, payment_option=payment)
#             order_items = []
#             for cart_item in cart_items:
                
#                 OrderItem.objects.create(order=order, product=cart_item.product, quantity=cart_item.quantity,
#                                         product_price=cart_item.product.price)
#                 product = Product.objects.get(id=cart_item.product.id)
#                 product.quantity -= cart_item.quantity
#                 product.save()
#                 order_items.append({
#                     'product_name': cart_item.product.Name,
#                     'quantity': cart_item.quantity,
#                     'product_price': cart_item.product.price,
#                     'total_price': cart_item.product.price * cart_item.quantity,
#                 })
#             cart_items.delete()
#             context = {
#                 'order_items': order_items,
#                 'subtotal': subtotal,
#                 'shipping': shipping,
#                 'total': total,
#             }
#             return render(request, 'userside/payment_success.html', context)
#         else:
#             return redirect('payment')
#     context = {
#         'items': cart_items,
#         'address': address,
#         'subtotal': subtotal,
#         'shipping': shipping,
#         'total': total,
#     }
#     return render(request, 'userside/checkout.html', context)


from django.db.models import F
from django.db import transaction
@login_required
def checkout_view(request):
    cart_items = Cart.objects.filter(user=request.user)
    address = Address.objects.filter(customer=request.user).first()
    subtotal = sum(item.product.price * item.quantity for item in cart_items)
    shipping = Decimal('50.00')
    total = subtotal + shipping

    if request.method == "POST":
        payment = request.POST.get('payment_method')
        if payment == 'cod':
            order_items = []

            for cart_item in cart_items:
                if cart_item.product.quantity < cart_item.quantity:
                    messages.error(request, f"Sorry, Product  out of stock.")
                    return redirect('cart')

            with transaction.atomic():
                order = Order.objects.create(customer=request.user, total_amount=total, payment_option=payment)
                for cart_item in cart_items:
                    OrderItem.objects.create(order=order, product=cart_item.product, quantity=cart_item.quantity,
                                            product_price=cart_item.product.price)
                    Product.objects.filter(id=cart_item.product.id).update(quantity=F('quantity') - cart_item.quantity)
                    order_items.append({
                        'product_name': cart_item.product.Name,
                        'quantity': cart_item.quantity,
                        'product_price': cart_item.product.price,
                        'total_price': cart_item.product.price * cart_item.quantity,
                    })
            cart_items.delete()
            context = {
                'order_items': order_items,
                'subtotal': subtotal,
                'shipping': shipping,
                'total': total,
            }
            return render(request, 'userside/payment_success.html', context)
        else:
            return redirect('payment')

    context = {
        'items': cart_items,
        'address': address,
        'subtotal': subtotal,
        'shipping': shipping,
        'total': total,
    }
    return render(request, 'userside/checkout.html', context)


# razorpay view
# def payment(request):
#     cart_items = Cart.objects.filter(user=request.user)
#     subtotal = sum(item.product.price * item.quantity for item in cart_items)
#     shipping = Decimal('50.00')
#     total = subtotal + shipping
    
#     client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET_KEY))
#     razorpay_order = client.order.create({
#         'amount': int(total * 100),
#         'currency': 'INR',
#         'payment_capture': 1
#     })  
#     print(f"Subtotal: {subtotal}")
#     print(f"Total: {total}")     
#     context = {
#         'subtotal': subtotal,
#         'shipping': shipping,
#         'total': total,
#         'razorpay_order_id': razorpay_order['id'],
#         'razorpay_key': settings.RAZORPAY_API_KEY,
#     }  
#     return render(request, 'userside/payment.html', context)


from django.contrib import messages
@never_cache
def payment(request):
    cart_items = Cart.objects.filter(user=request.user)
    subtotal = sum(item.product.price * item.quantity for item in cart_items)
    shipping = Decimal('50.00')
    total = subtotal + shipping
    
    for cart_item in cart_items:
        if cart_item.product.quantity < cart_item.quantity:
            messages.error(request, f"Sorry, '{cart_item.product.Name}' is out of stock.")
            return redirect('cart')

    client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET_KEY))
    razorpay_order = client.order.create({
        'amount': int(total * 100),
        'currency': 'INR',
        'payment_capture': 1
    })  
    print(f"Subtotal: {subtotal}")
    print(f"Total: {total}")     
    context = {
        'subtotal': subtotal,
        'shipping': shipping,
        'total': total,
        'razorpay_order_id': razorpay_order['id'],
        'razorpay_key': settings.RAZORPAY_API_KEY,
    }  
    return render(request, 'userside/payment.html', context)


@csrf_exempt
def createorder(request):
    cart_items = Cart.objects.filter(user=request.user)
    subtotal = sum(item.product.price * item.quantity for item in cart_items)
    shipping = Decimal('50.00')
    total = subtotal + shipping

    order = Order.objects.create(customer=request.user, total_amount=total, payment_option='upi')

    order_items = []
    for cart_item in cart_items:
        OrderItem.objects.create(order=order, product=cart_item.product, quantity=cart_item.quantity,
                                    product_price=cart_item.product.price)
        product = Product.objects.get(id=cart_item.product.id)
        product.quantity -= cart_item.quantity
        product.save()

        order_items.append({
            'product_name': cart_item.product.Name,
            'quantity': cart_item.quantity,
            'product_price': cart_item.product.price,    
            # 'subtotal':cart_item.total_amount - shipping,       
        })

    cart_items.delete()  
    context = {
        'order_items': order_items,
        'total': total,
    }
    return render(request, 'userside/payment_success.html', context)

@csrf_exempt
def payment_success(request):  
   return render(request, "userside/payment_success.html")



# def payment_success(request):
#     order_items = request.context.get('order_items', [])
#     subtotal = request.context.get('subtotal', Decimal('0.00'))
#     shipping = request.context.get('shipping', Decimal('0.00'))
#     total = request.context.get('total', Decimal('0.00'))
#     context = {
#         'order_items': order_items,
#         'subtotal': subtotal,
#         'shipping': shipping,
#         'total': total,
#     }
#     return render(request, 'userside/payment_success.html', context)


@login_required
def orderaddress(request):
    user_addresses = request.user.addresses.all()  
    user = Customer.objects.get(email = request.user)
    cart_items = Cart.objects.filter(user=user)
    subtotal = sum(item.product.price * item.quantity for item in cart_items)
    shipping = Decimal('50.00')
    total = subtotal + shipping
    if request.method == 'POST':
        selected_address_id = request.POST.get('selected_address')
        if selected_address_id:
            selected_address = Address.objects.get(id=selected_address_id)
            request.user.selected_address = selected_address 
            request.user.save()
      
        con = {
            'items': cart_items,
            'address':selected_address,
            'subtotal': subtotal ,
            'shipping': shipping,
            'total': total,
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
        post = request.POST.get('PostalCode')
        if len(post) != 6 or len(set(post))== 1:
            messages.error(request, "Invalid zip code. Please enter a proper value.")
            return render(request, 'userside/ord_add_address.html')
        sav = Address.objects.create(customer=cus, address=address, city=city, postalcode=post )
        sav.save()
        return redirect('orderaddress') 
    return render(request,'userside/ord_add_address.html')



# order management of cod
def order_success(request, order_id):
    order = Order.objects.get(id=order_id)
    order_items = order.items.all() 
    context = {
        'order': order,
        'order_items': order_items,
    }
    return render(request, 'userside/ordermanage.html', context)


# cancel order and return order and wallet refund
# def cancelorder(request, order_id):
#     order = get_object_or_404(Order, id=order_id)

#     if not order.cancel:
#         order.cancel = True
#         order.save()

#         refund_amount = order.total_amount
#         refund_transaction = Transaction.objects.create(
#             user=request.user,
#             amount=refund_amount,
#             transaction_type='Refund',
#             transaction_balance=request.user.wallet.balance + refund_amount,  
#             related_order=order,
#         )

#         request.user.wallet.balance += refund_amount
#         request.user.wallet.save()

#     return redirect("userprofile")

# for cancelorder view
def cancelorder(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if not order.cancel:
        order.cancel = True
        order.save()

        refund_amount = order.total_amount
        refund_transaction = Transaction.objects.create(
            user=order.customer,
            amount=refund_amount,
            transaction_type='Refund',
            transaction_balance=order.customer.wallet.balance + refund_amount,
            related_order=order,
        )
        order.customer.wallet.balance += refund_amount
        order.customer.wallet.save()
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

# editing profile
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
    return render(request, 'userside/USER-PROF-EDIT.HTML', context)


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
        post = request.POST.get('editPostalCode')
        if len(post) != 6 or len(set(post))== 1:
            messages.error(request, "Invalid zip code. Please enter a proper value.")
            return render(request, 'userside/2userprofile.html')
        sav = Address.objects.create(customer=cus, address=address, city=city, postalcode=post)
        sav.save()
        return redirect('userprofile') 
    return render(request,'userside/2userprofile.html')


# editing address
# def edit_address(request, address_id):
#     address = get_object_or_404(Address, id=address_id)
#     if request.method == 'POST':
#         new_address = request.POST.get('editAddress')
#         new_city = request.POST.get('editCity')
#         new_postalcode = request.POST.get('editPostalCode')
#         if len(new_postalcode) != 6 or len(set(new_postalcode))== 1:

#                 messages.error(request, "Invalid zip code. Please enter a proper value.")
#                 return render(request, 'userside/userEditaddress.html')
#         address.address = new_address
#         address.city = new_city
#         address.postalcode = new_postalcode
#         address.save()

#         return redirect('viewaddress')
#     return render(request, 'userside/userEditaddress.html', {'address': address})

def edit_address(request, address_id):
    address = get_object_or_404(Address, id=address_id)

    if request.method == 'POST':
        new_address = request.POST.get('editAddress')
        new_city = request.POST.get('editCity')
        new_postalcode = request.POST.get('postalCode')

        # Check if 'editPostalCode' is not None
        if new_postalcode is not None:
            # Perform additional validation
            if len(new_postalcode) != 6 or len(set(new_postalcode)) == 1:
                messages.error(request, "Invalid zip code. Please enter a proper value.")
                return render(request, 'userside/userEditaddress.html', {'address': address})
           
            # Update the address fields and save
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
@login_required
def wallet(request):
    user = request.user
    userd = Customer.objects.get(email=user)
    transactions = Transaction.objects.filter(user=user).order_by('-timestamp')
    return render(request, 'userside/wallet.html', {'user': userd, 'transactions': transactions})

from xhtml2pdf import pisa
from io import BytesIO
def generate_invoice(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    context = {'order': order}
    invoice_html = render(request, 'userside/invoice.html', context).content

    
    pdf_file = BytesIO()
    pisa.CreatePDF(invoice_html, dest=pdf_file)

    response = HttpResponse(pdf_file.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=invoice_{order_id}.pdf'

    return response

# change password
# from django.contrib.auth.decorators import login_required
# from django.contrib import messages
# from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password

@login_required
def change_password(request):
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if not request.user.check_password(old_password):
            messages.error(request, 'Old password is incorrect.')
            return redirect('change_password')

        if new_password != confirm_password:
            messages.error(request, 'New password and confirm password do not match.')
            return redirect('change_password')

        request.user.password = make_password(new_password)
        request.user.save()

        messages.success(request, 'Password successfully changed.')
        return redirect('change_password')

    return render(request, 'userside/change_password.html')









