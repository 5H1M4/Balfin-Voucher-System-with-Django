"""
URL configuration for imgrec project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from BalfinCouponGenerator import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),  # Make the root URL point to the home view
    path('home/', include('BalfinCouponGenerator.urls')),  # Include other app URLs
    path('created-coupon/', views.create_coupon, name='create_coupon'),
    path('display-coupon/', views.display_coupon, name='display_coupon'), 
    path('search_coupon/', views.search_coupon, name='search_coupon'),
    path('dashboard/', views.dashboard, name='dashboard'), 
    #delete this line below to fix this problem 
    path('mark_coupon_as_used/<str:barcode>/', views.mark_coupon_as_used, name='mark_coupon_as_used'),
    path('send-coupon/', views.send_coupon_email, name='send_coupon_email'),
    #path('activate_coupon/<str:coupon_code>/', views.activate_coupon, name='activate_coupon'),
] 


