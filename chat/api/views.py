from django.http import JsonResponse
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
import json
from chat.models import GlobalChatMessage
from django.utils import timezone

class GlobalMessagesAPI(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        messages = GlobalChatMessage.objects.all().order_by('-timestamp')[:50]
        data = [{
            'id': msg.id,
            'sender': {
                'username': msg.sender.username,
                'email': msg.sender.email,
                'profile_picture': msg.sender.profile_picture.url if hasattr(msg.sender, 'profile_picture') else None
            },
            'content': msg.content,
            'timestamp': msg.timestamp.strftime("%H:%M"),
            'is_own': msg.sender == request.user
        } for msg in reversed(messages)]
        
        return JsonResponse(data, safe=False)

class SendGlobalMessageAPI(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            content = data.get('content', '').strip()
            
            if not content:
                return JsonResponse({'status': 'error', 'message': 'Il messaggio non può essere vuoto'}, status=400)
                
            message = GlobalChatMessage.objects.create(
                sender=request.user,
                content=content
            )
            
            return JsonResponse({
                'status': 'success',
                'message': {
                    'id': message.id,
                    'sender': {
                        'username': request.user.username,
                        'email': request.user.email,
                        'profile_picture': request.user.profile_picture.url if hasattr(request.user, 'profile_picture') else None
                    },
                    'content': message.content,
                    'timestamp': message.timestamp.strftime("%H:%M"),
                    'is_own': True
                }
            })
            
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)