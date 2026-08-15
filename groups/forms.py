from django import forms

from .models import Group


class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name', 'description', 'image']


class AddMemberForm(forms.Form):
    username_or_email = forms.CharField(
        label="Username or email",
        max_length=150,
        help_text="The person must already have a SplitEase account.",
    )

    def clean_username_or_email(self):
        from accounts.models import User

        value = self.cleaned_data['username_or_email'].strip()
        user = (
            User.objects.filter(username=value).first()
            or User.objects.filter(email__iexact=value).first()
        )
        if not user:
            raise forms.ValidationError("No registered user found with that username or email.")
        if not user.is_active:
            raise forms.ValidationError("This user's account is inactive.")

        # Stash the resolved User object for the view to use — cleaned_data
        # for this field itself stays the raw string, which is fine.
        self.cleaned_data['user'] = user
        return value