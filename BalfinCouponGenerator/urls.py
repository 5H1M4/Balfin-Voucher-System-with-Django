from django.urls import path
from . import views  # Import views from the same directory
from django.conf import settings
from django.conf.urls.static import static



urlpatterns = [
    #if error happening bring back the path with home views
    #path('home/', views.home, name='home'),        # Home page URL
    path('created-coupon/', views.create_coupon, name='create_coupon'),
    path('display-coupon/', views.display_coupon, name='display_coupon'), 
    path('dashboard/', views.dashboard, name='dashboard'),
    #delete the line below along with the view and functionality in the html if server not running
    path('activate-coupon/', views.activate_coupon, name='activate_coupon'),

    #path('activate_coupon/<str:coupon_code>/', views.activate_coupon, name='activate_coupon'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
