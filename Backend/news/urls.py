from django.urls import path
from .views import (
    EventsListView,
    NewsListView,
    NewsCreateView,
    NewsDetailView,
    CelebrationNotificationsView,
)

urlpatterns = [
    path('events/', EventsListView.as_view()),
    path('list/', NewsListView.as_view()),
    path('notifications/', CelebrationNotificationsView.as_view()),
    path('create/', NewsCreateView.as_view()),
    path('<int:pk>/', NewsDetailView.as_view()),
]
