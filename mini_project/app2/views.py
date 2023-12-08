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
from django.contrib.admin.views.decorators import staff_member_required
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.http import HttpResponse

# Admin Side:--------------------------------------------
# @staff_member_required(login_url='admin_login') 
# def Admin_login(request):
#     if request.method == 'POST':
#         username = request.POST['username']
#         password = request.POST['password']
#         user = authenticate(username=username, password=password)
#         if user is not None:
#             if user.is_staff:
#                 request.session['username'] = username
#                 login(request, user)
#                 return redirect('admin_dashboard')
#             else:
#                 messages.error(request,"Login using user login!")
#                 return redirect('loginn')
#         else:
#             messages.error(request, 'Invalid username or password')
#     return render(request, 'adminside/admin-login.html')

# @staff_member_required(login_url='admin_login')      
# def Admin_dash(request):
#         return render(request, 'adminside/admindash.html')

def Admin_login(request):
    if request.user.is_authenticated:
        return redirect('admin_dashboard')
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = _Authenticator(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('admin_dashboard')
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'adminside/admin-login.html')
        
     
def Admin_dash(request):
     if request.user.is_authenticated:
        return render(request, 'adminside/admindash.html')
     return redirect('admin_login')

# admin logout
def Logout(request):
    if request.user.is_authenticated:
        logout(request)
    return redirect('admin_login') 


# @staff_member_required(login_url='admin_login')  
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

def Add_category(request, category_id=None):
    category = None
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('discription')
        status = request.POST.get('status') == 'on'  # Assuming status is a checkbox in the form

        existing_category = Category.objects.filter(Name=name)
        if existing_category.exists():
            error_message = "Category with this name already exists."
            return render(request, 'adminside/add_category.html', {'error_message': error_message})

        if category_id:
            category = get_object_or_404(Category, id=category_id)
        
        
        if category:
            # Editing an existing category
            category.Name = name
            category.description = description
            category.status = status
            category.save()
            messages.success(request, 'Category updated successfully.')
        else:
            # Adding a new category
            Category.objects.create(Name=name, description=description, status=status)
            messages.success(request, 'Category added successfully.')
  
        return redirect('add_category')    
    categories = Category.objects.all()
    return render(request, 'adminside/add_category.html', {'categories': categories})


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

def delete_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    category.soft_delete()
    return redirect('add_category')

# product management::--

# def Admin_edit(request,id):
#     product = Product.objects.get(id=id)
#     category = Category.objects.all()
#     productCat = product.category

#     if request.method == 'POST':
#         category_name = request.POST.get('category')
        
#         try:
#             category = Category.objects.get(id=category_name)
#             # product.category = category
#             product = Product.objects.get(id=id)
#         except Category.DoesNotExist:
#             pass

#         product.Name = request.POST['name']
#         product.quantity = request.POST['quantity']
#         product.price = request.POST['price']

#         product.save()
#         return redirect('productview')
    
#     return render(request,'admin_edit.html',{'editpro':product,'cat': category,'prodcat':productCat})   
def Admin_edit(request, id):
    product = get_object_or_404(Product, id=id)
    categories = Category.objects.all()

    if request.method == 'POST':
        category_id = request.POST.get('category')

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
            product.price = price
            product.quantity = quantity
        except ValueError as e:
            return render(request, 'adminside/admin_edit.html', {'editpro': product, 'cat': categories, 'error_message': str(e)})

        if selected_category:
            product.category = selected_category

        product.save()
        return redirect('productview')

    return render(request, 'adminside/admin_edit.html', {'editpro': product, 'cat': categories})


def Admin_delete(request,id):
    product = get_object_or_404(Product, id=id)
    product.deleted = True
    product.save()
    return redirect('productview')

# def Add_product(request):
#     if request.method == 'POST':
#         Name = request.POST['name']
#         description = request.POST['discription']
#         quantity = request.POST['quantity']
#         price = request.POST['price']
#         size = request.POST['size']
#         image = request.FILES['image']
#         if 'category' in request.POST:
#             category_name = request.POST['category']
#             try:
#                 category = Category.objects.get(Name=category_name)
#             except Category.DoesNotExist:
#                 category = None
        
#         else:
            
#             category = None
#         if int(price) <= 0:
#             messages.error(request, 'enter price greater than zero')
#         else:

#             product = Product.objects.create(Name = Name, description = description , price =price, image= image , category = category)
#             size = Size.objects.create(size= size, product = product, quantity= quantity)

#             for file in request.FILES.getlist('subimages'):
#                 Subimage.objects.create(products = product, image = file )
#             messages.success(request, 'product added Sucessfully')
    
#     cat = Category.objects.all()
#     return render(request,'adminside/addproduct.html', {'category' : cat})

# -------------------------------------------------------------------------------------
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

            # if existing_product:
            #     # If the product exists, update its quantity
            #     size_object, created = Size.objects.get_or_create(product=existing_product, size=size)
            #     if created:
            #         size_object.quantity = int(quantity)
            #     else:
            #         size_object.quantity += int(quantity)
            #     size_object.save()

            # else:
                # If the product does not exist, create a new product
            product = Product.objects.create(Name=Name, description=description, price=price, image=image, category=category, size=size, quantity=quantity, is_varient= is_varient)
            # size_object = Size.objects.create(size=size, product=product, quantity=quantity)

            for file in request.FILES.getlist('subimages'):
                Subimage.objects.create(products=product, image=file)
            messages.success(request, 'product added Successfully')
    cat = Category.objects.all()
    return render(request, 'adminside/addproduct.html', {'category': cat})
# --------------------------------------------------------------------------------------------------



# def Add_product(request):
#     if request.method == 'POST':
#         # Retrieve the crop coordinates and dimensions
#         x = request.POST.get('x')
#         y = request.POST.get('y')
#         width = request.POST.get('width')
#         height = request.POST.get('height')


#         Name = request.POST['name']
#         description = request.POST['discription']
#         quantity = request.POST['quantity']
#         price = request.POST['price']
#         size = request.POST.get('size', None)
#         is_varient = request.POST.get('varient')
#         image = request.FILES['image']
#         if is_varient == 'on':
#             is_varient = True
#         else:
#             is_varient = False

#         if 'category' in request.POST:
#             category_name = request.POST['category']
#             try:
#                 category = Category.objects.get(Name=category_name)
#             except Category.DoesNotExist:
#                 category = None
#         else:
#             category = None

#         # Perform image cropping and save the product
#         product = Product.objects.create(
#             Name=Name,
#             description=description,
#             price=price,
#             image=image,  
#             category=category,
#             size=size,
#             quantity=quantity,
#             is_varient=is_varient
#         )

#         # Perform image cropping and save the product
#         # You need to install the Pillow library for image processing
#         from PIL import Image

#         # Open the original image using Pillow
#         img = Image.open(product.image.path)

#         # Crop the image based on the provided coordinates and dimensions
#         cropped_img = img.crop((int(x), int(y), int(x) + int(width), int(y) + int(height)))

#         # Save the cropped image
#         cropped_img.save(product.image.path)

#         # Process and save sub-images if needed
#         for file in request.FILES.getlist('subimages'):
#             Subimage.objects.create(products=product, image=file)

#         messages.success(request, 'Product added successfully')

#         # Redirect to the product detail page or another appropriate page
#         return redirect('product_detail', product_id=product.id)

#     # If the request method is not POST, render the form
#     cat = Category.objects.all()
#     return render(request, 'adminside/addproduct.html', {'category': cat})


# order management and update status
def order_management(request):
    order = Order.objects.all()
    return render(request, 'adminside/admin_orderstatus.html',{'order': order})
def update_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        order.status = new_status
        order.save()

    return redirect('order_management')

# def update_order_status(request, order_id):
#     order = get_object_or_404(Order, id=order_id)

#     if request.method == 'POST':
#         new_status = request.POST.get('status')

#         if new_status == 'Delivered':
#             order.status = new_status
#             order.delivered = True  
#             order.save()
#         else:
#             order.status = new_status
#             order.save()

#     return redirect('order_management')





# inventory stock
def stock_list(request):
    product = Product.objects.all()
    return render(request, 'adminside/admin_inventory.html', {'product':product})


# user management
def user_management(request):
    users = Customer.objects.all()
    return render(request, 'adminside/admin_user_manage.html', {'users': users})

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




# sales pdf
def generate_pdf(request):
    template_path = 'adminside/sales_report_pdf.html'

    # Get relevant data from your models
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
    
    
    # Daily Sales Data
    if time_range == 'daily':
        daily_sales_data = Order.objects.annotate(
            order_date_day=TruncDate('order_date')
        ).values('order_date_day').annotate(
            total_sales=Sum('items__product_price'),
            sales_count=Count('id')
        ).order_by('order_date_day')

        formatted_dates = [entry['order_date_day'].strftime('%d-%B') for entry in daily_sales_data]
        sales_count = [entry['sales_count'] for entry in daily_sales_data]
        total_amounts = [float(entry['total_sales']) if entry['total_sales'] is not None else 0.0 for entry in daily_sales_data]

    # Weekly Sales Data
    elif time_range == 'weekly':
        weekly_sales_data = Order.objects.annotate(
            order_date_week=TruncWeek('order_date')
        ).values('order_date_week').annotate(
            total_sales=Sum('items__product_price'),
            sales_count=Count('id')
        ).order_by('order_date_week')

        formatted_weeks = [date(entry['order_date_week'].year, entry['order_date_week'].month, entry['order_date_week'].day).strftime('%d-%B') for entry in weekly_sales_data]
        total_weekly_sales = [float(entry['total_sales']) for entry in weekly_sales_data]

    # Monthly Sales Data
    elif time_range == 'monthly':
        monthly_sales_data = Order.objects.annotate(
            order_date_month=TruncMonth('order_date')
        ).values('order_date_month').annotate(
            total_sales=Sum('items__product_price'),
            sales_count=Count('id')
        ).order_by('order_date_month')

        formatted_months = [date(entry['order_date_month'].year, entry['order_date_month'].month, 1).strftime('%d-%B') for entry in monthly_sales_data]
        total_monthly_sales = [float(entry['total_sales']) for entry in monthly_sales_data]

    # Yearly Sales Data
    elif time_range == 'yearly':
        yearly_sales_data = Order.objects.annotate(
            order_date_year=TruncYear('order_date', output_field=DateTimeField())
        ).values('order_date_year').annotate(
            total_sales=Sum('items__product_price')
        ).order_by('order_date_year')

        formatted_years = [entry['order_date_year'].strftime('%Y') for entry in yearly_sales_data]
        total_yearly_sales = [float(entry['total_sales']) for entry in yearly_sales_data]

    context = {
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
