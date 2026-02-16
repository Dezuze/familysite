from django.contrib import admin
from unfold.admin import ModelAdmin
from . import models


@admin.register(models.Family)
class FamilyAdmin(ModelAdmin):
    list_display = ('member_no', 'sl_no', 'branch', 'created_at')


@admin.register(models.FamilyHead)
class FamilyHeadAdmin(ModelAdmin):
    list_display = ('name', 'family', 'phone', 'email')
    list_filter = ('gender', 'church')
    search_fields = ('name', 'email', 'phone')


@admin.register(models.FamilyMember)
class FamilyMemberAdmin(ModelAdmin):
    list_display = ('name', 'family', 'relation', 'age', 'blood_group')
    list_filter = ('relation', 'blood_group', 'family')
    search_fields = ('name', 'temp_member_id')

@admin.register(models.FamilyMedia)
class FamilyMediaAdmin(ModelAdmin):
    list_display = ('family', 'category', 'image')
    list_filter = ('category', 'family')

@admin.register(models.DeceasedMember)
class DeceasedMemberAdmin(ModelAdmin):
    list_display = ('name', 'family', 'relation', 'age_at_death')
    list_filter = ('family',)
    search_fields = ('name',)
