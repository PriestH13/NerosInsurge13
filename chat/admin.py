from django.contrib import admin
from .models import GlobalChatMessage, PrivateConversation, PrivateMessage, Group, GroupMembership, GroupMessage

@admin.register(GlobalChatMessage)
class GlobalChatMessageAdmin(admin.ModelAdmin):
    list_display = ('message_id', 'sender', 'content_preview', 'timestamp', 'is_edited')
    list_filter = ('timestamp', 'is_edited')
    search_fields = ('sender__username', 'content')
    readonly_fields = ('message_id', 'timestamp')
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Contenuto'

@admin.register(PrivateConversation)
class PrivateConversationAdmin(admin.ModelAdmin):
    list_display = ('conversation_id', 'participant1', 'participant2', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('participant1__username', 'participant2__username')
    readonly_fields = ('conversation_id', 'created_at')

@admin.register(PrivateMessage)
class PrivateMessageAdmin(admin.ModelAdmin):
    list_display = ('message_id', 'conversation', 'sender', 'content_preview', 'timestamp', 'is_read', 'is_edited')
    list_filter = ('timestamp', 'is_read', 'is_edited')
    search_fields = ('sender__username', 'content', 'conversation__conversation_id')
    readonly_fields = ('message_id', 'timestamp')
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Contenuto'

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('group_id', 'name', 'creator', 'created_at', 'member_count')
    list_filter = ('created_at',)
    search_fields = ('name', 'description', 'creator__username')
    readonly_fields = ('group_id', 'created_at', 'updated_at')
    
    def member_count(self, obj):
        return obj.members.count()
    member_count.short_description = 'Numero di membri'

@admin.register(GroupMembership)
class GroupMembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'group', 'is_admin', 'joined_at')
    list_filter = ('is_admin', 'joined_at')
    search_fields = ('user__username', 'group__name')
    readonly_fields = ('joined_at',)

@admin.register(GroupMessage)
class GroupMessageAdmin(admin.ModelAdmin):
    list_display = ('message_id', 'group', 'sender', 'content_preview', 'timestamp', 'is_edited')
    list_filter = ('timestamp', 'is_edited')
    search_fields = ('sender__username', 'content', 'group__name')
    readonly_fields = ('message_id', 'timestamp')
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Contenuto'