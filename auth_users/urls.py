from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from .views import RegisterView, ProfileView, ProfileUpdateView

app_name = 'auth'

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),

    path('login/', auth_views.LoginView.as_view(template_name='auth/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/edit/', ProfileUpdateView.as_view(), name='profile_edit'),

    # Password reset
    path('password_reset/',auth_views.PasswordResetView.as_view(template_name='auth/password_reset_form.html',email_template_name='auth/password_reset_email.html',success_url=reverse_lazy('auth:password_reset_done')),name='password_reset'),
    path('password_reset/done/',auth_views.PasswordResetDoneView.as_view(template_name='auth/password_reset_done.html'),name='password_reset_done'),
   path(
    'reset/<uidb64>/<token>/',
    auth_views.PasswordResetConfirmView.as_view(
        template_name='auth/password_reset_confirm.html',
        success_url=reverse_lazy('auth:password_reset_complete')  # aggiungi questa riga!
    ),
    name='password_reset_confirm'
),
    path('reset/done/',auth_views.PasswordResetCompleteView.as_view(template_name='auth/password_reset_complete.html'),name='password_reset_complete'),
    
    # Password change
    path('password_change/',auth_views.PasswordChangeView.as_view(template_name='auth/password_change_form.html',success_url=reverse_lazy('auth:password_change_done')),name='password_change'),
    path('password_change/done/',auth_views.PasswordChangeDoneView.as_view(template_name='auth/password_change_done.html'),name='password_change_done'),
]