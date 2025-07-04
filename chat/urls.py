from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('global/', views.GlobalChatView.as_view(), name='global_chat'),
    path('api/global/messages/', views.GlobalMessagesAPI.as_view(), name='global_messages_api'),
    path('api/global/send/', views.SendGlobalMessageAPI.as_view(), name='send_global_message_api'),

    path('conversations/', views.PrivateConversationsView.as_view(), name='private_conversations'),
    path('conversation/<uuid:conversation_id>/', views.PrivateConversationDetailView.as_view(), name='private_conversation_detail'),
    
    path('groups/', views.GroupListView.as_view(), name='group_list'),
    path('group/create/', views.CreateGroupView.as_view(), name='create_group'),
    path('group/<uuid:group_id>/', views.GroupDetailView.as_view(), name='group_detail'),
    path('group/<uuid:group_id>/add-member/', views.AddGroupMemberView.as_view(), name='add_group_member'),
    path('conversation/start/', views.StartConversationView.as_view(), name='start_conversation'),

    path('search/', views.SearchProfilesAndGroupsView.as_view(), name='search_profiles_and_groups'),
   
]