from django.db import models
from django.conf import settings
import uuid

#CATEGORIA
class PetitionCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

#TAG
class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

# === STATUS ===
class PetitionStatus(models.TextChoices):
    DRAFT = 'draft', 'Draft'
    PUBLISHED = 'published', 'Published'
    ARCHIVED = 'archived', 'Archived'
    DELETED = 'deleted', 'Deleted'

#PETIZIONE
class Petition(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='petitions')
    category = models.ForeignKey(PetitionCategory, on_delete=models.SET_NULL, null=True, blank=True)
    tags = models.ManyToManyField(Tag, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=PetitionStatus.choices, default=PetitionStatus.DRAFT)
    is_active = models.BooleanField(default=True)
    image = models.ImageField(upload_to='petitions/images/', null=True, blank=True)
    location = models.CharField(max_length=255, blank=True, help_text="Città o luogo associato alla petizione")


    def __str__(self):
        return self.title

#FIRMA
class Signature(models.Model):
    petition = models.ForeignKey(Petition, on_delete=models.CASCADE, related_name='signatures')
    email = models.EmailField(null=True, blank=True)
    signed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('petition', 'email')

    def __str__(self):
        return f"{self.email} signed '{self.petition.title}'"


class PendingSignature(models.Model):
    petition = models.ForeignKey(Petition, on_delete=models.CASCADE, related_name='pending_signatures')
    email = models.EmailField()
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    confirmed = models.BooleanField(default=False)
    requested_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.email} - {'Confirmed' if self.confirmed else 'Pending'}"


#COMMENTO
class Comment(models.Model):
    petition = models.ForeignKey(Petition, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username} on '{self.petition.title}'"

#VOTO
class PetitionVote(models.Model):
    petition = models.ForeignKey(Petition, on_delete=models.CASCADE, related_name='votes')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    is_upvote = models.BooleanField(default=True)
    voted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('petition', 'user', 'ip_address')

    def __str__(self):
        if self.user:
            return f"{self.user.username} voted {'↑' if self.is_upvote else '↓'}"
        return f"Anonymous ({self.ip_address}) voted {'↑' if self.is_upvote else '↓'}"


#ALLEGATO
class PetitionAttachment(models.Model):
    petition = models.ForeignKey(Petition, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='petitions/attachments/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Attachment for '{self.petition.title}'"

#REPORT
class Report(models.Model):
    reported_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    petition = models.ForeignKey(Petition, on_delete=models.CASCADE, null=True, blank=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True, blank=True)
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        target = self.petition or self.comment
        return f"Report by {self.reported_by.username} on {target}"

#NOTIFICA
class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    message = models.CharField(max_length=255)
    link = models.URLField(blank=True, null=True)  # link opzionale a petizione o altro
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notifica per {self.user.username}: {self.message[:30]}"

#VISUALIZZAZIONE
class PetitionView(models.Model):
    petition = models.ForeignKey(Petition, on_delete=models.CASCADE, related_name='views')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('petition', 'user')

    def __str__(self):
        return f"View of '{self.petition.title}' by {self.user.username if self.user else 'Anonymous'}"

#MODERAZIONE
class ModerationAction(models.Model):
    class ActionType(models.TextChoices):
        APPROVE = 'APPROVE', 'Approvata'
        REJECT = 'REJECT', 'Rifiutata'
        DELETE = 'DELETE', 'Cancellata'
        FLAG = 'FLAG', 'Segnalata'
        ARCHIVE = 'ARCHIVE', 'Archiviata'

    moderator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    petition = models.ForeignKey(Petition, on_delete=models.CASCADE)
    action = models.CharField(max_length=20, choices=ActionType.choices)
    reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.moderator} -> {self.get_action_display()} on '{self.petition.title}'"

#AUDIT LOG
class AuditLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    def __str__(self):
        return f"{self.user} - {self.action} at {self.timestamp}"
