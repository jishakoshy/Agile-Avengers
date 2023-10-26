from django.contrib import admin
from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    # user side:-
    path('',views.Home, name ='home'),
    path('sign_up/', views.Sign_up, name = 'sign_up'),
    path('loginn/',views.loginn, name ='loginn'),
    path('signout/', views.signout, name='signout'),
    # path('otp-verification/', views.otp_verification, name='otp_verification'),
    # path('resend-otp/', views.resend_otp, name='resend_otp'),
    path('product_detail/<int:product_id>/',views.Product_detail, name = 'product_detail'),
    path('searchproduct/',views.search_products, name ='search_products'),
    
    # admin side:-
    path('admin_login/',views.Admin_login, name ='admin_login'),
    path('admin_dashboard/', views.Admin_dash, name='admin_dashboard'),
    path('productview/', views.Productlist, name='productview'),
    path('add_category/',views.Add_category, name ='add_category'),
    path('addproduct/',views.Add_product, name ='addproduct'),
    path('admin_edit/<int:id>/', views.Admin_edit, name='admin_edit'),
    path('admin_delete/<int:id>/', views.Admin_delete, name='admin_delete'),
    
    # user_management
    path('user_management/', views.user_management, name='user_management'),
    path('block_user/<int:user_id>/', views.block_user, name='block_user'),
    path('unblock_user/<int:user_id>/', views.unblock_user, name='unblock_user'),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)


