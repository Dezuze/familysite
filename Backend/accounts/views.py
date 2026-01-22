from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
import logging
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import UserSerializer


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        identifier = request.data.get("identifier")
        password = request.data.get("password")

        User = get_user_model()
        logger = logging.getLogger(__name__)

        # Try authenticating directly (identifier as username)
        user = authenticate(username=identifier, password=password)

        # If that fails, try resolving identifier as email or member_id
        if not user and identifier:
            try:
                # Try email
                candidate = User.objects.filter(email__iexact=identifier).first()
                if candidate:
                    user = authenticate(username=candidate.username, password=password)
            except Exception:
                user = None

        if not user and identifier:
            try:
                # Try member_id
                candidate = User.objects.filter(member_id=identifier).first()
                if candidate:
                    user = authenticate(username=candidate.username, password=password)
            except Exception:
                user = None

        if not user:
            logger.info("Login failed for identifier=%s", identifier)
            return Response({"error": "Invalid credentials"}, status=400)

        login(request, user)
        logger.info("Login success for user=%s", user.username)
        return Response(UserSerializer(user).data)


from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

class SignupView(APIView):
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request):
        data = request.data
        User = get_user_model()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        sponsor_id = data.get('sponsor_id')
        avatar = data.get('avatar')

        if not (username and email and password and sponsor_id):
            return Response({"error": "missing fields (sponsor_id required)"}, status=status.HTTP_400_BAD_REQUEST)

        # Validate Sponsor
        if not User.objects.filter(member_id=sponsor_id).exists():
             return Response({"error": "Invalid Sponsor ID"}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():
            return Response({"error": "username taken"}, status=status.HTTP_400_BAD_REQUEST)

        # Generate new Member ID
        import random
        new_member_id = f"MEM{random.randint(10000, 99999)}"
        while User.objects.filter(member_id=new_member_id).exists():
             new_member_id = f"MEM{random.randint(10000, 99999)}"

        user = User.objects.create_user(username=username, email=email, member_id=new_member_id, password=password)
        
        # Handle Avatar
        if avatar:
            user.avatar = avatar
            user.save()

        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


class LogoutView(APIView):
    def post(self, request):
        logout(request)
        return Response({"message": "Logged out"})


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)


class CsrfInitView(APIView):
    permission_classes = [AllowAny]

    @method_decorator(ensure_csrf_cookie)
    def get(self, request):
        return Response({"detail": "ok"})
