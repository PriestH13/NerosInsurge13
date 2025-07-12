from .models import Petition, PetitionStatus
from django.db.models import Count

def unread_notifications_count(request):
    if request.user.is_authenticated:
        count = request.user.notifications.filter(is_read=False).count()
    else:
        count = 0
    return {'unread_notifications_count': count}



def unread_notifications(request):
    if request.user.is_authenticated:
        notifs = request.user.notifications.filter(is_read=False).order_by('-created_at')[:10]
        return {'unread_notifications': notifs}
    return {}