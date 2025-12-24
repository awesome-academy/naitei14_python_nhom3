"""URL configuration for ecommerce project."""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),
    path('', include('myapp.urls')),  
    path('products/', include('products.urls')),  
    path('cart/', include('cart.urls')),  
    path('orders/', include('orders.urls')),  
    path('comments/', include('comments.urls')),  
]