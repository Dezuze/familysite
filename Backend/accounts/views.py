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
    authentication_classes = []
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
                candidate = User.objects.filter(member__id=identifier).first()
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


from .models import InviteToken

class SignupView(APIView):
    authentication_classes = [] # Disable CSRF via SessionAuth for this endpoint
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data
        User = get_user_model()
        
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        invite_token_str = data.get('invite_token')

        if not (username and email and password and invite_token_str):
            return Response({"error": "Missing fields. Username, email, password, and invite_token are required."}, status=status.HTTP_400_BAD_REQUEST)

        # 1. Validate Token
        try:
            token_obj = InviteToken.objects.filter(token=invite_token_str, is_used=False).first()
            if not token_obj:
                return Response({"error": "Invalid or already used invite token."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
             return Response({"error": "Invalid token format."}, status=status.HTTP_400_BAD_REQUEST)

        # 2. Check Username
        if User.objects.filter(username=username).exists():
            return Response({"error": "Username taken."}, status=status.HTTP_400_BAD_REQUEST)

        # 3. Create User & Mark Token Used
        try:
            # We use the member pre-linked to the token if it exists
            member = token_obj.member
            
            user = User.objects.create_user(
                username=username, 
                email=email, 
                password=password,
                member=member
            )
            
            # Handle Avatar if provided
            avatar = request.FILES.get('avatar')
            if avatar and member:
                member.photo = avatar
                member.save()
            
            token_obj.is_used = True
            token_obj.save()
            
            # Log the user in to establish a session cookie for subsequent profile updates
            login(request, user)
            
            return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    def post(self, request):
        logout(request)
        return Response({"message": "Logged out"})


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)


class GenerateInviteTokenView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Ensure user is linked to a member
        if not hasattr(request.user, 'member') or not request.user.member:
            return Response({"error": "User must be linked to a Family Member to generate invites."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create a new token
        token_obj = InviteToken.objects.create(member=None) # member=None because anyone can use this token to sign up
        # We could also pre-link it if we wanted, but for general invites, member=None is fine
        # Or if the user wants to "sponsor" someone specifically, we'd need more logic.
        # For now, let's just generate a general token.
        
        return Response({"token": str(token_obj.token)}, status=status.HTTP_201_CREATED)


from django.middleware.csrf import get_token

class CsrfInitView(APIView):
    permission_classes = [AllowAny]

    @method_decorator(ensure_csrf_cookie)
    def get(self, request):
        return Response({"csrfToken": get_token(request)})
