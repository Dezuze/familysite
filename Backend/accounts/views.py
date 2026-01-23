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


class SignupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data
        User = get_user_model()
        username = data.get('username')
        email = data.get('email')
        member_id = data.get('member_id')
        password = data.get('password')

        if not (username and email and member_id and password):
            return Response({"error": "missing fields"}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():
            return Response({"error": "username taken"}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(username=username, email=email, member_id=member_id, password=password)
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
