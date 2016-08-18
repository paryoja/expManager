from django import forms

from .models import Project, BookMark

class ProjectEditForm(forms.ModelForm):
    class Meta:
        model = Project
        exclude = ['git_url']


class BookMarkEditForm(forms.ModelForm):
    class Meta:
        model = BookMark
        exclude = ['last_visit', 'times_visited']
