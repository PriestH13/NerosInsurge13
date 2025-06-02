from django import forms
from .models import Petition, PetitionCategory, Tag

class PetitionForm(forms.ModelForm):
    class Meta:
        model = Petition
        fields = ['title', 'description', 'category', 'tags', 'image','status']
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
