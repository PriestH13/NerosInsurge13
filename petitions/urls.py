from django.urls import path
from .views import (
    HomeView,
    PetitionListView,
    PetitionDetailView,
    PetitionCreateView,
    PetitionUpdateView,
    PetitionDeleteView
)

app_name = 'petitions'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),

    
    path('list/', PetitionListView.as_view(), name='petition_list'),
    path('create/', PetitionCreateView.as_view(), name='petition_create'),
    path('<int:pk>/', PetitionDetailView.as_view(), name='petition_detail'),
    path('<int:pk>/edit/', PetitionUpdateView.as_view(), name='petition_edit'),
    path('<int:pk>/delete/', PetitionDeleteView.as_view(), name='petition_delete'),
]
