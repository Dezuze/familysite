"""
Comprehensive tests for the families app.
Covers: FamilyMember CRUD, Relationships, Profile management,
        Managed Members (list/create/edit/delete), Guardian permissions,
        Family tree endpoint.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
import datetime
from families.models import Family, FamilyMember, Relationship

User = get_user_model()


class FamilyModelTests(TestCase):
    """Test Family and FamilyMember model basics."""

    def setUp(self):
        self.family = Family.objects.create(sl_no="1", branch="North", member_no="F-MODEL-001")

    def test_family_str(self):
        self.assertEqual(str(self.family), "F-MODEL-001")

    def test_create_member(self):
        m = FamilyMember.objects.create(
            family=self.family, name="Alice", age=50,
            relation="Head", date_of_birth=datetime.date(1974, 5, 5),
            blood_group="A+", gender="F"
        )
        self.assertEqual(m.name, "Alice")
        self.assertEqual(m.gender, "F")
        self.assertFalse(m.is_independent)
        self.assertFalse(m.is_deceased)

    def test_member_with_date_of_death(self):
        m = FamilyMember.objects.create(
            family=self.family, name="Deceased", age=80,
            relation="Grandfather", is_deceased=True,
            date_of_death=datetime.date(2020, 3, 15), gender="M"
        )
        self.assertTrue(m.is_deceased)
        self.assertEqual(m.date_of_death, datetime.date(2020, 3, 15))

    def test_member_without_dob(self):
        """Members should be creatable without date_of_birth."""
        m = FamilyMember.objects.create(
            family=self.family, name="No DOB", relation="Other"
        )
        self.assertIsNone(m.date_of_birth)

    def test_parent_child_relationship(self):
        parent = FamilyMember.objects.create(
            family=self.family, name="Parent", age=50, relation="Head"
        )
        child = FamilyMember.objects.create(
            family=self.family, name="Child", age=25, relation="Son"
        )
        child.parents.add(parent)
        self.assertIn(parent, child.parents.all())
        self.assertIn(child, parent.children.all())

    def test_relation_choices(self):
        """Verify all relation choices are valid."""
        valid = [c[0] for c in FamilyMember.RELATION_CHOICES]
        self.assertIn('Head', valid)
        self.assertIn('Father', valid)
        self.assertIn('Mother', valid)
        self.assertIn('Son', valid)
        self.assertIn('Daughter', valid)
        self.assertIn('Brother-in-law', valid)
        self.assertIn('Other', valid)
        self.assertEqual(len(valid), 24)


class RelationshipModelTests(TestCase):
    """Test the simplified Relationship model (PARENT/SPOUSE/SIBLING)."""

    def setUp(self):
        self.family = Family.objects.create(sl_no="1", branch="Main", member_no="F-REL-001")
        self.m1 = FamilyMember.objects.create(family=self.family, name="A", relation="Head")
        self.m2 = FamilyMember.objects.create(family=self.family, name="B", relation="Spouse")

    def test_create_relationship(self):
        rel = Relationship.objects.create(
            from_member=self.m1, to_member=self.m2, relation_type="SPOUSE"
        )
        self.assertEqual(rel.relation_type, "SPOUSE")

    def test_relationship_str(self):
        rel = Relationship.objects.create(
            from_member=self.m1, to_member=self.m2, relation_type="PARENT"
        )
        self.assertIn("PARENT", str(rel))

    def test_unique_constraint(self):
        """Same from/to/type should not be duplicated."""
        Relationship.objects.create(from_member=self.m1, to_member=self.m2, relation_type="SPOUSE")
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            Relationship.objects.create(from_member=self.m1, to_member=self.m2, relation_type="SPOUSE")

    def test_different_types_allowed(self):
        """Same pair can have different relationship types."""
        Relationship.objects.create(from_member=self.m1, to_member=self.m2, relation_type="SPOUSE")
        Relationship.objects.create(from_member=self.m1, to_member=self.m2, relation_type="SIBLING")
        self.assertEqual(Relationship.objects.filter(from_member=self.m1).count(), 2)


class UserProfileViewTests(TestCase):
    """Test the /api/families/profile/ endpoint."""

    def setUp(self):
        self.client = APIClient()
        self.family = Family.objects.create(sl_no="1", branch="Main", member_no="F-PROF-001")
        self.member = FamilyMember.objects.create(
            family=self.family, name="Profile User", age=30,
            relation="Head", gender="M"
        )
        self.user = User.objects.create_user(
            username="profuser", email="prof@example.com",
            password="Pass123!", member=self.member
        )

    def test_get_own_profile(self):
        self.client.force_authenticate(user=self.user)
        res = self.client.get('/api/families/profile/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['name'], "Profile User")
        self.assertIn('is_independent', res.data)
        self.assertIn('has_account', res.data)

    def test_update_own_profile(self):
        self.client.force_authenticate(user=self.user)
        res = self.client.post('/api/families/profile/', {
            "first_name": "Updated",
            "last_name": "Name",
            "gender": "M",
        }, format='multipart')
        self.assertEqual(res.status_code, 200)

    def test_profile_without_dob(self):
        """Saving profile without DOB should not error."""
        self.client.force_authenticate(user=self.user)
        res = self.client.post('/api/families/profile/', {
            "first_name": "No",
            "last_name": "DOB",
            "gender": "F",
        }, format='multipart')
        self.assertEqual(res.status_code, 200)

    def test_unauthenticated_profile(self):
        res = self.client.get('/api/families/profile/')
        self.assertIn(res.status_code, [401, 403])


class ManagedMembersViewTests(TestCase):
    """Test managed members CRUD operations via /api/families/managed/."""

    def setUp(self):
        self.client = APIClient()
        self.family = Family.objects.create(sl_no="1", branch="Main", member_no="F-MNG-001")
        self.guardian_member = FamilyMember.objects.create(
            family=self.family, name="Guardian", age=40, relation="Head"
        )
        self.guardian = User.objects.create_user(
            username="mng_guard", email="mng_guard@example.com",
            password="Pass123!", member=self.guardian_member
        )

    def test_list_managed_empty(self):
        self.client.force_authenticate(user=self.guardian)
        res = self.client.get('/api/families/managed/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data), 0)

    def test_create_managed_member(self):
        self.client.force_authenticate(user=self.guardian)
        res = self.client.post('/api/families/managed/', {
            "first_name": "Child",
            "last_name": "One",
            "relation": "Son",
            "gender": "M"
        }, format='multipart')
        self.assertEqual(res.status_code, 201)
        self.assertIn("Child One", res.data['name'])

    def test_create_managed_deceased_with_death_date(self):
        self.client.force_authenticate(user=self.guardian)
        res = self.client.post('/api/families/managed/', {
            "first_name": "Grandpa",
            "last_name": "Joe",
            "relation": "Grandfather",
            "gender": "M",
            "is_deceased": True,
            "date_of_death": "2020-01-15"
        }, format='multipart')
        self.assertEqual(res.status_code, 201)

    def test_list_managed_excludes_independent(self):
        """Independent members should not appear in managed list."""
        managed = FamilyMember.objects.create(
            family=self.family, name="Indep", relation="Son",
            created_by=self.guardian, is_independent=True
        )
        self.client.force_authenticate(user=self.guardian)
        res = self.client.get('/api/families/managed/')
        self.assertEqual(res.status_code, 200)
        ids = [m['id'] for m in res.data]
        self.assertNotIn(managed.id, ids)

    def test_edit_managed_member(self):
        managed = FamilyMember.objects.create(
            family=self.family, name="Edit Me", relation="Son",
            created_by=self.guardian, is_independent=False
        )
        self.client.force_authenticate(user=self.guardian)
        res = self.client.put(f'/api/families/managed/{managed.id}/', {
            "first_name": "Edited",
            "last_name": "Name",
            "relation": "Daughter",
            "gender": "F"
        }, format='multipart')
        self.assertEqual(res.status_code, 200)

    def test_cannot_edit_independent_member(self):
        managed = FamilyMember.objects.create(
            family=self.family, name="Free", relation="Son",
            created_by=self.guardian, is_independent=True
        )
        self.client.force_authenticate(user=self.guardian)
        res = self.client.put(f'/api/families/managed/{managed.id}/', {
            "first_name": "Hacked"
        }, format='multipart')
        self.assertEqual(res.status_code, 403)

    def test_delete_managed_member(self):
        managed = FamilyMember.objects.create(
            family=self.family, name="Delete Me", relation="Son",
            created_by=self.guardian, is_independent=False
        )
        self.client.force_authenticate(user=self.guardian)
        res = self.client.delete(f'/api/families/managed/{managed.id}/')
        self.assertEqual(res.status_code, 204)

    def test_cannot_delete_independent_member(self):
        managed = FamilyMember.objects.create(
            family=self.family, name="Free Delete", relation="Son",
            created_by=self.guardian, is_independent=True
        )
        self.client.force_authenticate(user=self.guardian)
        res = self.client.delete(f'/api/families/managed/{managed.id}/')
        self.assertEqual(res.status_code, 403)

    def test_get_managed_member_detail(self):
        managed = FamilyMember.objects.create(
            family=self.family, name="Detail", relation="Son",
            created_by=self.guardian, is_independent=False
        )
        self.client.force_authenticate(user=self.guardian)
        res = self.client.get(f'/api/families/managed/{managed.id}/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['name'], "Detail")


class FamilyTreeViewTests(TestCase):
    """Test the /api/families/tree/ endpoint."""

    def setUp(self):
        self.client = APIClient()
        self.family = Family.objects.create(sl_no="1", branch="Main", member_no="F-TREE-001")
        self.member = FamilyMember.objects.create(
            family=self.family, name="Tree User", age=30, relation="Head"
        )
        self.user = User.objects.create_user(
            username="treeuser", email="tree@example.com",
            password="Pass123!", member=self.member
        )

    def test_get_tree(self):
        self.client.force_authenticate(user=self.user)
        res = self.client.get('/api/families/tree/')
        self.assertEqual(res.status_code, 200)
        self.assertIn('nodes', res.data)

    def test_tree_unauthenticated(self):
        res = self.client.get('/api/families/tree/')
        self.assertEqual(res.status_code, 200)  # Tree is public


class PermissionsTests(TestCase):
    """Test IsGuardianOrSelf permission logic via managed member endpoints."""

    def setUp(self):
        self.family = Family.objects.create(sl_no="1", branch="Main", member_no="F-PERM-001")
        self.guardian_member = FamilyMember.objects.create(
            family=self.family, name="Guard", age=40, relation="Head"
        )
        self.guardian = User.objects.create_user(
            username="perm_guard", email="pg@example.com",
            password="Pass123!", member=self.guardian_member
        )
        self.managed = FamilyMember.objects.create(
            family=self.family, name="Managed", relation="Son",
            created_by=self.guardian, is_independent=False
        )

    def test_guardian_can_read(self):
        client = APIClient()
        client.force_authenticate(user=self.guardian)
        res = client.get(f'/api/families/managed/{self.managed.id}/')
        self.assertEqual(res.status_code, 200)

    def test_guardian_can_write_non_independent(self):
        client = APIClient()
        client.force_authenticate(user=self.guardian)
        res = client.put(f'/api/families/managed/{self.managed.id}/', {
            "first_name": "Updated", "last_name": "Child",
            "relation": "Son", "gender": "M"
        }, format='multipart')
        self.assertEqual(res.status_code, 200)

    def test_guardian_blocked_when_independent(self):
        self.managed.is_independent = True
        self.managed.save()
        client = APIClient()
        client.force_authenticate(user=self.guardian)
        res = client.put(f'/api/families/managed/{self.managed.id}/', {
            "first_name": "Blocked"
        }, format='multipart')
        self.assertEqual(res.status_code, 403)
