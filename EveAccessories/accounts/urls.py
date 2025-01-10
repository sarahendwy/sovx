from django.urls import path, include
from django.contrib.auth.decorators import login_required
from .views import *

urlpatterns = [
    # Authentication
    path('login/', Login.as_view(), name='login'),
    path('signup/', CreateAccount.as_view(), name='signup'),
    path('success/', success, name='success'),
    path('activate/<uidb64>/<token>/', activate, name='activate'),
    path('resend_mail/<str:uname>', resend_activation_mail, name="resend_mail"),
    path("logout/", login_required(logout_view), name="logout"),

    # User functions
    path('profile/', ShowProfile.as_view(), name='profile'),
    path('profile/edit', login_required(EditAccount.as_view()), name='edit_profile'),

    # Imports
    path('', include('django.contrib.auth.urls')),
]
