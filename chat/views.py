from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import View, ListView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import HttpResponseBadRequest, JsonResponse
import json
from .models import GlobalChatMessage, PrivateConversation, PrivateMessage, Group, GroupMembership, GroupMessage
from auth_users.models import User
from .forms import GlobalChatMessageForm, PrivateMessageForm, GroupForm, GroupMessageForm, AddGroupMemberForm, SearchForm

class GlobalChatView(LoginRequiredMixin, View):
    template_name = 'chat/global_chat.html'

    def get(self, request, *args, **kwargs):
        form = GlobalChatMessageForm()
        messages = GlobalChatMessage.objects.all().order_by('-timestamp')[:50]
        return render(request, self.template_name, {
            'form': form,
            'messages': reversed(messages),  # Show oldest first
        })

    def post(self, request, *args, **kwargs):
        form = GlobalChatMessageForm(request.POST)
        if form.is_valid():
            GlobalChatMessage.objects.create(
                sender=request.user,
                content=form.cleaned_data['content']
            )
            return redirect('chat:global_chat')
        messages = GlobalChatMessage.objects.all().order_by('-timestamp')[:50]
        return render(request, self.template_name, {
            'form': form,
            'messages': reversed(messages),
        })

class GlobalMessagesAPI(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        messages = GlobalChatMessage.objects.all().order_by('-timestamp')[:50]
        data = [{
            'id': msg.id,
            'sender': {
                'username': msg.sender.username,
                'profile_picture': msg.sender.profile_picture.url if hasattr(msg.sender, 'profile_picture') and msg.sender.profile_picture else '/static/images/default_profile.png'
            },
            'content': msg.content,
            'timestamp': msg.timestamp.strftime("%H:%M"),
            'is_own': msg.sender == request.user
        } for msg in reversed(messages)]  # Oldest first
        
        return JsonResponse(data, safe=False)

class SendGlobalMessageAPI(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            content = data.get('content', '').strip()
            
            if not content:
                return JsonResponse({'status': 'error', 'message': 'Message cannot be empty'}, status=400)
                
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
                        'profile_picture': request.user.profile_picture.url if hasattr(request.user, 'profile_picture') and request.user.profile_picture else '/static/images/default_profile.png'
                    },
                    'content': message.content,
                    'timestamp': message.timestamp.strftime("%H:%M")
                }
            })
            
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

class PrivateConversationsView(LoginRequiredMixin, ListView):
    model = PrivateConversation
    template_name = 'chat/private_conversations.html'
    context_object_name = 'conversations'

    def get_queryset(self):
        return PrivateConversation.objects.filter(
            Q(participant1=self.request.user) | Q(participant2=self.request.user)
        ).order_by('-created_at')

class PrivateConversationDetailView(LoginRequiredMixin, View):
    template_name = 'chat/private_conversation_detail.html'

    def get(self, request, conversation_id, *args, **kwargs):
        conversation = get_object_or_404(PrivateConversation, conversation_id=conversation_id)
        if request.user not in [conversation.participant1, conversation.participant2]:
            return HttpResponseBadRequest("Non autorizzato")
        messages = conversation.messages.all().order_by('timestamp')
        messages.filter(sender__ne=request.user).update(is_read=True)
        form = PrivateMessageForm()
        return render(request, self.template_name, {'conversation': conversation, 'messages': messages, 'form': form})

    def post(self, request, conversation_id, *args, **kwargs):
        conversation = get_object_or_404(PrivateConversation, conversation_id=conversation_id)
        if request.user not in [conversation.participant1, conversation.participant2]:
            return HttpResponseBadRequest("Non autorizzato")
        form = PrivateMessageForm(request.POST)
        if form.is_valid():
            PrivateMessage.objects.create(conversation=conversation, sender=request.user, **form.cleaned_data)
            return redirect('chat:private_conversation_detail', conversation_id=conversation_id)
        messages = conversation.messages.all().order_by('timestamp')
        return render(request, self.template_name, {'conversation': conversation, 'messages': messages, 'form': form})

# Lista dei gruppi
class GroupListView(LoginRequiredMixin, ListView):
    model = Group
    template_name = 'chat/group_list.html'
    context_object_name = 'groups'

    def get_queryset(self):
        return Group.objects.filter(members=self.request.user).order_by('name')

class CreateGroupView(LoginRequiredMixin, View):
    template_name = 'chat/create_group.html'

    def get(self, request, *args, **kwargs):
        form = GroupForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = GroupForm(request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            group.creator = request.user
            group.save()
            GroupMembership.objects.create(user=request.user, group=group, is_admin=True)
            return redirect('chat:group_detail', group_id=group.group_id)
        return render(request, self.template_name, {'form': form})

class GroupDetailView(LoginRequiredMixin, View):
    template_name = 'chat/group_detail.html'

    def get(self, request, group_id, *args, **kwargs):
        group = get_object_or_404(Group, group_id=group_id)
        if request.user not in group.members.all():
            return HttpResponseBadRequest("Non sei membro di questo gruppo")
        messages = group.messages.all().order_by('timestamp')
        form = GroupMessageForm()
        member_form = AddGroupMemberForm(queryset=User.objects.exclude(id__in=group.members.all()).exclude(id=request.user.id))
        return render(request, self.template_name, {
            'group': group,
            'messages': messages,
            'form': form,
            'member_form': member_form
        })

    def post(self, request, group_id, *args, **kwargs):
        group = get_object_or_404(Group, group_id=group_id)
        if request.user not in group.members.all():
            return HttpResponseBadRequest("Non sei membro di questo gruppo")
        form = GroupMessageForm(request.POST)
        if form.is_valid():
            GroupMessage.objects.create(group=group, sender=request.user, **form.cleaned_data)
            return redirect('chat:group_detail', group_id=group_id)
        messages = group.messages.all().order_by('timestamp')
        member_form = AddGroupMemberForm(queryset=User.objects.exclude(id__in=group.members.all()).exclude(id=request.user.id))
        return render(request, self.template_name, {
            'group': group,
            'messages': messages,
            'form': form,
            'member_form': member_form
        })

class AddGroupMemberView(LoginRequiredMixin, View):
    def post(self, request, group_id, *args, **kwargs):
        group = get_object_or_404(Group, group_id=group_id)
        if not GroupMembership.objects.filter(group=group, user=request.user, is_admin=True).exists():
            return HttpResponseBadRequest("Solo gli admin possono aggiungere membri")
        form = AddGroupMemberForm(request.POST, queryset=User.objects.exclude(id__in=group.members.all()).exclude(id=request.user.id))
        if form.is_valid():
            user = form.cleaned_data['user']
            GroupMembership.objects.create(user=user, group=group)
            return redirect('chat:group_detail', group_id=group.group_id)
        return redirect('chat:group_detail', group_id=group.group_id)

class SearchProfilesAndGroupsView(LoginRequiredMixin, TemplateView):
    template_name = 'chat/search_results.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = SearchForm(self.request.GET)
        context['form'] = form
        query = self.request.GET.get('query', '') if form.is_valid() else ''
        context['query'] = query
        if query:
            context['users'] = User.objects.filter(
                Q(username__icontains=query) | Q(bio__icontains=query)
            ).exclude(id=self.request.user.id)
            context['groups'] = Group.objects.filter(
                Q(name__icontains=query) | Q(description__icontains=query)
            )
        else:
            context['users'] = User.objects.none()
            context['groups'] = Group.objects.none()
        return context

class StartConversationView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        user_id = request.POST.get('user_id')
        other_user = get_object_or_404(User, user_id=user_id)
        if other_user == request.user:
            return HttpResponseBadRequest("Non puoi iniziare una conversazione con te stesso")
        conversation = PrivateConversation.objects.filter(
            Q(participant1=request.user, participant2=other_user) |
            Q(participant1=other_user, participant2=request.user)
        ).first()
        if not conversation:
            conversation = PrivateConversation.objects.create(participant1=request.user, participant2=other_user)
        return redirect('chat:private_conversation_detail', conversation_id=conversation.conversation_id)