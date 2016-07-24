from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.views import generic

from .models import Algorithm, Project, TodoItem, Dataset, ExpItem, Server, ExpTodo
from .utils import *


# Create your views here.

def index(request):
    return render(request, 'projectManager/index.html', {
                'project_list': Project.objects.all(), 
                'todo_list': TodoItem.objects.filter(level=0).filter(done=False),
                'server_list': Server.objects.all()})


class ServerView(generic.DetailView):
    model = Server
    template_name = 'projectManager/servers.html'


class DetailView(generic.DetailView):
    model = Project
    template_name = 'projectManager/detail.html'


class ExpView(generic.DetailView):
    model = Project
    template_name = 'projectManager/exp.html'


def exp(request, pk):
    expitem = ExpItem.objects.get(pk=pk)
    parameterList = toList( expitem.parameter )
    parsedResult = toList( expitem.result )
    return render(request, 'projectManager/expDetail.html', {
                'expitem': expitem,
                'parameterList': parameterList,
                'parsedResult': parsedResult
                })

class ExpDetailView(generic.DetailView):
    model = ExpItem
    template_name = 'projectManager/expDetail.html'


# add items
def addTodo(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    text = request.POST['todo_text']
    if text == "": 
        return render(request, 'projectManager/detail.html',
                {'project': project, 'error_message': 'Todo text is empty'})
    date = request.POST['deadline_date'] + " " + request.POST['deadline_time'] + ":00"
    level = request.POST['level']
    todo = TodoItem(project=project, todo_text=text, level=level, pub_date=timezone.now(), deadline_date=date, done=False )
    todo.save()
    return HttpResponseRedirect(reverse('project:detail', args=(project_id,)))


def addProject(request):
    project_text = request.POST['project_text']
    has_experiments = request.POST['has_experiments'] == "True"
    project = Project( project_text=project_text, pub_date=timezone.now(), has_experiments=has_experiments)
    project.save()
    return HttpResponseRedirect(reverse('project:index'))


def addServer(request):
    server_name = request.POST['server_name']
    server_ip = request.POST['server_ip']
    server = Server( server_name=server_name, server_ip=server_ip)
    server.save()
    return HttpResponseRedirect(reverse('project:index'))


def addExp(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    dataset = get_object_or_404(Dataset, pk=request.POST['dataset_name'])
    algorithm = get_object_or_404(Algorithm, pk=request.POST['algorithm_name'])
    exp_date = request.POST['pub_date']
    parameter = request.POST['parameter']
    result = request.POST['result']
    print(request.POST)

    expitem = ExpItem( project=project, dataset=dataset, algorithm=algorithm, exp_date=exp_date, parameter=parameter, result=result )
    expitem.save()

    return HttpResponseRedirect(reverse('project:exp', args=(project_id,)))


# modify items
def modifyTodo(request, project_id, todo_id):
    todo = get_object_or_404(TodoItem, pk=todo_id)

    print( request )
    if request.POST['method'] == 'Done':
        todo.done = True
        todo.save()
    elif request.POST['method'] == 'Delete':
        todo.delete()
    
    return HttpResponseRedirect(reverse('project:detail', args=(project_id,)))


def addForm(request):
    return render(request, 'projectManager/addForm.html' )


def addServerForm(request):
    return render(request, 'projectManager/addServerForm.html')


def expForm(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    return render(request, 'projectManager/addExpForm.html', {
        'project': project
        })


def deleteTodo(request, project_id, todo_id):
    return HttpResponse(str(request.POST))


def addAlgorithm(request, project_id):
    return HttpResponse('')


def algorithmForm(request, project_id):
    return render(request, 'projectManager/algorithmForm.html')


def addDataset(request, project_id):
    return HttpResponse('')


def datasetForm(request, project_id):
    return HttpResponse('')
