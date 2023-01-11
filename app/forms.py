from django import forms
from .models import UserFile
from django import forms


class FileForm(forms.ModelForm):
    file = forms.FileField(widget=forms.ClearableFileInput(attrs={"multiple": True}))

    class Meta:
        model = UserFile
        fields = ["file"]


class EmailAuthenticationForm(forms.Form):
    email = forms.EmailField()

    def clean(self):
        email = self.cleaned_data.get("email")
        return self.cleaned_data


class DocumentTypeForm(forms.Form):
    DOCUMENT_TYPE_CHOICES = [
        ("australia_passport", "Australia Passport"),
        ("canada_passport", "Canada Passport"),
        ("canada_visa", "Canada Visa"),
        ("china_visa", "China Visa"),
        ("european_union_passport", "European Union Passport"),
        ("japan_visa", "Japan Visa"),
        ("india_visa", "India Visa"),
        ("schengen_visa", "Schengen Visa"),
        ("us_visa", "US Visa"),
        ("us_passport", "US Passport"),
    ]
    document_type = forms.ChoiceField(choices=DOCUMENT_TYPE_CHOICES)
