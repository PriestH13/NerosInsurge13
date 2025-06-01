from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import User
from .forms import UserRegisterForm, UserProfileForm

class RegisterView(CreateView):
    model = User
    form_class = UserRegisterForm
    template_name = 'auth/register.html'
    success_url = reverse_lazy('auth:login')

class ProfileView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'auth/profile.html'
    context_object_name = 'user_profile'

    def get_object(self):
        return self.request.user

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserProfileForm
    template_name = 'auth/profile_edit.html'
    success_url = reverse_lazy('auth:profile')

    def get_object(self):
        return self.request.user
