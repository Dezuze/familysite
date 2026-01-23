from django.urls import path
from .views import UserProfileView, FamilyTreeView, FamilyMediaList, FamilyMediaDetail

urlpatterns = [
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('tree/', FamilyTreeView.as_view(), name='family-tree'),
    path('media/', FamilyMediaList.as_view(), name='family-media-list'),
    path('media/<int:pk>/', FamilyMediaDetail.as_view(), name='family-media-detail'),
]
