from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User
from families.models import FamilyMember, FamilyHead

@receiver(post_save, sender=User)
def sync_user_to_member(sender, instance, created, **kwargs):
    """
    Synchronizes the User link across FamilyMember and FamilyHead records.
    """
    if instance.member:
        # 1. Sync User back to FamilyMember
        member = instance.member
        if member.user != instance:
            member.user = instance
            member.save()

        # 2. Sync User to FamilyHead if this member is the head of their family
        # We check if a FamilyHead exists for this member's family and if the names match
        try:
            family_head = FamilyHead.objects.get(family=member.family)
            # If the member name matches the head name, we assume they are the same person
            if family_head.name == member.name and family_head.user != instance:
                family_head.user = instance
                family_head.save()
        except FamilyHead.DoesNotExist:
            pass

@receiver(post_save, sender=FamilyMember)
def sync_member_to_user(sender, instance, **kwargs):
    """
    Ensures that if a FamilyMember's user field is updated, the User's member field matches.
    """
    if instance.user:
        user = instance.user
        if user.member != instance:
            user.member = instance
            user.save()
