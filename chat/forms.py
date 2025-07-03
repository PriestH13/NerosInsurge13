from django import forms
from .models import GlobalChatMessage, PrivateMessage, Group, GroupMessage, GroupMembership
from auth_users.models import User

class GlobalChatMessageForm(forms.ModelForm):
    class Meta:
        model = GlobalChatMessage
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Scrivi un messaggio...'}),
        }

class PrivateMessageForm(forms.ModelForm):
    class Meta:
        model = PrivateMessage
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Scrivi un messaggio...'}),
        }

class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Nome del gruppo'}),
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Descrizione del gruppo (opzionale)'}),
        }

class GroupMessageForm(forms.ModelForm):
    class Meta:
        model = GroupMessage
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Scrivi un messaggio...'}),
        }

class AddGroupMemberForm(forms.Form):
    user = forms.ModelChoiceField(
        queryset=User.objects.all(),
        label='Utente da aggiungere',
        empty_label='Seleziona un utente'
    )

    def __init__(self, *args, queryset=None, **kwargs):
        super().__init__(*args, **kwargs)
        if queryset is not None:
            self.fields['user'].queryset = queryset

class SearchForm(forms.Form):
    query = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Cerca utenti o gruppi...'})
    )