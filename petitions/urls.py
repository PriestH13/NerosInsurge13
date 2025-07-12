from django.urls import path
from .views import (HomeView,PetitionListView,PetitionDetailView,PetitionCreateView,PetitionUpdateView,PetitionDeleteView,RequestSignatureView,ConfirmSignatureView,
    PetitionSearchView,PetitionVoteView,ReportPetitionView,NotificationListView,AboutView, TermsView, PrivacyView, mark_notification_read, go_to_notification
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
    # Vote
    path('<int:pk>/vote/', PetitionVoteView.as_view(), name='petition_vote'),
    # Rep
    path('report/petition/<int:pk>/', ReportPetitionView.as_view(), name='report_petition'),
    # Notif
    path('notifications/', NotificationListView.as_view(), name='notification_list'),
    path('mark-notification-read/<int:pk>/', mark_notification_read, name='mark_notification_read'),
    path('notifications/go-to/<int:pk>/', go_to_notification, name='go_to_notification'),

    # other
    path('other/chi-siamo/', AboutView.as_view(), name='about'),
    path('other/termini-e-condizioni/', TermsView.as_view(), name='terms'),
    path('other/privacy/', PrivacyView.as_view(), name='privacy'),


]