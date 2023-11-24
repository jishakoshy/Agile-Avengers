from datetime import timedelta, timezone
from imaplib import _Authenticator
from django.shortcuts import redirect, render, get_object_or_404
from main.models import *
from django.contrib.auth import login
from django.contrib.auth import logout
from django.contrib import messages
from django.db.models import Q, Sum

# Admin Side:--------------------------------------------
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
        # Handle form submission for editing
        name = request.POST.get('name')
        description = request.POST.get('discription')
        status = request.POST.get('status') == 'on'  # Assuming status is a checkbox in the form

        # Update category fields
        category.Name = name
        category.description = description
        category.status = status
        category.save()

        messages.success(request, 'Category updated successfully.')
        return redirect('add_category')

    return render(request, 'adminside/adm_cate_edit.html', {'category': category})


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


def Add_product(request):
    if request.method == 'POST':
        Name = request.POST['name']
        description = request.POST['discription']
        quantity = request.POST['quantity']
        price = request.POST['price']
        size = request.POST.get('size', None)
        image = request.FILES['image']
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

            if existing_product:
                # If the product exists, update its quantity
                size_object, created = Size.objects.get_or_create(product=existing_product, size=size)
                if created:
                    size_object.quantity = int(quantity)
                else:
                    size_object.quantity += int(quantity)
                size_object.save()

            else:
                # If the product does not exist, create a new product
                product = Product.objects.create(Name=Name, description=description, price=price, image=image, category=category)
                size_object = Size.objects.create(size=size, product=product, quantity=quantity)

                for file in request.FILES.getlist('subimages'):
                    Subimage.objects.create(products=product, image=file)

                messages.success(request, 'product added Successfully')

    cat = Category.objects.all()
    return render(request, 'adminside/addproduct.html', {'category': cat})



# order management
def order_management(request):
    order = Order.objects.all()
    return render(request, 'adminside/admin_orderstatus.html',{'order': order})

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


class DashboardView():
    def get(self, request, *args, **kwargs):
        # Get daily sales data
        today = timezone.now().date()
        daily_sales = Sale.objects.filter(date=today).count()

        # Get weekly sales data
        start_of_week = today - timedelta(days=today.weekday())
        weekly_sales = Sale.objects.filter(date__gte=start_of_week).count()

        # Get yearly sales data
        start_of_year = today.replace(month=1, day=1)
        yearly_sales = Sale.objects.filter(date__gte=start_of_year).count()

        context = {
            'daily_sales': daily_sales,
            'weekly_sales': weekly_sales,
            'yearly_sales': yearly_sales,
        }

        return render(request, 'admindash.html', context)