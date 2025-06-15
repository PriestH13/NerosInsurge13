from django.contrib import admin
from .models import PetitionCategory, Tag, Petition, Signature, Comment, PetitionVote,PetitionAttachment, Report, Notification, PetitionView,ModerationAction, AuditLog


@admin.register(PetitionCategory)
class PetitionCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Petition)
class PetitionAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_by', 'status', 'category', 'created_at', 'is_active')
    list_filter = ('status', 'created_at', 'category')
    search_fields = ('title', 'description', 'created_by__username')
    autocomplete_fields = ('created_by', 'tags')




@admin.register(Signature)
class SignatureAdmin(admin.ModelAdmin):
    list_display = ('petition', 'email', 'signed_at')
    search_fields = ('petition__title', 'email')
    list_filter = ('signed_at',)



@admin.register(PetitionVote)
class PetitionVoteAdmin(admin.ModelAdmin):
    list_display = ('petition', 'user', 'is_upvote', 'voted_at')
    list_filter = ('is_upvote', 'voted_at')
    search_fields = ('petition__title', 'user__username')


@admin.register(PetitionAttachment)
class PetitionAttachmentAdmin(admin.ModelAdmin):
    list_display = ('petition', 'file', 'uploaded_at')
    search_fields = ('petition__title',)


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('reported_by', 'get_target', 'reason', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('reason', 'reported_by__username')

    def get_target(self, obj):
        return obj.petition or obj.comment
    get_target.short_description = 'Oggetto Segnalato'


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('user__username', 'message')


@admin.register(PetitionView)
class PetitionViewAdmin(admin.ModelAdmin):
    list_display = ('petition', 'user', 'viewed_at')
    list_filter = ('viewed_at',)
    search_fields = ('petition__title', 'user__username')


@admin.register(ModerationAction)
class ModerationActionAdmin(admin.ModelAdmin):
    list_display = ['moderator', 'petition', 'action', 'created_at']
    list_filter = ['action', 'created_at']
    search_fields = ['petition__title', 'moderator__username', 'reason']


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'timestamp', 'ip_address')
    search_fields = ('user__username', 'action', 'ip_address')
    list_filter = ('timestamp',)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('petition', 'user', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('content', 'user__username', 'petition__title')