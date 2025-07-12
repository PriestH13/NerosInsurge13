from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import PrivateMessage
from petitions.models import Notification

@receiver(post_save, sender=PrivateMessage)
def create_notification_for_private_message(sender, instance, created, **kwargs):
    if created:
        recipient = instance.conversation.participant1 if instance.sender != instance.conversation.participant1 else instance.conversation.participant2
        Notification.objects.create(
            user=recipient,
            message=f"Nuovo messaggio da {instance.sender.username}",
            link=f"/chat/conversation/{instance.conversation.conversation_id}/",
            notification_type='chat_message',
        )
