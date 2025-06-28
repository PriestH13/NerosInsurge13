from django.urls import path
from . import api

app_name = 'petitions_api'

urlpatterns = [
    path('petitions/', api.PetitionListAPI.as_view(), name='petition_list_api'),
    path('petitions/<int:pk>/', api.PetitionDetailAPI.as_view(), name='petition_detail_api'),
    path('petitions/<int:pk>/comments/', api.PetitionCommentsAPI.as_view(), name='petition_comments_api'),
    path('petitions/<int:pk>/vote/', api.PetitionVoteAPI.as_view(), name='petition_vote_api'),
    path('petitions/<int:pk>/sign/', api.PetitionSignAPI.as_view(), name='petition_sign_api'),
]
