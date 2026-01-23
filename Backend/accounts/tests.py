from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient


from families.models import FamilyMember, Family

class AccountsAPITestCase(TestCase):
	def setUp(self):
		User = get_user_model()
		self.username = 'testuser'
		self.password = 'pass1234'
		
		# Create family and member first
		self.family = Family.objects.create(sl_no='A1', branch='AccBranch', member_no='AMem1')
		self.member = FamilyMember.objects.create(
			family=self.family,
			name="Test Member",
			date_of_birth="2000-01-01",
			relation="Self",
			occupation="Tester"
		)
		
		self.user = User.objects.create_user(
			username=self.username,
			email='test@example.com',
			member=self.member, # Use instance, or member_id=self.member.id
			password=self.password,
		)
		self.client = APIClient()

	def test_login_success_and_me(self):
		resp = self.client.post('/api/auth/login/', {'identifier': self.username, 'password': self.password}, format='json')
		self.assertEqual(resp.status_code, 200)
		self.assertIn('username', resp.data)

		# After login, /api/auth/me/ should return the user
		resp2 = self.client.get('/api/auth/me/')
		self.assertEqual(resp2.status_code, 200)
		self.assertEqual(resp2.data.get('username'), self.username)

	def test_login_failure(self):
		resp = self.client.post('/api/auth/login/', {'identifier': self.username, 'password': 'wrong'}, format='json')
		self.assertEqual(resp.status_code, 400)
		self.assertIn('error', resp.data)

	def test_logout(self):
		# login first
		self.client.post('/api/auth/login/', {'identifier': self.username, 'password': self.password}, format='json')
		resp = self.client.post('/api/auth/logout/')
		self.assertEqual(resp.status_code, 200)
		self.assertIn('message', resp.data)

	def test_login_by_email(self):
		resp = self.client.post('/api/auth/login/', {'identifier': 'test@example.com', 'password': self.password}, format='json')
		self.assertEqual(resp.status_code, 200)
		self.assertEqual(resp.data.get('username'), self.username)

	def test_login_by_member_id(self):
		# User is linked to self.member
		resp = self.client.post('/api/auth/login/', {'identifier': self.member.id, 'password': self.password}, format='json')
		self.assertEqual(resp.status_code, 200)
		self.assertEqual(resp.data.get('username'), self.username)

	def test_me_unauthenticated_returns_401(self):
		# use a fresh client without session
		client2 = APIClient()
		resp = client2.get('/api/auth/me/')
		self.assertIn(resp.status_code, (401, 403))

	def test_signup(self):
		f2 = Family.objects.create(sl_no='A2', branch='AccBranch2', member_no='AMem2')
		m2 = FamilyMember.objects.create(family=f2, name="Member 2", date_of_birth="1990-01-01", relation="Sibling")
		resp = self.client.post('/api/auth/signup/', {
			'username': 'newuser',
			'email': 'new@example.com',
			'member_id': m2.id,
			'password': 'newpass123'
		}, format='json')
		self.assertEqual(resp.status_code, 201)
		self.assertEqual(resp.data.get('username'), 'newuser')
