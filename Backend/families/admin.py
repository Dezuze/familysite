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
    
    tabs = [
        ("General", ["general_tab"]),
        ("Contact", ["contact_tab"]),
        ("Background", ["background_tab"]),
    ]

    fieldsets = (
        ("Core Details", {
            "classes": ["unfold-tab", "unfold-general_tab"],
            "fields": (("name", "nickname"), ("age", "gender"), "family", "user")
        }),
        ("Contact Information", {
            "classes": ["unfold-tab", "unfold-contact_tab"],
            "fields": ("address", "phone", "email")
        }),
        ("Professional Background", {
            "classes": ["unfold-tab", "unfold-background_tab"],
            "fields": ("church", "education", "occupation")
        }),
    )


@admin.register(models.FamilyMember)
class FamilyMemberAdmin(ModelAdmin):
    list_display = ('name', 'family', 'relation', 'age', 'blood_group')
    list_filter = ('relation', 'blood_group', 'family')
    search_fields = ('name', 'temp_member_id')

    tabs = [
        ("Personal Info", ["info_tab"]),
        ("Work & Education", ["work_tab"]),
        ("Gallery & Links", ["links_tab"]),
    ]
    
    fieldsets = (
        ("Basic Information", {
            "classes": ["unfold-tab", "unfold-info_tab"],
            "fields": (("name", "relation"), ("age", "date_of_birth"), "blood_group", "family")
        }),
        ("Career & Studies", {
            "classes": ["unfold-tab", "unfold-work_tab"],
            "fields": (("education", "occupation"), "place_of_work")
        }),
        ("Profile Data", {
            "classes": ["unfold-tab", "unfold-links_tab"],
            "fields": ("temp_member_id", "parents", "photo", "created_by")
        }),
    )

@admin.register(models.FamilyMedia)
class FamilyMediaAdmin(ModelAdmin):
    list_display = ('family', 'category', 'image')
    list_filter = ('category', 'family')

@admin.register(models.DeceasedMember)
class DeceasedMemberAdmin(ModelAdmin):
    list_display = ('name', 'family', 'relation', 'age_at_death')
    list_filter = ('family',)
    search_fields = ('name',)
