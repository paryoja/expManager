import sys

from dateutil.parser import parse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render

from .misc import ExpContainer
from .models import Algorithm, Dataset, ExpItem, Server, Project, DataList, DataContainment
from .utils import toList, toDictionary, appendDict


def exp(request, pk):
    expitem = ExpItem.objects.get(pk=pk)
    parameterList = toList(expitem.parameter)
    parsedResult = sorted(toList(expitem.result), key=lambda x: x[0])
    return render(request, 'projectManager/expDetail.html', {
        'expitem': expitem,
        'parameterList': parameterList,
        'parsedResult': parsedResult
    })


def expListAll(request, pk):
    project = get_object_or_404(Project, pk=pk)
    exp_all = project.expitem_set.order_by('-id')

    paginator = Paginator(exp_all, 25)
    page = request.GET.get('page')

    try:
        exps = paginator.page(page)
    except PageNotAnInteger:
        exps = paginator.page(1)
    except EmptyPage:
        exps = paginator.page(paginator.num_pages)

    return render(request, 'projectManager/expListAll.html', {'project': project, 'exp_list': exps})


def listSameExp(request, project_id, dataset_id, algorithm_id):
    project = get_object_or_404(Project, pk=project_id)
    dataset = get_object_or_404(Dataset, pk=dataset_id)
    algorithm = get_object_or_404(Algorithm, pk=algorithm_id)

    param_filter = project.getParamFilter()
    param_list = []
    for par in param_filter:
        param = request.GET.get(par)
        param_list.append(param)

    exp_all_list = ExpItem.objects.filter(project=project).filter(algorithm=algorithm).filter(dataset=dataset)
    exp_list = []

    for exp in exp_all_list:
        skip = False
        param_exp = exp.toParamValueList()
        for par, val in zip(param_list, param_exp):
            if par != val:
                skip = True
                break
        if not skip:
            exp_list.append(exp)

    result_filter = project.getResultFilter()

    return render(request, 'projectManager/listSameExp.html', {
        'exp_list': exp_list,
        'param_filter': param_filter,
        'result_filter': result_filter})


def expCompare(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    expitems = sorted(request.GET.getlist('exp'))
    expList = []

    parameterListMap = {}
    resultListMap = {}
    index = 0
    for expId in expitems:
        exp = get_object_or_404(ExpItem, pk=expId)
        expList.append(exp)
        parameterList = toDictionary(exp.parameter)
        appendDict(parameterListMap, parameterList, index)

        resultList = toDictionary(exp.result)
        appendDict(resultListMap, resultList, index)

        index += 1

    sortedParameterList = sorted(list(parameterListMap.items()), key=lambda x: x[0])
    sortedResultList = sorted(list(resultListMap.items()), key=lambda x: x[0])
    sameValue = set()
    similarValue = set()
    singleValue = set()
    for (key, valueList) in sortedParameterList:
        startValue = valueList[0]
        same = True

        for value in valueList:
            if startValue != value:
                same = False
                break

        if same:
            sameValue.update({key})

    minMaxList = []
    for (key, valueList) in sortedResultList:
        startValue = valueList[0]
        same = True

        if startValue.isdigit() and startValue != '':
            minValue = startValue
            maxValue = startValue
            maxId = 0
            minId = 0
        else:
            minValue = sys.maxsize
            maxValue = -sys.maxsize

        nonEmptyCount = 0
        for idx, value in enumerate(valueList):
            if value != "":
                nonEmptyCount += 1
            if startValue != value:
                same = False

                if value.isdigit():
                    if float(minValue) > float(value):
                        minValue = value
                        minId = idx
                    if float(maxValue) < float(value):
                        maxValue = value
                        maxId = idx

        if float(minValue) != 0:
            ratio = float(maxValue) / float(minValue)
        else:
            ratio = ''

        if minValue == sys.maxsize:
            minValue = ''
            ratio = ''
        else:
            minValue = (minValue, minId)

        if maxValue == -sys.maxsize:
            maxValue = ''
            ratio = ''
        else:
            maxValue = (maxValue, maxId)

        if nonEmptyCount <= 1:
            singleValue.update({key})
        elif isinstance(ratio, float) and ratio < 1.1:
            similarValue.update({key})

        minMaxList.append((minValue, maxValue, ratio))

        if same:
            sameValue.update({key})

    zippedResult = zip(sortedResultList, minMaxList)
    return render(request, 'projectManager/expCompare.html', {
        'project': project,
        'expList': expList,
        'parameterList': sortedParameterList,
        'resultList': zippedResult,
        'sameValue': sameValue,
        'similarValue': similarValue,
        'singleValue': singleValue,
    })


def addExp(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    dataset = get_object_or_404(Dataset, pk=request.POST['dataset_name'])
    algorithm = get_object_or_404(Algorithm, pk=request.POST['algorithm_name'])
    server = get_object_or_404(Server, pk=request.POST['server_name'])
    exp_date = parse(request.POST['exp_date'])
    parameter = request.POST['parameter']
    result = request.POST['result']

    expitem = ExpItem(project=project, dataset=dataset, algorithm=algorithm, exp_date=exp_date, parameter=parameter,
                      result=result, server=server)
    expitem.save()

    return HttpResponseRedirect(reverse('project:exp', args=(project_id,)))


def modifyExp(request, project_id, exp_id):
    exp = get_object_or_404(ExpItem, pk=exp_id)

    if request.POST['method'] == 'invalid':
        exp.invalid = True
        exp.save()
    elif request.POST['method'] == 'delete':
        exp.delete()

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def expForm(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    return render(request, 'projectManager/form/addExpForm.html', {
        'project': project
    })


def datalistConfigure(request, project_id, datalist_id):
    project = get_object_or_404(Project, pk=project_id)
    datalist = get_object_or_404(DataList, pk=datalist_id)
    dataset_list = DataContainment.objects.filter(data_list=datalist)
    dataset_id_list = []
    for dataset in dataset_list:
        dataset_id_list.append(dataset.dataset.id)
    other_dataset = Dataset.objects.filter(project=project).exclude(id__in=dataset_id_list)

    return render(request, 'projectManager/datalist/configure.html', {
        'project': project, 'datalist': datalist, 'dataset_list': dataset_list, 'other_dataset_list': other_dataset
    })


def addToDataList(request, project_id, datalist_id, dataset_id):
    datalist = get_object_or_404(DataList, pk=datalist_id)
    dataset = get_object_or_404(Dataset, pk=dataset_id)
    contain = DataContainment(data_list=datalist, dataset=dataset)
    contain.save()

    return datalistConfigure(request, project_id, datalist_id)


def removeFromDataList(request, project_id, datalist_id, dataset_id):
    datalist = get_object_or_404(DataList, pk=datalist_id)
    dataset = get_object_or_404(Dataset, pk=dataset_id)
    contain = get_object_or_404(DataContainment, data_list=datalist, dataset=dataset)
    contain.delete()

    return datalistConfigure(request, project_id, datalist_id)


def datalistResultSelect(request, project_id, datalist_id):
    project = get_object_or_404(Project, pk=project_id)
    datalist = get_object_or_404(DataList, pk=datalist_id)

    server_list = Server.objects.all()
    filtered_server_list = []

    cont = DataContainment.objects.filter(data_list=datalist)

    for server in server_list:
        count = 0
        for dataset in cont:
            count += ExpItem.objects.filter(project=project, dataset=dataset.dataset, server=server, failed=False,
                                            invalid=False).count()

        if count != 0:
            filtered_server_list.append((count, server))

    filtered_server_list.sort(reverse=True)

    return render(request, 'projectManager/datalist/resultSelect.html', {
        'project': project, 'datalist': datalist, 'server_list': filtered_server_list
    })


def datalistResult(request, project_id, datalist_id):
    project = get_object_or_404(Project, pk=project_id)
    datalist = get_object_or_404(DataList, pk=datalist_id)
    dataset_list = DataContainment.objects.filter(data_list=datalist)

    param_name_list = project.getParamFilterOriginalName()
    query_name_list = project.getQueryFilterOriginalName()

    # TODO sanity check of GET parameters
    server_id = request.GET.get('server')
    # since forloop.counter in template starts with 1 
    result_title = project.getSummaryFilter()[int(request.GET.get('summary')) - 1]

    exp_cont = ExpContainer(dataset_list, query_name_list, param_name_list, result_title, server_id)
    exp_cont.load()
    query_list, param_list, alg_list, value_list = exp_cont.getResult()

    return render(request, 'projectManager/datalist/result.html', {
        'project': project, 'datalist': datalist, 'dataset_list': dataset_list,
        'value_list': value_list, 'result_title': result_title,
        'server': Server.objects.get(pk=server_id)
    })


def drawGraph(request, project_id, datalist_id, server_id):
    project = get_object_or_404(Project, pk=project_id)
    datalist = get_object_or_404(DataList, pk=datalist_id)
    server = get_object_or_404(Server, pk=server_id)
    dataset_list = DataContainment.objects.filter(data_list=datalist)

    post = request.POST
    query = post['query']
    alg_id_list = post.getlist('algorithm')
    result_title = post['result_title']
    log_scale = post.getlist('logscale')

    alg_param_map = {}
    for alg in alg_id_list:
        algorithm = get_object_or_404(Algorithm, pk=alg)
        alg_param_map[algorithm.id] = post['param_' + algorithm.name + '_' + algorithm.version]

    param_name_list = project.getParamFilterOriginalName()
    query_name_list = project.getQueryFilterOriginalName()

    if "ms_to_s" in post:
        ms_to_s = True
    else:
        ms_to_s = False

    exp_cont = ExpContainer(dataset_list, query_name_list, param_name_list, result_title, server_id)
    exp_cont.load(alg_id_list=alg_id_list,selected_query=query, alg_param_map=alg_param_map)
    query_list, param_list, alg_list, debug_list = exp_cont.getResult()

    graph = exp_cont.save_to_graph(project, datalist, log_scale, ms_to_s)
    #print(graph.graph_file.url)

    return render(request, 'projectManager/datalist/drawGraph.html', {
        'project': project, 'datalist': datalist, 'server': server, 'query': query, 'algorithm_list': alg_list,
        'value_list': debug_list, 'graph': graph, 'result_title': result_title
        })

def manageGraph(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    return render(request, 'projectManager/datalist/manageGraph.html', {
        'project': project
    })
