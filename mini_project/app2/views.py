from datetime import timedelta, timezone 
from imaplib import _Authenticator
from django.shortcuts import redirect, render, get_object_or_404
from main.models import *
from django.contrib.auth import login,authenticate
from django.contrib.auth import logout
from django.contrib import messages
from django.db.models import Q, Sum, Count, DateTimeField
from django.db.models.functions import TruncDate, TruncMonth, TruncYear
from datetime import date
from django.db.models.functions import TruncWeek
from django.views.decorators.cache import never_cache
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.http import HttpResponse

# Admin Side:--------------------------------------------

@never_cache
def Admin_login(request):
    if request.user.is_authenticated:
        return redirect('admin_dashboard')
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_staff:
                request.session['username'] = username
                login(request, user)
                return redirect('admin_dashboard')
            else:
                messages.error(request,"Login using user login!")
                return redirect('loginn')
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'adminside/admin-login.html')

@never_cache
@staff_member_required(login_url='admin_login')    
def Admin_dash(request):
    if request.user.is_authenticated:
        total_users = Customer.objects.count()
        total_orders = Order.objects.count()
        total_products = Product.objects.count()

        context = {
            'total_users': total_users,
            'total_orders': total_orders,
            'total_products': total_products,
        }

        return render(request, 'adminside/admindash.html', context)  
    return redirect('admin_login')


# admin logout
def Logout(request):
    if request.user.is_authenticated:
        logout(request)
    return redirect('admin_login') 

@never_cache
@staff_member_required(login_url='admin_login')
def Productlist(request):
    if request.method == 'POST':
        search_query = request.POST.get('search')
        products = Product.objects.filter(Q(Name__icontains=search_query) & ~Q(deleted=True))
    else:
        products = Product.objects.filter(deleted=False)
        # sizes = Size.objects.values('product').annotate(total_quantity=Sum('quantity'))
        # product_quantity_dict = {size['product']: size['total_quantity'] for size in sizes}
        # categories = Category.objects.all()
    
    return render(request, 'adminside/adminproductview.html', {'product': products})


# Category Management
@never_cache
@staff_member_required(login_url='admin_login')
def Add_category(request, category_id=None):
    category = None
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('discription')
        status = request.POST.get('status') == 'on'  
        existing_category = Category.objects.filter(Name=name)
        if existing_category.exists():
            error_message = "Category with this name already exists."
            return render(request, 'adminside/add_category.html', {'message': error_message})

        if category_id:
            category = get_object_or_404(Category, id=category_id)
        
        
        if category:
            category.Name = name
            category.description = description
            category.status = status
            category.save()
            messages.success(request, 'Category updated successfully.')
        else:
            Category.objects.create(Name=name, description=description, status=status)
            messages.success(request, 'Category added successfully.')
  
        return redirect('add_category')    
    categories = Category.objects.all()
    return render(request, 'adminside/add_category.html', {'categories': categories})

@never_cache
@staff_member_required(login_url='admin_login')
def Edit_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)

    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('discription')
        status = request.POST.get('status') == 'on'  

        category.Name = name
        category.description = description
        category.status = status
        category.save()

        messages.success(request, 'Category updated successfully.')
        return redirect('add_category')

    return render(request, 'adminside/adm_cate_edit.html', {'category': category})

@never_cache
@staff_member_required(login_url='admin_login')
def delete_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    category.delete()
    return redirect('add_category')

# product management::--
@never_cache
def Admin_edit(request, id):
    product = get_object_or_404(Product, id=id)
    categories = Category.objects.all()
    
    if request.method == 'POST':
        category_id = request.POST.get('category')
        selected_category_id = request.POST.get('category')
        category = Category.objects.get(id=selected_category_id)

        try:
            selected_category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            selected_category = None

        product.Name = request.POST['name']
        product.quantity = request.POST['quantity']

        try:
            price = float(request.POST['price'])
            if price < 0:
                raise ValueError("Price must be greater than or equal to zero.")
            quantity = int(request.POST['quantity'])
            if quantity < 0:
                raise ValueError("Quantity must be greater than or equal to zero.")
            if selected_category and selected_category.Name == 'Shoes':
                size = request.POST['size'] 
            else:
                size = None
            product.price = price
            product.quantity = quantity            
            if category.Name == 'Shoes' and size == 'None':
               size = 7

            product.size = size

        except ValueError as e:
            return render(request, 'adminside/admin_edit.html', {'editpro': product, 'cat': categories, 'error_message': str(e)})
        if selected_category:
            product.category = selected_category

        product.save()
        return redirect('productview')

    return render(request, 'adminside/admin_edit.html', {'editpro': product, 'cat': categories})



@staff_member_required(login_url='admin_login')
def Admin_delete(request,id):
    product = get_object_or_404(Product, id=id)
    product.deleted = True
    product.save()
    return redirect('productview')


# -------------------------------------------------------------------------------------

@never_cache
@staff_member_required(login_url='admin_login')
def Add_product(request):
    if request.method == 'POST':
        Name = request.POST['name']
        description = request.POST['discription']
        quantity = request.POST['quantity']
        price = request.POST['price']
        size = request.POST.get('size', None)
        is_varient= request.POST.get('varient')
        image = request.FILES['image']
        if is_varient == 'on':
            is_varient = True
        else:
            is_varient = False
        print("The value is",is_varient)
        if 'category' in request.POST:
            category_name = request.POST['category']
            try:
                category = Category.objects.get(Name=category_name)
            except Category.DoesNotExist:
                category = None
        else:
            category = None

        if int(price) <= 0:
            messages.error(request, 'enter price greater than zero')
        else:
            # Check if the product with the same name already exists
            existing_product = Product.objects.filter(Name=Name).first()

            
            product = Product.objects.create(Name=Name, description=description, price=price, image=image, category=category, size=size, quantity=quantity, is_varient= is_varient)
            # size_object = Size.objects.create(size=size, product=product, quantity=quantity)

            for file in request.FILES.getlist('subimages'):
                Subimage.objects.create(products=product, image=file)
            messages.success(request, 'product added Successfully')
    cat = Category.objects.all()
    return render(request, 'adminside/addproduct.html', {'category': cat})
# --------------------------------------------------------------------------------------------------

@never_cache
@staff_member_required(login_url='admin_login')
def order_management(request):
    order = Order.objects.all().order_by('-order_date')
    return render(request, 'adminside/admin_orderstatus.html', {'order': order})


from decimal import Decimal
from django.db import transaction

def update_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status == 'Reject':
            if not order.cancel:
                order.status = new_status
                order.cancel = True
                order.save()

                if order.payment_option == 'upi':
                    with transaction.atomic():
                        wallet, created = Wallet.objects.select_for_update().get_or_create(user=order.customer)
                        wallet.balance = Decimal(str(wallet.balance))
                        refund_amount = Decimal(str(order.total_amount))
                        refund_transaction = Transaction.objects.create(
                            user=order.customer,
                            amount=refund_amount,
                            transaction_type='Refund',
                            transaction_balance=wallet.balance + refund_amount,
                            related_order=order,
                        )
                        wallet.balance += refund_amount
                        wallet.balance = float(wallet.balance)  
                        wallet.save()
        else:
            order.status = new_status
            order.save()
    return redirect('order_management')


# inventory stock---------------
@staff_member_required(login_url='admin_login')
def stock_list(request):
    product = Product.objects.filter(deleted=False)
    return render(request, 'adminside/admin_inventory.html', {'product':product})


# user management---------------  
@staff_member_required(login_url='admin_login')
def user_management(request):
    users = Customer.objects.filter(is_staff=False)
    return render(request, 'adminside/admin_user_manage.html', {'users': users})


def block_user(request, user_id):
    user = Customer.objects.get(pk=user_id)
    user.is_active = False
    user.save()
    messages.success(request, f'User {user.first_name} {user.last_name} has been blocked.')
    return redirect('user_management')


def unblock_user(request, user_id):
    user = Customer.objects.get(pk=user_id)
    user.is_active = True
    user.save()
    messages.success(request, f'User {user.first_name} {user.last_name} has been unblocked.')
    return redirect('user_management')




# sales pdf
def generate_pdf(request):
    template_path = 'adminside/sales_report_pdf.html'

    orders = Order.objects.all()
    order_items = OrderItem.objects.select_related('product').all()
    customers = Customer.objects.all()

    context = {
        'orders': orders,
        'order_items': order_items,
        'customers': customers,
    }

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="sales_report.pdf"'

    template = get_template(template_path)
    html = template.render(context)
    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('Error creating PDF', content_type='text/plain')
    return response


def Salesreport(request):
    current_orders = Order.objects.all()
    time_range = request.GET.get('time_range', 'daily')
    daily_sales_data = []
    weekly_sales_data = []
    monthly_sales_data = []
    yearly_sales_data = []
    formatted_dates = [] 
    total_amounts = []
    total_weekly_sales = []
    formatted_weeks = []
    total_monthly_sales = []
    formatted_months = []
    sales_count =[]
    formatted_years = []
    total_yearly_sales = []
    
    if time_range == 'daily':
        daily_sales_data = Order.objects.annotate(
            order_date_day=TruncDate('order_date')
        ).values('order_date_day').annotate(
            total_sales=Sum('items__product_price'),
            sales_count=Count('id')
        ).order_by('order_date_day')

        formatted_dates = [entry['order_date_day'].strftime('%d-%B') for entry in daily_sales_data]
        # formatted_dates = [
        #     entry['order_date_day'].strftime('%d-%B') if entry['order_date_day'] is not None else 'N/A'
        #     for entry in daily_sales_data
        # ]

        sales_count = [entry['sales_count'] for entry in daily_sales_data]
        total_amounts = [float(entry['total_sales']) if entry['total_sales'] is not None else 0.0 for entry in daily_sales_data]

    elif time_range == 'weekly':
        weekly_sales_data = Order.objects.annotate(
            order_date_week=TruncWeek('order_date')
        ).values('order_date_week').annotate(
            total_sales=Sum('items__product_price'),
            sales_count=Count('id')
        ).order_by('order_date_week')

        formatted_weeks = [date(entry['order_date_week'].year, entry['order_date_week'].month, entry['order_date_week'].day).strftime('%d-%B') for entry in weekly_sales_data]
        total_weekly_sales = [float(entry['total_sales']) for entry in weekly_sales_data]

    elif time_range == 'monthly':
        monthly_sales_data = Order.objects.annotate(
            order_date_month=TruncMonth('order_date')
        ).values('order_date_month').annotate(
            total_sales=Sum('items__product_price'),
            sales_count=Count('id')
        ).order_by('order_date_month')

        formatted_months = [date(entry['order_date_month'].year, entry['order_date_month'].month, 1).strftime('%d-%B') for entry in monthly_sales_data]
        total_monthly_sales = [float(entry['total_sales']) for entry in monthly_sales_data]

    elif time_range == 'yearly':
        yearly_sales_data = Order.objects.annotate(
            order_date_year=TruncYear('order_date', output_field=DateTimeField())
        ).values('order_date_year').annotate(
            total_sales=Sum('items__product_price')
        ).order_by('order_date_year')

        formatted_years = [entry['order_date_year'].strftime('%Y') for entry in yearly_sales_data]
        total_yearly_sales = [float(entry['total_sales']) for entry in yearly_sales_data]
    
    # order = Order.objects.create(customer=request.user,total_amount=total,payment_option=payment_method)

    context = {
        # "payment_method": order.payment_method,
        "daily_sales_data": daily_sales_data,
        "weekly_sales_data": weekly_sales_data,
        "monthly_sales_data": monthly_sales_data,
        "yearly_sales_data": yearly_sales_data,
        "current_orders": current_orders,
        "dates": formatted_dates,
        "total_amounts": total_amounts,
        "total_weekly_sales": total_weekly_sales,
        "formatted_weeks": formatted_weeks,
        "total_monthly_sales": total_monthly_sales,
        "formatted_months": formatted_months,
        "sales_count": sales_count,
        "current_orders": current_orders,
        "formatted_years": formatted_years,
        "total_yearly_sales": total_yearly_sales,
        "time_range": time_range  
    }

    return render(request, 'adminside/sales_report.html', context)
