from django import forms
from django.core.exceptions import ValidationError
from .models import Project, ProjectMembership
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
                'placeholder': 'Enter budget in USD'
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
        labels = {
            'hours_estimated': 'Estimated Hours',
            'is_public': 'Make this project public',
        }
        help_texts = {
            'deadline': 'Project deadline date',
            'technologies': 'Hold Ctrl/Cmd to select multiple',
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
    def clean_budget(self):
        budget = self.cleaned_data.get('budget')
        if budget and budget < 0:
            raise ValidationError('Budget cannot be negative.')
        return budget
    #TODO test if the hours are correct
    def clean_hours_estimated(self):
        hours = self.cleaned_data.get('hours_estimated')
        if hours and hours < 0:
            raise ValidationError('Estimated hours cannot be negative.')
        if hours and hours > 10000:
            raise ValidationError('Estimated hours seem too high. Please verify.')
        return hours
class ProjectMembershipForm(forms.ModelForm):
    class Meta:
        model = ProjectMembership
        fields = ['role', 'is_active']
        widgets = {
            'role': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'user' in self.fields:
            self.fields['user'].disabled = True



