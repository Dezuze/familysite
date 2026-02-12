from django.test import TestCase
from django.contrib.auth import get_user_model
from families.models import Family, FamilyMember
from rest_framework.test import APIClient
import datetime
from .models import InviteToken

User = get_user_model()

class AccountsTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.family = Family.objects.create(sl_no="1", branch="Main", member_no="FAM-TEST-001")
        self.member = FamilyMember.objects.create(
            family=self.family,
            name="John Doe",
            age=30,
            relation="Head",
            date_of_birth=datetime.date(1994, 1, 1),
            blood_group="O+",
            education="B.Tech",
            occupation="Engineer"
        )
        self.user = User.objects.create_user(
            username="johndoe",
            email="john@example.com",
            password="ComplexPass123!",
            member=self.member
        )

    def test_user_creation(self):
        self.assertEqual(self.user.username, "johndoe")
        self.assertEqual(self.user.member, self.member)

    def test_login_success(self):
        url = '/api/auth/login/'
        data = {"identifier": "johndoe", "password": "ComplexPass123!"}
        response = self.client.post(url, data, format='json')
        if response.status_code != 200:
            print("Login success test failed with status", response.status_code, "and data:", response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['username'], "johndoe")

    def test_login_fail(self):
        url = '/api/auth/login/'
        data = {"identifier": "johndoe", "password": "wrongpassword123!"}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_signup_with_token(self):
        # 0. Create a separate member for signup (since one-to-one)
        new_member = FamilyMember.objects.create(
            family=self.family,
            name="New Member",
            age=20,
            relation="Child",
            date_of_birth=datetime.date(2004, 1, 1)
        )
        # 1. Generate Token
        token_obj = InviteToken.objects.create(member=new_member)
        token_str = str(token_obj.token)

        # 2. Signup
        url = '/api/auth/signup/'
        data = {
            "username": "newuser",
            "email": "new@example.com",
            "password": "ComplexPass123!",
            "invite_token": token_str
        }
        response = self.client.post(url, data, format='json')
        if response.status_code != 201:
             print("Signup with token failed with data:", response.data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['username'], "newuser")

        # 3. Verify Token Used
        token_obj.refresh_from_db()
        self.assertTrue(token_obj.is_used)

    def test_signup_invalid_token(self):
        url = '/api/auth/signup/'
        data = {
            "username": "baduser",
            "email": "bad@example.com",
            "password": "ComplexPass123!",
            "invite_token": "invalid-uuid"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.data)
