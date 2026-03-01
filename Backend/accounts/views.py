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


from .models import InviteToken, ClaimToken

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
        token_obj = InviteToken.objects.create(member=None)
        
        return Response({"token": str(token_obj.token)}, status=status.HTTP_201_CREATED)


class GiveAccessView(APIView):
    """
    Guardian sets a username + password for a managed member.
    Creates a ClaimToken and a User account immediately.
    The managed member can then log in with the provided credentials.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        from families.models import FamilyMember
        
        profile_id = request.data.get('profile_id')
        username = request.data.get('username')
        password = request.data.get('password')

        if not all([profile_id, username, password]):
            return Response({"error": "profile_id, username, and password are required."}, status=400)

        # Validate the managed member
        try:
            profile = FamilyMember.objects.get(id=profile_id)
        except FamilyMember.DoesNotExist:
            return Response({"error": "Profile not found."}, status=404)

        # Check guardian permission
        if profile.created_by != request.user:
            return Response({"error": "You are not the guardian of this profile."}, status=403)
        if profile.is_independent:
            return Response({"error": "This profile is already independent."}, status=400)
        if hasattr(profile, 'user_account') and profile.user_account:
            return Response({"error": "This profile already has a user account."}, status=400)

        # Check username uniqueness
        User = get_user_model()
        if User.objects.filter(username=username).exists():
            return Response({"error": "Username already taken."}, status=400)

        # Create the User account for the profile
        user = User.objects.create_user(
            username=username,
            email=f"{username}@placeholder.local",  # Placeholder email, member can update later
            password=password,
            member=profile
        )

        # Create a ClaimToken record for tracking
        claim = ClaimToken.objects.create(
            profile=profile,
            username=username,
            temp_password="[set by guardian]",  # Don't store actual password
            created_by=request.user,
            is_claimed=True  # Already claimed since we created the user directly
        )

        return Response({
            "message": f"Account created for {profile.name}. They can now log in with username '{username}'.",
            "username": username,
            "profile_name": profile.name,
        }, status=201)


class ClaimAccountView(APIView):
    """
    A new member claims their profile via a claim token.
    They can optionally set a new password.
    """
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        token_str = request.data.get('token')
        new_password = request.data.get('new_password')

        if not token_str:
            return Response({"error": "Claim token is required."}, status=400)

        try:
            claim = ClaimToken.objects.get(token=token_str, is_claimed=False)
        except ClaimToken.DoesNotExist:
            return Response({"error": "Invalid or already claimed token."}, status=400)

        User = get_user_model()

        # Check if a user already exists for this profile
        if hasattr(claim.profile, 'user_account') and claim.profile.user_account:
            # Already has an account — just authenticate with temp credentials
            user = claim.profile.user_account
            if new_password:
                user.set_password(new_password)
                user.save()
        else:
            # Create user account
            user = User.objects.create_user(
                username=claim.username,
                email=f"{claim.username}@placeholder.local",
                password=new_password or claim.temp_password,
                member=claim.profile
            )

        claim.is_claimed = True
        claim.save()

        login(request, user)
        return Response(UserSerializer(user).data, status=200)


class GoIndependentView(APIView):
    """
    Authenticated user declares their profile independent.
    This revokes the guardian's write access.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        member = getattr(request.user, 'member', None)
        if not member:
            return Response({"error": "No linked profile found."}, status=400)

        if member.is_independent:
            return Response({"message": "Profile is already independent."}, status=200)

        member.is_independent = True
        member.save()

        return Response({
            "message": "Your profile is now independent. Your guardian can no longer edit your profile.",
            "is_independent": True
        }, status=200)


from django.middleware.csrf import get_token

class CsrfInitView(APIView):
    permission_classes = [AllowAny]

    @method_decorator(ensure_csrf_cookie)
    def get(self, request):
        return Response({"csrfToken": get_token(request)})
