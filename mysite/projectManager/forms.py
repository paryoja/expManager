from django import forms

from .models import Project

class ProjectEditForm(forms.ModelForm):
    class Meta:
        model = Project
        exclude = ['git_url']
