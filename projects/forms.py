from django import forms
from django.core.exceptions import ValidationError
from .models import Project, ProjectMembership
from datetime import date


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description', 'start_date', 'deadline', 'status',
                  'priority', 'budget', 'hours_estimated', 'is_public', 'technologies']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter project name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Describe your project'
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'deadline': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'budget': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Budget in USD'
            }),
            'hours_estimated': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Estimated hours'
            }),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'technologies': forms.SelectMultiple(attrs={
                'class': 'form-select',
                'size': 5
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        deadline = cleaned_data.get('deadline')

        if start_date and deadline and deadline < start_date:
            raise ValidationError({
                'deadline': 'Deadline cannot be earlier than start date.'
            })

        return cleaned_data


