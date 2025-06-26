from django import forms
from .models import Petition, PetitionCategory, Tag, Signature, Report, ModerationAction, PetitionStatus

class PetitionForm(forms.ModelForm):
    class Meta:
        model = Petition
        fields = ['title', 'description', 'category', 'tags', 'image','status','location']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Enter petition title'}),
            'description': forms.Textarea(attrs={'placeholder': 'Describe your petition'}),
            'category': forms.Select(),
            'tags': forms.SelectMultiple(),
            'image': forms.ClearableFileInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].empty_label = "Select a category"
        self.fields['tags'].required = False
        self.fields['image'].required = False

class SignatureForm(forms.Form):
    email = forms.EmailField(label='La tua email')


from django import forms
from .models import Comment

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Scrivi un commento...'
            })
        }


class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['reason']
        widgets = {
            'reason': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Spiega il motivo della segnalazione...'}),}
        

class ModerationActionForm(forms.ModelForm):
    class Meta:
        model = ModerationAction
        fields = ['petition', 'action', 'reason']


class PetitionFilterForm(forms.Form):
    q = forms.CharField(required=False, label='Ricerca')
    category = forms.ModelChoiceField(
        queryset=PetitionCategory.objects.all(), required=False, empty_label='Tutte le categorie')
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(), required=False, widget=forms.CheckboxSelectMultiple)
    status = forms.ChoiceField(
        choices=[('', 'Tutti gli stati')] + list(PetitionStatus.choices), required=False)
    order = forms.ChoiceField(
        choices=[('recenti', 'Più recenti'), ('meno_recente', 'Meno recenti')], required=False)