import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    # 2. USER AUTHENTICATION
    email = models.EmailField(unique=True)
    
    # One-to-One link between 'members' and 'users'. Only family members can have accounts.
    # One-to-One link between 'members' and 'users'. Only family members can have accounts.
    member = models.OneToOneField(
        'families.FamilyMember', 
        on_delete=models.CASCADE, 
        related_name='user_account',
        null=True,
        blank=True
    )
    
    role = models.CharField(max_length=20, default='member') # 'admin', 'member'
    
    # avatar is now on the Member model (profile_pic), but keeping here for fallback or removed? 
    # User request says "profile_pic_url TEXT" in members table.
    # So we can potentially deprecate 'avatar' here or keep it. 
    # The request doesn't explicitly show 'avatar' in users table.
    # I will keep it for now to avoid breaking too many things, or remove it if I strictly follow the schema.
    # Request: "profile_pic_url TEXT" in members.
    # I'll comment it out or remove it to align with schema.
    # avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email'] # removed member_id from required as it's a FK now, usually set programmatically

class InviteToken(models.Model):
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    
    # Optional pre-link to a member so they don't have to enter member_id during signup
    member = models.ForeignKey(
        'families.FamilyMember', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='invite_tokens'
    )
    
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Token {self.token} ({'Used' if self.is_used else 'Available'})"
