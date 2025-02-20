from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate, login
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from .serializers import UserRegistrationSerializer, UserLoginSerializer, ChangePasswordSerializer, ForgotPasswordSerializer,ResetPasswordSerializer

from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import logout
import uuid




User = get_user_model()
PASSWORD_RESET_TOKENS = {}

@method_decorator(csrf_exempt, name='dispatch')
class RegisterView(APIView):
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()  # This calls the create() method
            return Response({"message": "User registered successfully!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            identifier = serializer.validated_data.get("identifier")
            password = serializer.validated_data.get("password")

            # Attempt to fetch the user by email first, then by phone number.
            try:
                user = User.objects.get(email=identifier)
            except User.DoesNotExist:
                try:
                    user = User.objects.get(phone_number=identifier)
                except User.DoesNotExist:
                    return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)

            # Since you've set USERNAME_FIELD to 'email', use email for authentication.
            user = authenticate(request, email=user.email, password=password)

            if user is not None:
                login(request, user)
                return Response({"message": "Login successful!"}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # Logout View remains the same
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response({"message": "Logged out successfully."}, status=status.HTTP_200_OK)

# Change Password View with confirm_password


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]
    
    # Warning: This change-password endpoint does not verify the old password.
    # Use with caution.
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            new_password = serializer.validated_data.get("new_password")
            user.set_password(new_password)
            user.save()
            return Response({"message": "Password changed successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ForgotPasswordView(APIView):
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response({"error": "User with this email does not exist."}, status=status.HTTP_400_BAD_REQUEST)
            
            token = str(uuid.uuid4())
            PASSWORD_RESET_TOKENS[token] = user.id
            
            # In production, send the token via email.
            return Response({"message": "Password reset token generated.", "token": token}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ResetPasswordView(APIView):
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            token = serializer.validated_data["token"]
            if token not in PASSWORD_RESET_TOKENS:
                return Response({"error": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)
            
            user_id = PASSWORD_RESET_TOKENS[token]
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return Response({"error": "User does not exist."}, status=status.HTTP_400_BAD_REQUEST)
            
            new_password = serializer.validated_data["new_password"]
            user.set_password(new_password)
            user.save()
            
            # Remove the token once it is used
            del PASSWORD_RESET_TOKENS[token]
            
            return Response({"message": "Password reset successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# (Existing views: RegisterView, LoginView, LogoutView, ChangePasswordView would be defined here)