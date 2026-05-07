from django import forms
from .models import Letter


class LetterForm(forms.ModelForm):
    class Meta:
        model  = Letter
        fields = ('title', 'category', 'recipient_name', 'recipient_organization', 'body')
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Business Proposal – Tech Partnership',
            }),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'recipient_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Mr. John Smith',
            }),
            'recipient_organization': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Acme Corporation',
            }),
            'body': forms.Textarea(attrs={
                'class': 'form-control',
                'id': 'id_body',
                'rows': 16,
                'placeholder': 'Write your letter here. Be clear, professional, and detailed.\n\nMinimum 50 words required.',
            }),
        }
        labels = {
            'recipient_name': 'Recipient Name (optional)',
            'recipient_organization': 'Recipient Organization (optional)',
        }

    def clean_body(self):
        body = self.cleaned_data.get('body', '')
        word_count = len(body.split())
        if word_count < 50:
            raise forms.ValidationError(
                f"Letter is too short ({word_count} words). Please write at least 50 words."
            )
        return body
