from django.views import generic
from django.core.urlresolvers import reverse
from django.shortcuts import render, get_object_or_404 
from django.http import HttpResponse, HttpResponseRedirect
from django.utils import timezone

from .models import Project, ExpItem, Server, TodoItem


# Create your views here.

class IndexView(generic.ListView):
    template_name = 'projectManager/index.html'
    context_object_name = 'project_list'

    def get_queryset(self):
        return Project.objects.all()


class ServerView(generic.ListView):
    template_name = 'projectManager/servers.html'
    context_object_name = 'server_list'

    def get_queryset(self):
        return Server.objects.all()


class DetailView(generic.DetailView):
    model = Project
    template_name = 'projectManager/detail.html'


class ExpView(generic.DetailView):
    model = Project
    template_name = 'projectManager/exp.html'


def addTodo(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    text = request.POST['todo_text']
    date = request.POST['deadline_date']
    level = request.POST['level']
    todo = TodoItem(project=project, todo_text=text, level=level, pub_date=timezone.now(), deadline_date=date )
    todo.save()
    return HttpResponseRedirect(reverse('project:detail', args=(project_id,)))
    

def deleteTodo(request, project_id, todo_id):
    return HttpResponse( str( request.POST ) )


def addForm(request):
    return HttpResponse( "" )


def addProject(request):
    return HttpResponse( "" )
