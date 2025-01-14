import re
import random
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from .models import OTP, TemporaryUser
from django.utils.timezone import now
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from datetime import timedelta
from django.conf import settings


# ================================
# 1. Password Validator for Users
# ================================
def validate_password(password):
    password_regex = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&#])[A-Za-z\d@$!%*?&#]{8,}$'
    return re.match(password_regex, password)


# ================================
# 2. Signup View for End User
# ================================
def end_user_signup(request):
    data1 = {'title': 'User Sign Up'}
    if request.method == 'POST':
        email = request.POST.get('email')

        # Check if the email exists in the User model
        if User.objects.filter(email=email).exists():
            messages.error(request, "User with this email already exists!")
            return redirect('end_user_signup')

        # Check if the email exists in the TemporaryUser model and if it is expired
        try:
            temp_user = TemporaryUser.objects.get(email=email)

            if temp_user.is_expired():  # If the temporary user data is expired
                temp_user.delete()  # Delete the expired temporary user
                OTP.objects.filter(email=email).delete()  # Delete the expired OTP
            else:##
                messages.error(request, "Temporary user with this email already exists. Please check your email for OTP.")
                return redirect('end_user_signup')

        except TemporaryUser.DoesNotExist:
            pass  # If no temporary user exists, proceed with signup

        # Extract other user info
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if not validate_password(password):
            messages.error(request, "Password must be at least 8 characters and include atleast one (uppercase, lowercase, numbers, and special characters).")
            return redirect('end_user_signup')

        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return redirect('end_user_signup')

        # Store temporary user details in the TemporaryUser model
        TemporaryUser.objects.create(
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password  # Ensure the password is hashed
        )

        otp = random.randint(100000, 999999)
        OTP.objects.update_or_create(
            email=email,
            defaults={'otp': otp, 'created_at': now()}
        )

        # Try sending OTP email
        try:
            send_mail(
                subject="Your OTP Verification Code",
                message=f"Your OTP Code is {otp}.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
            )
        except Exception as e:
            messages.error(request, f"Error sending OTP: {str(e)}")
            return redirect('end_user_signup')
##
        messages.success(request, "Account created! Please verify your email.")
        return redirect('otp_verification', email=email, source_page='end_user_signup')

    return render(request, 'signup_app/end_user_signup.html', data1)


# ================================
# 3. Signup View for Doctor
# ================================
def doctor_signup(request):
    data2 = {
        'title': 'Doctor Sign Up'
    }
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        doctor_id = request.POST['doctor_id']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        # Check if the email exists in the TemporaryUser model and if it is expired
        try:
            temp_user = TemporaryUser.objects.get(email=email)

            if temp_user.is_expired():  # If the temporary user data is expired
                temp_user.delete()  # Delete the expired temporary user
                OTP.objects.filter(email=email).delete()  # Delete the expired OTP
            else:##
                messages.error(request, "Temporary user with this email already exists. Please check your email for OTP.")
                return redirect('doctor_signup')

        except TemporaryUser.DoesNotExist:
            pass  # If no temporary user exists, proceed with signup

        if not validate_password(password):
            messages.error(request, "Password must be at least 8 characters and include atleast one (uppercase, lowercase, numbers, and special characters).")
            return redirect('doctor_signup')

        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return redirect('doctor_signup')

        if User.objects.filter(username=email).exists():
            messages.error(request, "User with this email already exists!")
            return redirect('doctor_signup')

        if len(doctor_id) < 6:
            messages.error(request, "Invalid Doctor ID!")
            return redirect('doctor_signup')

        # Store temporary user details in the TemporaryUser model
        TemporaryUser.objects.create(
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password,
            doctor_id=doctor_id
        )

        otp = random.randint(100000, 999999)
        OTP.objects.update_or_create(
            email=email,
            defaults={'otp': otp, 'created_at': now()}
        )

        try:
            send_mail(
                subject="Your OTP Verification Code",
                message=f"Your OTP Code is {otp}.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
            )
        except Exception as e:
            messages.error(request, f"Error sending OTP: {str(e)}")
            return redirect('doctor_signup')
##
        messages.success(request, "Account created! Please verify your email.")
        return redirect('otp_verification', email=email, source_page='doctor_signup')

    return render(request, 'signup_app/doctor_signup.html', data2)



# ================================
# 4. OTP Verification View
# ================================
def otp_verification(request, email, source_page):
    data = {'title': 'Verify OTP', 'email': email, 'source_page': source_page}

    if request.method == 'POST':
        otp_input = request.POST.get('otp')

        try:
            otp_entry = OTP.objects.get(email=email)

            # Check if OTP is expired
            if otp_entry.is_expired():
                messages.error(request, "OTP has expired. Please sign up again.")
                
                # Delete expired OTP and the corresponding TemporaryUser
                otp_entry.delete()
                TemporaryUser.objects.filter(email=email).delete()
                
                return redirect(source_page)

            # Validate OTP input
            if str(otp_entry.otp) == otp_input:
                temp_user = TemporaryUser.objects.get(email=email)

                # Create the final user account
                user = User.objects.create_user(
                    username=email,
                    email=email,
                    first_name=temp_user.first_name,
                    last_name=temp_user.last_name,
                    password=temp_user.password,
                    is_active=True
                )
                temp_user.delete()

                # Add user to the corresponding group
                group_name = 'specialuser' if source_page == 'doctor_signup' else 'regularuser'
                group, _ = Group.objects.get_or_create(name=group_name)
                group.user_set.add(user)

                otp_entry.delete()
                messages.success(request, "Account verified successfully! You can now sign in.")
                return redirect('login')
            else:
                messages.error(request, "Invalid OTP. Please try again.")
        except (OTP.DoesNotExist, TemporaryUser.DoesNotExist):
            messages.error(request, "OTP or user data not found. Please sign up again.")
            return redirect(source_page)

    return render(request, 'signup_app/otp_verification.html', data)


# ================================
# 5. Login View
# ================================
@csrf_protect
def login_view(request):
    data = {
        'title': 'User Login'
    }
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        # Use the authenticate function to verify email and password
        user = authenticate(request, username=email, password=password)

        if user:
            login(request, user)

            if user.groups.filter(name='regularuser').exists():
                return redirect('result_view')
            elif user.groups.filter(name='specialuser').exists():
                return redirect('Tool')
            else:
                messages.error(request, "You don't have the necessary permissions. Please sign in first or create an account if you don't have one already.")
                return redirect('login')
        else:
            messages.error(request, "Invalid email or password.")
            return redirect('login')

    return render(request, 'signup_app/login.html', data)


# ================================
# 6. Logout View
# ================================
@login_required
@csrf_protect
def logout_view(request):
    logout(request)
    messages.success(request, "You have been signed out.")
    return redirect('login')