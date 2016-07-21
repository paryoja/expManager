from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import loader
from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from django.views import generic

from .models import Project, TodoItem, ExpItem


# Create your views here.

class IndexView(generic.ListView):
    template_name = 'projectManager/index.html'
    context_object_name = 'project_list'

    def get_queryset(self):
        return Project.objects.all()


class DetailView(generic.DetailView):
    model = Project
    template_name = 'projectManager/detail.html'


class ExpView(generic.DetailView):
    model = Project
    template_name = 'projectManager/exp.html'
