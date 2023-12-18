from django.contrib import admin
from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.auth import  views as auth_views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    # USER SIDE------------------------------
    path('admin/', admin.site.urls  ),
    path('',views.Home, name ='home'),
    path('sign_up/', views.Sign_up, name = 'sign_up'),
    path('loginn/',views.loginn, name ='loginn'),
   
    path('logout', LogoutView.as_view(next_page = 'home'), name = 'logout'),
    # path('verify_otp/', views.verify_otp, name='verify_otp'),

        #forgot password
    # path('activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z](1,13)-[0-9A-Za-z](1,20))/',views.activate ),
    path('reset_password/', auth_views.PasswordResetView.as_view(),name='reset_password'),
    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(),name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(),name='password_reset_confirm'),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(),name='password_reset_complete'), 




    path('product_detail/<int:product_id>/',views.Product_detail, name = 'product_detail'),
    path('searchproduct/',views.search_products, name ='search_products'),
    
    # shop---------------------------------
    path('Shop/', views.Shop, name='Shop'),

    # checkout Page-------------------------
    path('checkout/', views.checkout_view, name='checkout'),
    path('orderaddress/', views.orderaddress, name='orderaddress'),
    path('order_address/', views.order_add_addre, name='order_address'),
    path('payment/', views.payment, name='payment'),

    # filter----------------------------------
    path('category/<int:category_id>/', views.category_filter, name='category_filter'),
    path('filter_products_by_price/', views.filter_products_by_price, name='filter_products_by_price'),

    # payment razor----------------------------
    path('payment_success', views.payment_success, name='payment_success'),
    path('createorder', views.createorder, name='createorder'),


    # order management-------------------------
    path('order/success/<int:order_id>/', views.order_success, name='order_success'),
    path('cancelorder/<int:order_id>/', views.cancelorder, name='cancelorder'),
    path('return_order/<int:order_id>/', views.return_order, name='returnorder'),

    #user profile ------------------------------
    path('userprofile/', views.userprofile, name='userprofile'),
    path('user_edit/', views.user_edit, name='user_edit'),
    path('add_addresses/', views.add_addresses, name='add_addresses'),

    path('edit_address/<int:address_id>/', views.edit_address, name='edit_address'),
    path('remove_address/<int:address_id>/', views.remove_address, name='remove_address'),
    path('viewaddress/', views.view_address, name='viewaddress'),
    path('change_password/',views.change_password, name = 'change_password'),

    #  user profile order list--------------------
    path('order/<int:order_id>/', views.view_order, name='view_order'),
    path('generate-invoice/<int:order_id>/', views.generate_invoice, name='generate_invoice'),

    # Wishlist------------------------------------
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('add-to-wishlist/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),

    # cart management-----------------------------
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart, name='cart'),
    path('remove_from_cart/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('update_quantity/<int:product_id>/<int:quantity>/', views.update_quantity, name='update_quantity'),
    path('product/quantity/<int:product_id>/<int:qty>/', views.get_product_quantity, name='get_product_quantity'),


    # wallet----------------------------------------
    path('wallet/', views.wallet, name='wallet_view'),
    # path('deposit_wallet/', views.deposit_wallet, name='deposit_wallet'),







  

]


