"""
Data migration:
1. Set is_independent=True for FamilyMembers that already have a User account.
2. Migrate old relationship types to new 3-type system:
   - Father, Mother → PARENT
   - Spouse → SPOUSE
   - Sibling, Cousin, Aunt, Uncle, Grandparent, Other → SIBLING
3. Auto-assign gender based on old relationship type (Father→M, Mother→F).
"""

from django.db import migrations


def migrate_data(apps, schema_editor):
    FamilyMember = apps.get_model('families', 'FamilyMember')
    Relationship = apps.get_model('families', 'Relationship')

    # 1. Set is_independent=True for members with user accounts
    #    We check via the reverse relation 'user_account' on FamilyMember
    User = apps.get_model('accounts', 'User')
    linked_member_ids = User.objects.filter(member__isnull=False).values_list('member_id', flat=True)
    FamilyMember.objects.filter(id__in=linked_member_ids).update(is_independent=True)

    # 2. Migrate relationship types
    TYPE_MAP = {
        'Father': 'PARENT',
        'Mother': 'PARENT',
        'Spouse': 'SPOUSE',
        'Sibling': 'SIBLING',
        'Cousin': 'SIBLING',
        'Aunt': 'SIBLING',
        'Uncle': 'SIBLING',
        'Grandparent': 'PARENT',
        'Other': 'SIBLING',
    }

    # 3. Gender auto-assign map from old relation types
    GENDER_MAP = {
        'Father': 'M',
        'Mother': 'F',
    }

    for rel in Relationship.objects.all():
        old_type = rel.relation_type
        new_type = TYPE_MAP.get(old_type)
        if new_type and new_type != old_type:
            # Check for existing duplicate before updating
            exists = Relationship.objects.filter(
                from_member=rel.from_member,
                to_member=rel.to_member,
                relation_type=new_type
            ).exclude(id=rel.id).exists()
            if exists:
                rel.delete()
            else:
                rel.relation_type = new_type
                rel.save()

        # Auto-assign gender on the to_member based on old relation type
        if old_type in GENDER_MAP:
            target = rel.to_member
            target.gender = GENDER_MAP[old_type]
            target.save()


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('families', '0015_familymember_is_independent_and_more'),
        ('accounts', '0006_claimtoken'),
    ]

    operations = [
        migrations.RunPython(migrate_data, noop),
    ]
