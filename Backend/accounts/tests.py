from django.test import TestCase
from django.contrib.auth import get_user_model
from families.models import Family, FamilyMember
from rest_framework.test import APIClient
import datetime

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
            member=self.member,
            first_name="John",
            last_name="Doe"
        )

    def test_user_creation(self):
        self.assertEqual(self.user.username, "johndoe")
        self.assertEqual(self.user.member, self.member)

    def test_login_success(self):
        url = '/auth/login/'
        data = {"identifier": "johndoe", "password": "ComplexPass123!"}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['username'], "johndoe")

    def test_login_fail(self):
        url = '/api/auth/login/'
        data = {"identifier": "johndoe", "password": "wrongpassword123!"}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)
