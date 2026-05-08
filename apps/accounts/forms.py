from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Kyc


class RegisterForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "First name"}
        ),
    )
    last_name = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Last name"}
        ),
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": "Email address"}
        ),
    )

    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "username",
            "email",
            "password1",
            "password2",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if "class" not in field.widget.attrs:
                field.widget.attrs["class"] = "form-control"
        self.fields["username"].widget.attrs["placeholder"] = "Choose a username"
        self.fields["password1"].widget.attrs["placeholder"] = "Create password"
        self.fields["password2"].widget.attrs["placeholder"] = "Confirm password"


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "email",
            "phone",
            "country",
            "bio",
            "avatar",
        )
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "phone": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "+1 555 000 0000"}
            ),
            "country": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "e.g. United States"}
            ),
            "bio": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Tell us a bit about yourself...",
                }
            ),
            "avatar": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }


class PasswordChangeForm(forms.Form):
    current_password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Current password"}
        )
    )
    new_password = forms.CharField(
        min_length=8,
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "New password (min 8 chars)"}
        ),
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Confirm new password"}
        )
    )

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get("new_password")
        p2 = cleaned.get("confirm_password")
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("New passwords do not match.")
        return cleaned


class KycForm(forms.ModelForm):
    class Meta:
        model = Kyc
        fields = ["document_front", "document_back"]

    def clean_document_front(self):
        file = self.cleaned_data.get("document_front")
        if file and file.size > 5 * 1024 * 1024:
            raise forms.ValidationError("Front document must be under 5MB.")
        return file

    def clean_document_back(self):
        file = self.cleaned_data.get("document_back")
        if file and file.size > 5 * 1024 * 1024:
            raise forms.ValidationError("Back document must be under 5MB.")
        return file
