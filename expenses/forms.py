from django import forms

from .models import Category, Expense


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['title', 'amount', 'category', 'paid_by', 'split_type', 'date', 'notes', 'receipt_image']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, group=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.group = group
        if group is not None:
            self.fields['paid_by'].queryset = group.members.all()
        if not Category.objects.exists():
            self.fields['category'].required = False