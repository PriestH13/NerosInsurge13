from django.urls import re_path
from . import consumers


websocket_urlpatterns = [
    re_path(r'ws/chat/private/(?P<conversation_id>[0-9a-f-]+)/$', consumers.PrivateChatConsumer.as_asgi()),

    re_path(r'ws/chat/global/$', consumers.GlobalChatConsumer.as_asgi()),
]