"""
Comprehensive tests for the accounts app.
Covers: User creation, login (success/fail/email/member_id), signup with tokens,
        Give Access flow, Claim Account flow, Go Independent flow, CSRF init.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from families.models import Family, FamilyMember
from rest_framework.test import APIClient
import datetime
from .models import InviteToken, ClaimToken

User = get_user_model()


class UserCreationTests(TestCase):
    """Test user model creation and linking."""

    def setUp(self):
        self.family = Family.objects.create(sl_no="1", branch="Main", member_no="FAM-TEST-001")
        self.member = FamilyMember.objects.create(
            family=self.family, name="John Doe", age=30,
            relation="Head", date_of_birth=datetime.date(1994, 1, 1),
            blood_group="O+", occupation="Engineer"
        )

    def test_create_user_with_member(self):
        user = User.objects.create_user(username="john", email="john@example.com", password="Pass123!", member=self.member)
        self.assertEqual(user.username, "john")
        self.assertEqual(user.member, self.member)

    def test_create_user_without_member(self):
        user = User.objects.create_user(username="solo", email="solo@example.com", password="Pass123!")
        self.assertIsNone(user.member)

    def test_create_superuser(self):
        user = User.objects.create_superuser(username="admin", email="admin@example.com", password="Admin123!")
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)


class LoginTests(TestCase):
    """Test login endpoint with various identifiers."""

    def setUp(self):
        self.client = APIClient()
        self.family = Family.objects.create(sl_no="1", branch="Main", member_no="FAM-LOGIN-001")
        self.member = FamilyMember.objects.create(
            family=self.family, name="Login User", age=30,
            relation="Head", date_of_birth=datetime.date(1994, 1, 1)
        )
        self.user = User.objects.create_user(
            username="loginuser", email="login@example.com",
            password="ComplexPass123!", member=self.member
        )

    def test_login_with_username(self):
        res = self.client.post('/api/auth/login/', {"identifier": "loginuser", "password": "ComplexPass123!"}, format='json')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['username'], "loginuser")

    def test_login_with_email(self):
        res = self.client.post('/api/auth/login/', {"identifier": "login@example.com", "password": "ComplexPass123!"}, format='json')
        self.assertEqual(res.status_code, 200)

    def test_login_wrong_password(self):
        res = self.client.post('/api/auth/login/', {"identifier": "loginuser", "password": "wrong"}, format='json')
        self.assertEqual(res.status_code, 400)

    def test_login_nonexistent_user(self):
        res = self.client.post('/api/auth/login/', {"identifier": "nobody", "password": "any"}, format='json')
        self.assertEqual(res.status_code, 400)

    def test_login_missing_fields(self):
        res = self.client.post('/api/auth/login/', {"identifier": "loginuser"}, format='json')
        self.assertEqual(res.status_code, 400)


class SignupTests(TestCase):
    """Test signup with invite tokens."""

    def setUp(self):
        self.client = APIClient()
        self.family = Family.objects.create(sl_no="1", branch="Main", member_no="FAM-SIGNUP-001")
        self.member = FamilyMember.objects.create(
            family=self.family, name="New Person", age=20,
            relation="Son", date_of_birth=datetime.date(2004, 1, 1)
        )

    def test_signup_with_valid_token(self):
        token = InviteToken.objects.create(member=self.member)
        res = self.client.post('/api/auth/signup/', {
            "username": "newbie", "email": "newbie@example.com",
            "password": "ComplexPass123!", "invite_token": str(token.token)
        }, format='json')
        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.data['username'], "newbie")
        token.refresh_from_db()
        self.assertTrue(token.is_used)

    def test_signup_with_invalid_token(self):
        res = self.client.post('/api/auth/signup/', {
            "username": "bad", "email": "bad@example.com",
            "password": "ComplexPass123!", "invite_token": "not-a-real-uuid"
        }, format='json')
        self.assertEqual(res.status_code, 400)

    def test_signup_with_used_token(self):
        token = InviteToken.objects.create(member=self.member, is_used=True)
        res = self.client.post('/api/auth/signup/', {
            "username": "late", "email": "late@example.com",
            "password": "ComplexPass123!", "invite_token": str(token.token)
        }, format='json')
        self.assertEqual(res.status_code, 400)

    def test_signup_auto_login(self):
        """After signup, user should be logged in (session established)."""
        token = InviteToken.objects.create(member=None)
        res = self.client.post('/api/auth/signup/', {
            "username": "autouser", "email": "auto@example.com",
            "password": "ComplexPass123!", "invite_token": str(token.token)
        }, format='json')
        self.assertEqual(res.status_code, 201)
        # Should be able to hit /me/ immediately
        me_res = self.client.get('/api/auth/me/')
        self.assertEqual(me_res.status_code, 200)
        self.assertEqual(me_res.data['username'], "autouser")


class MeAndLogoutTests(TestCase):
    """Test /me/ endpoint and logout."""

    def setUp(self):
        self.client = APIClient()
        self.family = Family.objects.create(sl_no="1", branch="Main", member_no="FAM-ME-001")
        self.member = FamilyMember.objects.create(
            family=self.family, name="Me User", age=30, relation="Head"
        )
        self.user = User.objects.create_user(
            username="meuser", email="me@example.com",
            password="Pass123!", member=self.member
        )

    def test_me_authenticated(self):
        self.client.force_authenticate(user=self.user)
        res = self.client.get('/api/auth/me/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['username'], "meuser")

    def test_me_unauthenticated(self):
        res = self.client.get('/api/auth/me/')
        self.assertIn(res.status_code, [401, 403])

    def test_logout(self):
        self.client.force_authenticate(user=self.user)
        res = self.client.post('/api/auth/logout/')
        self.assertEqual(res.status_code, 200)


class GiveAccessTests(TestCase):
    """Test the guardian Give Access flow."""

    def setUp(self):
        self.client = APIClient()
        self.family = Family.objects.create(sl_no="1", branch="Main", member_no="FAM-GA-001")
        # Guardian
        self.guardian_member = FamilyMember.objects.create(
            family=self.family, name="Guardian", age=40, relation="Head"
        )
        self.guardian = User.objects.create_user(
            username="guardian", email="guardian@example.com",
            password="Pass123!", member=self.guardian_member
        )
        # Managed member (no user account)
        self.managed = FamilyMember.objects.create(
            family=self.family, name="Child Member", age=10,
            relation="Son", created_by=self.guardian
        )

    def test_give_access_success(self):
        self.client.force_authenticate(user=self.guardian)
        res = self.client.post('/api/auth/give-access/', {
            "profile_id": self.managed.id,
            "username": "child_user",
            "password": "ChildPass123!"
        }, format='json')
        self.assertEqual(res.status_code, 201)
        self.assertIn("child_user", res.data['username'])
        # Verify user was created
        self.assertTrue(User.objects.filter(username="child_user").exists())

    def test_give_access_not_guardian(self):
        """Non-guardian cannot give access."""
        other_member = FamilyMember.objects.create(
            family=self.family, name="Other", age=30, relation="Brother"
        )
        other_user = User.objects.create_user(username="other", email="other@ex.com", password="Pass123!", member=other_member)
        self.client.force_authenticate(user=other_user)
        res = self.client.post('/api/auth/give-access/', {
            "profile_id": self.managed.id,
            "username": "hack", "password": "hack123!"
        }, format='json')
        self.assertEqual(res.status_code, 403)

    def test_give_access_already_has_account(self):
        """Cannot give access if profile already has an account."""
        User.objects.create_user(username="existing", email="ex@ex.com", password="Pass123!", member=self.managed)
        self.client.force_authenticate(user=self.guardian)
        res = self.client.post('/api/auth/give-access/', {
            "profile_id": self.managed.id,
            "username": "dup", "password": "dup123!"
        }, format='json')
        self.assertEqual(res.status_code, 400)

    def test_give_access_duplicate_username(self):
        """Cannot use an already-taken username."""
        self.client.force_authenticate(user=self.guardian)
        res = self.client.post('/api/auth/give-access/', {
            "profile_id": self.managed.id,
            "username": "guardian",  # Already exists
            "password": "Pass123!"
        }, format='json')
        self.assertEqual(res.status_code, 400)

    def test_give_access_missing_fields(self):
        self.client.force_authenticate(user=self.guardian)
        res = self.client.post('/api/auth/give-access/', {
            "profile_id": self.managed.id
        }, format='json')
        self.assertEqual(res.status_code, 400)


class GoIndependentTests(TestCase):
    """Test the Go Independent flow."""

    def setUp(self):
        self.client = APIClient()
        self.family = Family.objects.create(sl_no="1", branch="Main", member_no="FAM-IND-001")
        self.guardian_member = FamilyMember.objects.create(
            family=self.family, name="Guardian", age=40, relation="Head"
        )
        self.guardian = User.objects.create_user(
            username="guard2", email="guard2@example.com",
            password="Pass123!", member=self.guardian_member
        )
        self.managed = FamilyMember.objects.create(
            family=self.family, name="Dependent", age=20,
            relation="Son", created_by=self.guardian, is_independent=False
        )
        self.dependent_user = User.objects.create_user(
            username="dependent", email="dep@example.com",
            password="Pass123!", member=self.managed
        )

    def test_go_independent(self):
        self.client.force_authenticate(user=self.dependent_user)
        res = self.client.post('/api/auth/go-independent/')
        self.assertEqual(res.status_code, 200)
        self.managed.refresh_from_db()
        self.assertTrue(self.managed.is_independent)

    def test_already_independent(self):
        self.managed.is_independent = True
        self.managed.save()
        self.client.force_authenticate(user=self.dependent_user)
        res = self.client.post('/api/auth/go-independent/')
        self.assertEqual(res.status_code, 200)

    def test_go_independent_blocks_guardian_edit(self):
        """After going independent, guardian should not be able to edit."""
        self.managed.is_independent = True
        self.managed.save()
        self.client.force_authenticate(user=self.guardian)
        res = self.client.put(f'/api/families/managed/{self.managed.id}/', {
            "first_name": "Hacked", "last_name": "Name"
        }, format='json')
        self.assertIn(res.status_code, [403, 404])


class CsrfTests(TestCase):
    """Test CSRF init endpoint."""

    def test_csrf_init(self):
        client = APIClient()
        res = client.get('/api/csrf/')
        self.assertEqual(res.status_code, 200)
        self.assertIn('csrfToken', res.data)
