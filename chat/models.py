from django.db import models
from django.utils import timezone
import uuid
from auth_users.models import User

class GlobalChatMessage(models.Model):
    message_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='global_messages')
    content = models.TextField(max_length=2000)
    timestamp = models.DateTimeField(default=timezone.now)
    is_edited = models.BooleanField(default=False)

    class Meta:
        ordering = ['timestamp']
        indexes = [
            models.Index(fields=['timestamp']),
        ]

    def __str__(self):
        return f"{self.sender.username}: {self.content[:50]}..."

class PrivateConversation(models.Model):
    conversation_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    participant1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversations1')
    participant2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversations2')
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ['participant1', 'participant2']  # Evita conversazioni duplicate
        indexes = [
            models.Index(fields=['participant1', 'participant2']),
        ]

    def __str__(self):
        return f"Conversation between {self.participant1.username} and {self.participant2.username}"

class PrivateMessage(models.Model):
    message_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    conversation = models.ForeignKey(PrivateConversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='private_messages')
    content = models.TextField(max_length=2000)
    timestamp = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)
    is_edited = models.BooleanField(default=False)

    class Meta:
        ordering = ['timestamp']
        indexes = [
            models.Index(fields=['conversation', 'timestamp']),
        ]

    def __str__(self):
        return f"{self.sender.username} in {self.conversation}: {self.content[:50]}..."

# Modello per i gruppi
class Group(models.Model):
    group_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=500, blank=True, null=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_groups')
    members = models.ManyToManyField(User, through='GroupMembership', related_name='chat_groups')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['name']),
        ]

    def __str__(self):
        return self.name

class GroupMembership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    is_admin = models.BooleanField(default=False)
    joined_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ['user', 'group']
        indexes = [
            models.Index(fields=['user', 'group']),
        ]

    def __str__(self):
        return f"{self.user.username} in {self.group.name}"

class GroupMessage(models.Model):
    message_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='group_messages')
    content = models.TextField(max_length=2000)
    timestamp = models.DateTimeField(default=timezone.now)
    is_edited = models.BooleanField(default=False)
    class Meta:
        ordering = ['timestamp']
        indexes = [
            models.Index(fields=['group', 'timestamp']),
        ]

    def __str__(self):
        return f"{self.sender.username} in {self.group.name}: {self.content[:50]}..."