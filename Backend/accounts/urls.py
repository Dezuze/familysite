from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.LoginView.as_view()),
    path('signup/', views.SignupView.as_view()),
    path('logout/', views.LogoutView.as_view()),
    path('me/', views.MeView.as_view()),
    path('generate-invite-token/', views.GenerateInviteTokenView.as_view()),
    # Guardian / Claim flows
    path('give-access/', views.GiveAccessView.as_view()),
    path('claim/', views.ClaimAccountView.as_view()),
    path('go-independent/', views.GoIndependentView.as_view()),
]
