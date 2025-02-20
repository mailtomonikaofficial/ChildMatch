from django.urls import path
from .views import RegisterView, LoginView,LogoutView, ChangePasswordView,ForgotPasswordView, ResetPasswordView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
     path('changepassword/', ChangePasswordView.as_view(), name='changepassword'),
    path('forgotpassword/', ForgotPasswordView.as_view(), name='forgotpassword'),
    path('resetpassword/', ResetPasswordView.as_view(), name='resetpassword'),
    
]

