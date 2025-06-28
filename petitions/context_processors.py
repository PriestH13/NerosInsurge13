from .models import Petition, PetitionStatus
from django.db.models import Count

def unread_notifications_count(request):
    if request.user.is_authenticated:
        return {
            'unread_notifications_count': request.user.notifications.filter(is_read=False).count()
        }
    return {}


def featured_petitions_context(request):
    return {
        'featured_petitions': Petition.objects.filter(
            status=PetitionStatus.PUBLISHED,
            is_active=True
        ).annotate(num_signatures=Count('signatures')).order_by('-num_signatures')[:5]
    }