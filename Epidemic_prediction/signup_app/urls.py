from django.urls import path
from . import views

urlpatterns = [
    # User Signup Views
    path('signup/', views.login_view, name='login'), #End_user signup
    path('signup/end_user/', views.end_user_signup, name='end_user_signup'), #End_user signup
    path('signup/doctor/', views.doctor_signup, name='doctor_signup'), #doctor signup

    # OTP Verification View
    path('verify-otp/<str:email>/<str:source_page>/', views.otp_verification, name='otp_verification'),

    # Login and Logout Views
    path('login/', views.login_view, name='login'),  #user login
    path('logout/', views.logout_view, name='logout'),  #user logout
]