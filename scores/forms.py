from django import forms
from .models import Score, Group


class ScoreUploadForm(forms.ModelForm):
    class Meta:
        model = Score
        fields = ['name', 'author', 'groups', 'file']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Score name',
            }),
            'author': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Author (optional)',
            }),
            'groups': forms.SelectMultiple(attrs={
                'class': 'form-control',
            }),
            'file': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': '.xml,.musicxml,.mxl',
            }),
        }

    def clean_file(self):
        f = self.cleaned_data.get('file')
        if f:
            ext = f.name.rsplit('.', 1)[-1].lower()
            if ext not in ('xml', 'musicxml', 'mxl'):
                raise forms.ValidationError('Only MusicXML files (.xml, .musicxml, .mxl) are allowed.')
        return f


class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Group name',
            }),
        }


class LoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Email',
        'autofocus': True,
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Password',
    }))
