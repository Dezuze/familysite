from django.urls import path
from .views import (
    UserProfileView, FamilyTreeView, FamilyMediaList, FamilyMediaDetail,
    ManagedMembersView, ManagedMemberDetailView
)

urlpatterns = [
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('tree/', FamilyTreeView.as_view(), name='family-tree'),
    path('media/', FamilyMediaList.as_view(), name='family-media-list'),
    path('media/<int:pk>/', FamilyMediaDetail.as_view(), name='family-media-detail'),
    path('managed/', ManagedMembersView.as_view(), name='managed-members'),
    path('managed/<int:pk>/', ManagedMemberDetailView.as_view(), name='managed-member-detail'),
]
