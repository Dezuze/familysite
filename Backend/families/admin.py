from django.contrib import admin
from . import models


@admin.register(models.Family)
class FamilyAdmin(admin.ModelAdmin):
    list_display = ('member_no', 'sl_no', 'branch', 'created_at')


@admin.register(models.FamilyHead)
class FamilyHeadAdmin(admin.ModelAdmin):
    list_display = ('name', 'family')


@admin.register(models.FamilyMember)
class FamilyMemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'family', 'relation', 'age')

@admin.register(models.DeceasedMember)
class DeceasedMemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'family', 'relation', 'age_at_death')
