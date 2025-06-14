from django.urls import path
from .views import (HomeView,PetitionListView,PetitionDetailView,PetitionCreateView,PetitionUpdateView,PetitionDeleteView,RequestSignatureView,ConfirmSignatureView,
    PetitionSearchView,
    PetitionVoteView,
    ReportPetitionView,
    NotificationListView,
    
)

app_name = 'petitions'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),

    
    path('list/', PetitionListView.as_view(), name='petition_list'),
    path('create/', PetitionCreateView.as_view(), name='petition_create'),
    path('<int:pk>/', PetitionDetailView.as_view(), name='petition_detail'),
    path('<int:pk>/edit/', PetitionUpdateView.as_view(), name='petition_edit'),
    path('<int:pk>/delete/', PetitionDeleteView.as_view(), name='petition_delete'),
    path('search/', PetitionSearchView.as_view(), name='petition_search'),


    path('petizione/<int:pk>/firma/', RequestSignatureView.as_view(), name='request_signature'),
    path('firma/conferma/<uuid:token>/', ConfirmSignatureView.as_view(), name='confirm_signature'),
    
    path('<int:pk>/vote/', PetitionVoteView.as_view(), name='petition_vote'),

    path('report/petition/<int:pk>/', ReportPetitionView.as_view(), name='report_petition'),

    path('notifications/', NotificationListView.as_view(), name='notification_list'),

]