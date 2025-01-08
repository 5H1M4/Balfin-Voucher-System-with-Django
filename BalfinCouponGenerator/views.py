from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.http import HttpResponseRedirect
from django.urls import reverse
from datetime import timedelta, datetime
import barcode

from barcode import Code128 
from barcode.writer import ImageWriter
from io import BytesIO
import base64
from .models import Coupon
from .forms import CouponForm
import random 
import string
from django.http import JsonResponse

import json
from django.core.mail import EmailMessage
from django.views.decorators.csrf import csrf_exempt
import re
from PIL import Image






def dashboard (request):
                                    #remove from .orderby to sort from oldest coupon to newest
    coupons = Coupon.objects.all().order_by('-expiration_date')  # Replace 'expiration_date' with 'created_at' if needed
    return render(request, 'BalfinCouponGenerator/dashboard.html', {'coupons': coupons})

def home(request):
    return render (request, 'BalfinCouponGenerator/home.html')

def display_coupon(request):
    return render (request, 'BalfinCouponGenerator/display_coupon.html')

def generate_random_code(length=6):
    # Generate a random alphanumeric coupon code
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))


def generate_barcode(data):
    # Generate barcode in CODE128 format
    CODE128 = barcode.get_barcode_class('code128')
    barcode_img = CODE128(data, writer=ImageWriter())
    buffer = BytesIO()
    barcode_img.write(buffer)
    base64_img = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return base64_img


def create_coupon(request):
    if request.method == 'POST':
        amount = request.POST.get('amount')
        start_date = request.POST.get('startDate')

        # Convert start_date to a date object and calculate expiration date
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        expiration_date = start_date + timedelta(days=60)  # approx. 2 months

        # Generate a random code for the coupon
        coupon_code = generate_random_code()

        # Format barcode content with amount and coupon code
        #we can remove the famount to remove the price in the barcode generation image cause it is emebeded in the image of the barcode 
        #barcode_data = f"{amount:<5} - {coupon_code:<7}"
        barcode_data = f"{coupon_code:<7}"

        # Save the coupon details in the database
        coupon = Coupon.objects.create(
            amount=amount,
            expiration_date=expiration_date,
            barcode=coupon_code
        )

        # Generate the barcode image
        barcode_img = generate_barcode(barcode_data)

        # Pass amount, expiration date, and barcode to the template
        context = {
            'amount': amount,
            'expiration_date': expiration_date.strftime('%Y-%m-%d'),
            'barcode_img': barcode_img,
            'coupon_code': coupon_code
        }
        return render(request, 'BalfinCouponGenerator/display_coupon.html', context)
                                        #changed this line from create coupon to 
    return render(request, 'BalfinCouponGenerator/created_coupon.html')

    #added the new create coupon function along with the 
    #generate_random_code function added maybe a path is required?



def search_coupon(request):
    search_query = request.GET.get('query')
    coupon = None
    barcode_img = None  # Initialize barcode_img to avoid UnboundLocalError
    message = "Enter a coupon code to search."

    if search_query:
        # Check if a coupon with the specified code exists
        coupon = Coupon.objects.filter(barcode__icontains=search_query).first()
        
        if coupon:
            print("Success: Coupon found")  # Print success message if found
            message = "Success: Coupon found"
            barcode_img = generate_barcode(coupon.barcode)
        else:
            print("Coupon not found")  # Print message if not found
            message = "Coupon not found"
    
    # Add coupon details to context if coupon is found
    context = {
        'coupon': coupon,
        'search_query': search_query,
        'message': message,
        'amount': coupon.amount if coupon else None,
        'expiration_date': coupon.expiration_date.strftime('%Y-%m-%d') if coupon else None,
        'barcode_img': barcode_img,
    }
    return render(request, 'BalfinCouponGenerator/home.html', context)



#delete this activate if server not running
def activate_coupon(request):
    coupon_code = request.POST.get('coupon_code')  # Get the coupon code from the request
    
    print(f"Received coupon code: {coupon_code}")  # Debugging input
    
    if not coupon_code:
        print("No coupon code provided.")  # Debugging missing input
        return render(request, 'BalfinCouponGenerator/home.html', {'message': 'Please enter a coupon code.'})
    
    coupon = Coupon.objects.filter(barcode=coupon_code).first()

    if coupon:
        print(f"Coupon found: {coupon.barcode}, Active status: {coupon.is_active}")  # Debugging coupon lookup

        if not coupon.is_active:
            coupon.is_active = True
            coupon.save()
            print(f"Coupon {coupon.barcode} activated.")  # Debugging activation
            message = f"Coupon {coupon.barcode} has been activated and is ready for use."
        else:
            print(f"Coupon {coupon.barcode} is already active.")  # Debugging already active
            message = f"Coupon {coupon.barcode} is already active and ready for use."
    else:
        print(f"No coupon found with code: {coupon_code}")  # Debugging not found
        message = f"No coupon found with the code {coupon_code}."

    return render(request, 'BalfinCouponGenerator/home.html', {
        'message': message,
        #'coupon': coupon #this was the reason it was printing parameters
    })



#delete this below to take project to the first step 

def mark_coupon_as_used(request):
    if request.method == 'POST':
        barcode = request.POST.get('barcode')  # Get the barcode from the POST data
        print(f"Received barcode: {barcode}")  # Debugging line to see the received barcode

        if not barcode:
            print("Error: No barcode provided.")
            return JsonResponse({"message": "No barcode provided."}, status=400)

        try:
            # Find the coupon by barcode
            coupon = Coupon.objects.get(barcode=barcode)
            print(f"Coupon found: {coupon.barcode} - Active: {coupon.is_active}, Used: {coupon.is_used}")

            if coupon.is_active and not coupon.is_used:
                # Mark the coupon as used
                coupon.is_used = True
                coupon.save()
                print(f"Coupon {coupon.barcode} marked as used.")
                return JsonResponse({"message": f"Coupon {coupon.barcode} marked as used."}, status=200)
            
            elif coupon.is_used:
                # If the coupon is already used
                print(f"Coupon {coupon.barcode} has already been used.")
                return JsonResponse({"message": "Coupon has already been used."}, status=400)
            
            else:
                # If the coupon is not active
                print(f"Coupon {coupon.barcode} is not active.")
                return JsonResponse({"message": "Coupon is not active."}, status=400)

        except Coupon.DoesNotExist:
            # If the coupon doesn't exist
            print(f"Error: Coupon with barcode {barcode} not found.")
            return JsonResponse({"message": "Coupon not found."}, status=404)

    return JsonResponse({"message": "Invalid request method."}, status=405)

@csrf_exempt
def send_coupon_email(request):
    if request.method == 'POST':
        try:
            print("Received POST request to /send-coupon/")
            
            # Parse JSON data from request
            data = json.loads(request.body)
            recipient_email = data.get('email')
            screenshot_data = data.get('image')  # Look for 'image' key in JSON body
            
            print(f"Recipient email: {recipient_email}")
            print(f"Screenshot data (first 100 chars): {screenshot_data[:100]}...")  # Truncated log for readability

            # Validate email format
            if not re.match(r"[^@]+@[^@]+\.[^@]+", recipient_email):
                print("Invalid email format detected.")
                return JsonResponse({"message": "Invalid email address."}, status=400)

            # Check if screenshot data is present
            if not screenshot_data:
                print("Screenshot data is missing.")
                return JsonResponse({"message": "Coupon screenshot data is missing."}, status=400)

            # Decode the base64 image data and save it as a PNG
            image_data = base64.b64decode(screenshot_data.split(",")[1])  # Remove "data:image/png;base64,"
            screenshot_image = BytesIO(image_data)
            img = Image.open(screenshot_image)
            img_path = 'screenshot.png'
            img.save(img_path)
            print("Screenshot image successfully saved to disk.")

            # Configure email details
            email = EmailMessage(
                subject="Your Coupon",
                body="Here is your coupon screenshot.",
                from_email="dailydrivejaguar@gmail.com",
                to=[recipient_email]
            )
            email.attach("coupon_screenshot.png", image_data, "image/png")
            print(f"Email prepared to {recipient_email}")

            # Send email
            email.send(fail_silently=False)
            print("Email sent successfully.")
            return JsonResponse({"message": "Coupon sent successfully!"}, status=200)

        except Exception as e:
            print(f"Error in send_coupon_email: {str(e)}")  # Detailed error for debugging
            return JsonResponse({"message": "An error occurred while sending the coupon."}, status=500)

    print("Invalid request method used.")
    return JsonResponse({"message": "Invalid request method."}, status=405)


#def activate_coupon(request, coupon_id):
 #   coupon = get_object_or_404(Coupon, id=coupon_id)
  #  if not coupon.is_active:
   #     coupon.is_active = True
    #    coupon.save()
     #   message = f"Coupon {coupon.barcode} has been activated successfully."
    #else:
     #   message = f"Coupon {coupon.barcode} is already active."
    #return redirect('search_coupon')






