import sys
from collections import defaultdict
from urllib.request import urlopen
from wsgiref.util import FileWrapper

import git
from dateutil.parser import parse
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import generic

from .forms import *
from .models import Algorithm, TodoItem, Dataset, ExpItem, Server, RelatedWork
from .utils import *


# Create your views here.
@login_required
def index(request):
    unfinished = TodoItem.objects.filter(done=False)
    return render(request, 'projectManager/index.html', {
        'project_list': Project.objects.all(),
        'todo_list': unfinished.filter(level=0).order_by('deadline_date'),
        'overdued_todo_list': unfinished.filter(deadline_date__lt=timezone.now()).order_by('deadline_date'),
        'algorithm_list': Algorithm.objects.all().order_by('project'),
        'server_list': Server.objects.all().order_by('server_ip'),
        'bookmark_list': BookMark.objects.all().order_by('-times_visited')
    })


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

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(DetailView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        context['todo_list'] = context['project'].todoitem_set.filter(done=False).order_by('level')
        context['completed_list'] = context['project'].todoitem_set.filter(done=True).order_by('-completed_date')
        context['related_list'] = context['project'].relatedwork_set.all()

        return context


class ExpView(generic.DetailView):
    model = Project
    template_name = 'projectManager/exp.html'

    def get_context_data(self, **kwargs):
        context = super(ExpView, self).get_context_data(**kwargs)
        context['exp_list'] = context['project'].expitem_set.order_by('-exp_date')[:10]
        context['dataset_list'] = context['project'].dataset_set.order_by('name')
        context['datasetlist_list'] = context['project'].datasetlist_set.order_by('name')

        return context


class AlgorithmDetailView(generic.DetailView):
    model = Algorithm
    template_name = 'projectManager/algorithmDetail.html'

    def get_context_data(self, **kwargs):
        context = super(AlgorithmDetailView, self).get_context_data(**kwargs)
        context['exp_list'] = context['algorithm'].expitem_set.all()
        context['project'] = context['algorithm'].project
        context['skip_algorithm'] = True

        return context


class DatasetDetailView(generic.DetailView):
    model = Dataset
    template_name = 'projectManager/datasetDetail.html'

    def get_context_data(self, **kwargs):
        context = super(DatasetDetailView, self).get_context_data(**kwargs)

        context = getDatasetContextData(context)
        context['exp_list'] = context['dataset'].expitem_set.all()
        context['project'] = context['dataset'].project
        context['skip_dataset'] = True
        return context




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


def addProjectWithForm(request):
    if request.method == 'GET':
        edit_form = ProjectEditForm()
    elif request.method == 'POST':
        edit_form = ProjectEditForm(request.POST)

        if edit_form.is_valid():
            edit_form.save()

            return HttpResponseRedirect(reverse('project:index'))
    return render(request, 'projectManager/form/addProjectForm.html',
                  {'form': edit_form})


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

    if is_synthetic == 'true':
        is_synthetic = 'True'
    elif is_synthetic == 'false':
        is_synthetic = 'False'

    if 'synthetic_parameters' in request.POST:
        synthetic_parameters = request.POST['synthetic_parameters']
    else:
        synthetic_parameters = ""
    data_info = request.POST['data_info']

    if 'file_size' in request.POST.keys():
        file_size = int(request.POST['file_size'])
    else:
        file_size = 0

    dataset = Dataset(project=project, name=name, is_synthetic=is_synthetic, synthetic_parameters=synthetic_parameters, data_info=data_info,
                      size=file_size)

    dataset.save()
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



def invalidateOld(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    all_alg = Algorithm.objects.filter(project=project)

    alg_map = defaultdict(list)
    new_alg_list = []

    for alg in all_alg:
        if not alg.isNewest():
            old = alg_map[alg.name]
            old.append(alg)
        else:
            new_alg_list.append(alg)

    alg_list = []
    for alg in new_alg_list:
        alg_list.append((alg.name, alg, alg_map[alg.name]))

    alg_list = sorted(alg_list, key=lambda x: x[0])

    return render(request, 'projectManager/invalidateOld.html',
                  {'project': project, 'alg_list': alg_list})


def invalidateOldAction(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    all_alg = Algorithm.objects.filter(project=project)

    for alg in all_alg:
        if not alg.isNewest():
            exps = ExpItem.objects.filter(algorithm=alg)
            for exp in exps:
                if not exp.invalid:
                    exp.invalid = True
                    exp.save()
    return HttpResponseRedirect(reverse('project:exp', args=(project_id,)))


def addGitUrl(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if project.git_url is None:
        url = request.POST['url']

        from subprocess import call
        returnValue = call(['git', 'ls-remote', request.POST['url']])

        if returnValue != 0:
            # message = request.POST['url'] + ' is not a valid url'
            return HttpResponseRedirect(reverse('project:detail', args=(project_id,)))

        project.git_url = url
        project.save()
    return HttpResponseRedirect(reverse('project:detail', args=(project_id,)))


def addForm(request):
    return render(request, 'projectManager/form/addForm.html')


def addServerForm(request):
    return render(request, 'projectManager/form/addServerForm.html')


def deleteTodo(request, project_id, todo_id):
    return HttpResponse(str(request.POST))


def algorithmForm(request, project_id):
    return render(request, 'projectManager/form/algorithmForm.html', {
        'project_id': project_id
    })


def datasetForm(request, project_id):
    return render(request, 'projectManager/form/datasetForm.html', {
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


def getAlgorithmId(request, project_id, algorithm_name, algorithm_version):
    project = get_object_or_404(Project, pk=project_id)
    try:
        algorithm = Algorithm.objects.filter(project=project).filter(name=algorithm_name).get(version=algorithm_version)
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


def eclipseSetting(request):
    return render(request, 'projectManager/setting/eclipseSetting.html')


def ubuntuPreseed(request):
    return render(request, 'projectManager/setting/ubuntuPreseed.html')


def jupyterSetting(request):
    return render(request, 'projectManager/setting/jupyterSetting.html')


def expUploader(request):
    g = git.cmd.Git('projectManager/static/projectManager/expUploader/ExperimentUploader')
    g.pull()

    filename = 'projectManager/static/projectManager/expUploader/ExperimentUploader/uploadExperiment.py'
    wrapper = FileWrapper(open(filename))
    response = HttpResponse(wrapper, content_type='text/x-python')
    response['Content-Length'] = os.path.getsize(filename)
    response['Content-Disposition'] = 'attachment; filename="uploadExperiment.py"'
    return response


def addBookMark(request):
    if request.method == 'GET':
        edit_form = BookMarkEditForm()
    elif request.method == 'POST':
        edit_form = BookMarkEditForm(request.POST)

        if edit_form.is_valid():
            edit_form.save()

            return HttpResponseRedirect(reverse('project:index'))

    return render(request, 'projectManager/form/addBookMark.html', {'form': edit_form})


def redirectBookMark(request, bookmark_id):
    bookmark = BookMark.objects.get(pk=bookmark_id)
    bookmark.times_visited += 1
    bookmark.save()
    return redirect(bookmark.url, permanent=True)


def showMap(request):
    return render(request, 'projectManager/map.html')


def addRelatedWork(request, pk):
    project = get_object_or_404(Project, pk=pk)
    title = request.POST['title']
    authors = request.POST['authors']
    url = request.POST['url']
    content = urlopen(url)
    name = getPDFName(url)
    related = RelatedWork(project=project, title=title, authors=authors, url=url)
    related.pdf_path.save(name, content)
    related.save()
    return HttpResponseRedirect(reverse('project:detail', args=(project.id,)))


def graph(request, pk):
    project = get_object_or_404(Project, pk=pk)
    resultFilter = project.getResultFilter()
    paramFilter = project.getParamFilter()
    algorithmList = project.algorithm_set.all()
    serverList = Server.objects.all().order_by('server_name')

    return render(request, 'projectManager/graph.html', {'project': project,
                                                         'resultFilter': resultFilter,
                                                         'paramFilter': paramFilter,
                                                         'algorithmList': algorithmList,
                                                         'serverList': serverList,
                                                         })


def addGraph(request, pk):
    project = get_object_or_404(Project, pk=pk)
    selected_result = request.POST['result']
    selected_param = request.POST['param']
    selected_algorithm = request.POST.getlist('algorithm')
    selected_server = request.POST['server']

    param_filter = project.getParamFilter()
    # exclude = {param_filter.index(selected_param)}

    distinct_options = {}
    server = Server.objects.filter(id=selected_server)
    for algorithm_id in selected_algorithm:
        algorithm = Algorithm.objects.get(id=algorithm_id)
        exp_list = project.expitem_set.filter(invalid=False).filter(algorithm=algorithm).filter(server=server)

        for exp in exp_list:
            param_list = exp.toParamValueList()
            param_str = exp.toOptionString(selected_param, param_filter)

            if param_str in distinct_options.keys():
                distinct_options[param_str].append(exp.id)
            else:
                distinct_options[param_str] = [exp.id]
            result_list = exp.toResultValueList()

    return render(request, 'projectManager/addGraph.html',
                  {'project': project,
                   'selected_result': selected_result,
                   'selected_param': selected_param,
                   'distinct_options': sorted(distinct_options.items()),
                   })


def graphExp(request, pk):
    project = get_object_or_404(Project, pk=pk)
    get = request.GET

    selected_param = get['selected_param']
    selected_result = get['selected_result']

    # param_filter = project.getParamFilter()
    exps = get['exp'].split(',')
    exp_list = []

    algorithm_map = {}
    param_set = set()

    for exp in exps:
        exp_model = get_object_or_404(ExpItem, pk=exp)
        exp_list.append(exp_model)
        result = float(toDictionary(exp_model.result)[selected_result])
        param = float(toDictionary(exp_model.parameter)[selected_param])
        algorithm = exp_model.algorithm

        if algorithm not in algorithm_map:
            algorithm_map[algorithm] = {}

        mapping = algorithm_map[algorithm]

        param_set.update({param})

        if param not in mapping:
            mapping[param] = result
        else:
            mapping[param] += result

    param_list = sorted(list(param_set))
    exp_result = []

    algorithm_list = sorted(list(algorithm_map.keys()))

    for param in param_list:
        entry = [param]
        for algorithm in algorithm_list:
            entry.append(algorithm_map[algorithm][param])

        exp_result.append(entry)

    return render(request, 'projectManager/graphExp.html', {
        'selected_param': selected_param,
        'selected_result': selected_result,
        'project': project,
        'exp_list': exp_list,
        'algorithms': algorithm_list,
        'exp_result': exp_result,
    })


def glossary(request):
    return render(request, 'projectManager/glossary/glossary_main.html')

