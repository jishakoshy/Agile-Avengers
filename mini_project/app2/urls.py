from django.contrib import admin
from django.urls import path , include
from . import views
from django.conf.urls.static import static
from django.conf import settings
urlpatterns = [
    
# ADMIN SIDE...............................................:-
    path('admin_login/',views.Admin_login, name ='admin_login'),
    path('admin_dashboard/', views.Admin_dash, name='admin_dashboard'),
    path('log_out', views.Logout, name = 'log_out'),
    path('productview/', views.Productlist, name='productview'),

    # category management
    path('add_category/',views.Add_category, name ='add_category'),
    path('edit_category/<int:category_id>/', views.Edit_category, name='edit_category'),
    path('delete_category/<int:category_id>/', views.delete_category, name='delete_category'),
    
    # Sales Report
    path('sales_report/', views.Salesreport, name='sales_report'),
    path('generate_pdf/', views.generate_pdf, name='generate_pdf'),

    # product management
    path('addproduct/',views.Add_product, name ='addproduct'),
    path('admin_edit/<int:id>/', views.Admin_edit, name='admin_edit'),
    path('admin_delete/<int:id>/', views.Admin_delete, name='admin_delete'),
    
    # user_management
    path('user_management/', views.user_management, name='user_management'),
    path('block_user/<int:user_id>/', views.block_user, name='block_user'),
    path('unblock_user/<int:user_id>/', views.unblock_user, name='unblock_user'),

    # order management
    path('order-management/', views.order_management, name='order_management'),
    path('update_order_status/<int:order_id>/', views.update_order_status, name='update_order_status'),
     
    # inventory stock
    path('stock_list/', views.stock_list, name='stock_list'),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)