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
    
    # Professional Tabbed Interface
    tabs = [
        ("General", ["general_tab"]),
        ("Contact", ["contact_tab"]),
        ("Background", ["background_tab"]),
    ]

    fieldsets = (
        (None, {
            'classes': ('unfold-tab', 'unfold-general_tab'),
            'fields': (('name', 'nickname'), ('age', 'gender'), 'family', 'user')
        }),
        (None, {
            'classes': ('unfold-tab', 'unfold-contact_tab'),
            'fields': ('address', 'phone', 'email')
        }),
        (None, {
            'classes': ('unfold-tab', 'unfold-background_tab'),
            'fields': ('church', 'education', 'occupation')
        }),
    )


@admin.register(models.FamilyMember)
class FamilyMemberAdmin(ModelAdmin):
    list_display = ('name', 'family', 'relation', 'age', 'blood_group')
    list_filter = ('relation', 'blood_group', 'family')
    search_fields = ('name', 'temp_member_id')

    tabs = [
        ("Information", ["info_tab"]),
        ("Work & Education", ["work_tab"]),
        ("Connections", ["connections_tab"]),
    ]
    
    fieldsets = (
        (None, {
            'classes': ('unfold-tab', 'unfold-info_tab'),
            'fields': (('name', 'relation'), ('age', 'date_of_birth'), 'blood_group', 'family')
        }),
        (None, {
            'classes': ('unfold-tab', 'unfold-work_tab'),
            'fields': ('education', 'occupation', 'place_of_work')
        }),
        (None, {
            'classes': ('unfold-tab', 'unfold-connections_tab'),
            'fields': ('temp_member_id', 'parents', 'photo')
        }),
    )

@admin.register(models.DeceasedMember)
class DeceasedMemberAdmin(ModelAdmin):
    list_display = ('name', 'family', 'relation', 'age_at_death')
    list_filter = ('family',)
    search_fields = ('name',)
