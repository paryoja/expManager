from dateutil.parser import parse
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.views import generic
from django.db.models import Q

from .models import Algorithm, Project, TodoItem, Dataset, ExpItem, Server
from .utils import *


# Create your views here.

def index(request):
    unfinished = TodoItem.objects.filter(done=False)
    return render(request, 'projectManager/index.html', {
        'project_list': Project.objects.all(),
        'todo_list': unfinished.filter(level=0).order_by('deadline_date'),
        'overdued_todo_list': unfinished.filter(deadline_date__lt=timezone.now()).order_by('deadline_date'),
        'algorithm_list': Algorithm.objects.all(),
        'server_list': Server.objects.all()})


class ListProjectView(generic.ListView):
    template_name = 'projectManager/json/listProjects.json'
    context_object_name = 'project_list'

    def get_queryset(self):
        return Project.objects.all


class ServerView(generic.DetailView):
    model = Server
    template_name = 'projectManager/servers.html'


class DetailView(generic.DetailView):
    model = Project
    template_name = 'projectManager/detail.html'

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        context['todo_list'] = context['project'].todoitem_set.filter(done=False).order_by('level')
        context['completed_list'] = context['project'].todoitem_set.filter(done=True).order_by('-completed_date')

        return context


class ExpView(generic.DetailView):
    model = Project
    template_name = 'projectManager/exp.html'

    def get_context_data(self, **kwargs):
        context = super(ExpView, self).get_context_data(**kwargs)
        context['latest_exp_list'] = context['project'].expitem_set.order_by('-exp_date')[:10]

        return context


class ExpListAllView(generic.DetailView):
    model = Project
    template_name = 'projectManager/expListAll.html'


class AlgorithmDetailView(generic.DetailView):
    model = Algorithm
    template_name = 'projectManager/algorithmDetail.html'


class DatasetDetailView(generic.DetailView):
    model = Dataset
    template_name = 'projectManager/datasetDetail.html'

    def get_context_data(self, **kwargs):
        context = super(DatasetDetailView, self).get_context_data(**kwargs)

        context = getDatasetContextData(context)
        return context


def exp(request, pk):
    expitem = ExpItem.objects.get(pk=pk)
    parameterList = toList(expitem.parameter)
    parsedResult = sorted( toList(expitem.result), key=lambda x: x[0])
    return render(request, 'projectManager/expDetail.html', {
        'expitem': expitem,
        'parameterList': parameterList,
        'parsedResult': parsedResult
    })


# add items
def addTodo(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    text = request.POST['todo_text']
    if text == "":
        return render(request, 'projectManager/detail.html',
                      {'project': project, 'error_message': 'Todo text is empty'})

    timeStr = request.POST['deadline_date'] + " " + request.POST['deadline_time'] + ":00 KST"
    date = parse(timeStr)
    if date < timezone.now():
        return render(request, 'projectManager/detail.html',
                      {'project': project, 'error_message': 'Invalid deadline ' + timeStr})

    level = request.POST['level']
    todo = TodoItem(project=project, todo_text=text, level=level, pub_date=timezone.now(), deadline_date=date,
                    done=False)
    todo.save()
    return HttpResponseRedirect(reverse('project:detail', args=(project_id,)))


def addProject(request):
    project_text = request.POST['project_text']
    if project_text == '':
        return render(request, 'projectManager/index.html',
                      {'project_list': Project.objects.all(),
                       'todo_list': TodoItem.objects.filter(level=0).filter(done=False),
                       'server_list': Server.objects.all(),
                       'error_message': 'Project name is empty'})
    has_experiments = request.POST['has_experiments'] == "True"
    project = Project(project_text=project_text, pub_date=timezone.now(), has_experiments=has_experiments)
    project.save()
    return HttpResponseRedirect(reverse('project:index'))


def addServer(request):
    server_name = request.POST['server_name']
    server_ip = request.POST['server_ip']

    try:
        server = Server.objects.get(server_name=server_name)
    except ObjectDoesNotExist:
        server = Server(server_name=server_name, server_ip=server_ip)

    server.save()
    return HttpResponseRedirect(reverse('project:index'))


def addAlgorithm(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    name = request.POST['name']
    version = request.POST['version']
    algorithm = Algorithm(project=project, name=name, version=version)
    algorithm.save()
    return HttpResponseRedirect(reverse('project:exp', args=(project_id,)))


def addDataset(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    name = request.POST['name']
    is_synthetic = request.POST['is_synthetic']
    synthetic_parameters = request.POST['synthetic_parameters']
    dataset = Dataset(project=project, name=name, is_synthetic=is_synthetic, synthetic_parameters=synthetic_parameters)
    dataset.save()
    return HttpResponseRedirect(reverse('project:exp', args=(project_id,)))


def addExp(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    dataset = get_object_or_404(Dataset, pk=request.POST['dataset_name'])
    algorithm = get_object_or_404(Algorithm, pk=request.POST['algorithm_name'])
    server = get_object_or_404(Server, pk=request.POST['server_name'])
    exp_date = parse(request.POST['pub_date'] + " KST")
    parameter = request.POST['parameter']
    result = request.POST['result']

    expitem = ExpItem(project=project, dataset=dataset, algorithm=algorithm, exp_date=exp_date, parameter=parameter,
                      result=result, server=server)
    expitem.save()

    return HttpResponseRedirect(reverse('project:exp', args=(project_id,)))


# modify items
def modifyTodo(request, project_id, todo_id):
    todo = get_object_or_404(TodoItem, pk=todo_id)

    if request.POST['method'] == 'Done':
        todo.done = True
        todo.completed_date = timezone.now()
        todo.save()
    elif request.POST['method'] == 'Delete':
        todo.delete()

    return HttpResponseRedirect(reverse('project:detail', args=(project_id,)))


def modifyExp(request, project_id, exp_id):
    exp = get_object_or_404(ExpItem, pk=exp_id)

    if request.POST['method'] == 'invalid':
        exp.invalid = True
        exp.save()
    elif request.POST['method'] == 'delete':
        exp.delete()

    return HttpResponseRedirect(reverse('project:expListAll', args=(project_id,)))


def addGitUrl(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if project.git_url is None:
        url = request.POST['url']

        from subprocess import call
        returnValue = call(['git', 'ls-remote', request.POST['url']])

        if returnValue != 0:
            message = request.POST['url'] + ' is not a valid url'
            return HttpResponseRedirect(reverse('project:detail', args=(project_id,)))

        project.git_url = url
        project.save()
    return HttpResponseRedirect(reverse('project:detail', args=(project_id,)))


def addForm(request):
    return render(request, 'projectManager/addForm.html')


def addServerForm(request):
    return render(request, 'projectManager/addServerForm.html')


def expForm(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    return render(request, 'projectManager/addExpForm.html', {
        'project': project
    })


def deleteTodo(request, project_id, todo_id):
    return HttpResponse(str(request.POST))


def algorithmForm(request, project_id):
    return render(request, 'projectManager/algorithmForm.html', {
        'project_id': project_id
    })


def datasetForm(request, project_id):
    return render(request, 'projectManager/datasetForm.html', {
        'project_id': project_id
    })


def listAlgorithms(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    return render(request, 'projectManager/json/listAlgorithms.json', {
        'algorithm_list': Algorithm.objects.filter(project=project)
    })


def listDatasets(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    return render(request, 'projectManager/json/listDatasets.json', {
        'dataset_list': Dataset.objects.filter(project=project)})


def getServerId(request, server_name):
    try:
        server = Server.objects.get(server_name=server_name)
    except ObjectDoesNotExist:
        return HttpResponse('-1')

    return HttpResponse(server.id)


def getProjectId(request, project_name):
    try:
        project = Project.objects.get(project_text=project_name)
    except ObjectDoesNotExist:
        return HttpResponse('-1')

    return HttpResponse(project.id)


def getAlgorithmId(request, project_id, algorithm_name):
    project = get_object_or_404(Project, pk=project_id)
    try:
        algorithm = Algorithm.objects.filter(project=project).get(name=algorithm_name)
    except ObjectDoesNotExist:
        return HttpResponse('-1')

    return HttpResponse(algorithm.id)


def getDatasetId(request, project_id, dataset_name):
    project = get_object_or_404(Project, pk=project_id)
    try:
        dataset = Dataset.objects.filter(project=project).get(name=dataset_name)
    except ObjectDoesNotExist:
        return HttpResponse('-1')

    return HttpResponse(dataset.id)


def hadoopSetting(request):
    return render(request, 'projectManager/setting/hadoopSetting.html')


def vimSetting(request):
    return render(request, 'projectManager/setting/vimSetting.html')


def hostSetting(request):
    return render(request, 'projectManager/setting/hostSetting.html', {
            'public_server_list': Server.objects.filter(~Q(server_ip__startswith='192.168')),
            'rsa_server_list': Server.objects.filter(rsa_pub__startswith='ssh')})
