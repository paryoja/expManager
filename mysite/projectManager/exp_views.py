import sys

from dateutil.parser import parse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from .misc import ExpContainer
from .models import Algorithm, Dataset, ExpItem, Server, Project, DataList, DataContainment, ServerList, ExpTodo
from .utils import toList, toDictionary, appendDict

import json


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
    if request.POST['dataset_name'] != "none":
        dataset = get_object_or_404(Dataset, pk=request.POST['dataset_name'])
    else:
        dataset = get_object_or_404(Dataset, pk=request.POST['dataset_id'])
    algorithm = get_object_or_404(Algorithm, pk=request.POST['algorithm_name'])
    server = get_object_or_404(Server, pk=request.POST['server_name'])
    try:
        exp_date = parse(request.POST['exp_date'])
    except KeyError:
        exp_date = timezone.now()
    parameter = request.POST['parameter']
    result = request.POST['result']

    try:
        is_failed = bool(request.POST['failed'])
    except:
        is_failed = False

    expitem = ExpItem(project=project, dataset=dataset, algorithm=algorithm, exp_date=exp_date, parameter=parameter,
                      result=result, server=server, failed=is_failed)

    expitem.save()
    try:
        redirect = request.POST['redirect']
        if redirect == 'rev':
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    except:
        return HttpResponse('uploaded')


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
    dataset_list = project.dataset_set.all().order_by('name')
    algorithm_list = project.algorithm_set.all().order_by('name')
    server_list = Server.objects.all()
    return render(request, 'projectManager/form/addExpForm.html', {
        'project': project, 'dataset_list': dataset_list, 'algorithm_list': algorithm_list,
        'server_list': server_list,
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
    serverlist_list = {}

    cont = DataContainment.objects.filter(data_list=datalist)

    for server in server_list:
        count = 0
        for dataset in cont:
            count += ExpItem.objects.filter(project=project, dataset=dataset.dataset, server=server, failed=False,
                                            invalid=False).count()

        if count != 0:
            filtered_server_list.append((count, server))
            if server.server_list is not None:
                if server.server_list not in serverlist_list:
                    serverlist_list[server.server_list] = (count, [server])
                else:
                    prev_count, prev_list = serverlist_list[server.server_list]
                    prev_list.append(server)
                    serverlist_list[server.server_list] = (prev_count + count, prev_list)
    filtered_server_list.sort(reverse=True)
    sorted_serverlist = sorted(serverlist_list.items(), key=lambda k: k[1])


    return render(request, 'projectManager/datalist/resultSelect.html', {
        'project': project, 'datalist': datalist, 'server_list': filtered_server_list,
        'serverlist_list': sorted_serverlist
    })


def datalistResult(request, project_id, datalist_id):
    project = get_object_or_404(Project, pk=project_id)
    datalist = get_object_or_404(DataList, pk=datalist_id)
    dataset_list = DataContainment.objects.filter(data_list=datalist)

    param_name_list = project.getParamFilterOriginalName()
    query_name_list = project.getQueryFilterOriginalName()

    server_or_serverlist_id = request.GET.get('server')
    method = request.GET.get('aggregation')

    server_list = []
    server = None
    serverlist = None
    if server_or_serverlist_id.startswith('sl_'): # sl_{{ serverlist.id }}
        # it is serverlist id
        serverlist = get_object_or_404(ServerList, pk=int(server_or_serverlist_id[3:]))
        for s in serverlist.server_set.all():
            server_list.append(s)
    else: # s_{{ server.id }}
        # it is server id
        server = get_object_or_404(Server, pk=int(server_or_serverlist_id[2:]))
        server_list.append(server)

    # since forloop.counter in template starts with 1 
    summary = int(request.GET.get('summary')) - 1
    result_title = project.getSummaryFilter()[summary]

    exp_cont = ExpContainer(dataset_list, query_name_list, param_name_list, result_title, server_list, method)
    exp_cont.load()
    query_list, param_list, alg_list, value_list = exp_cont.getResult()

    return render(request, 'projectManager/datalist/result.html', {
        'project': project, 'datalist': datalist, 'dataset_list': dataset_list,
        'value_list': value_list, 'result_title': result_title,
        'serverlist': serverlist, 'server': server, 'aggregation': method,
        's_sl_id': server_or_serverlist_id, 'summary': summary,
    })


def drawGraph(request, project_id, datalist_id, server_id):
    project = get_object_or_404(Project, pk=project_id)
    datalist = get_object_or_404(DataList, pk=datalist_id)
    dataset_list = DataContainment.objects.filter(data_list=datalist)

    post = request.POST
    server = None
    serverlist = None
    server_list = []
    if post['server_type'] == 'server':
        server = get_object_or_404(Server, pk=server_id)
        server_list.append( server )
    else:
        serverlist = get_object_or_404(ServerList, pk=server_id)
        for s in serverlist.server_set.all():
            server_list.append(s)

    query = post['query']
    alg_id_list = post.getlist('algorithm')
    result_title = post['result_title']
    log_scale = post.getlist('logscale')
    method = post['aggregation']

    alg_param_map = {}
    for alg in alg_id_list:
        algorithm = get_object_or_404(Algorithm, pk=alg)
        alg_param_map[algorithm.id] = [post['param_' + algorithm.name + '_' + algorithm.version]]

    param_name_list = project.getParamFilterOriginalName()
    query_name_list = project.getQueryFilterOriginalName()

    if "ms_to_s" in post:
        ms_to_s = True
    else:
        ms_to_s = False

    exp_cont = ExpContainer(dataset_list, query_name_list, param_name_list, result_title, server_list, method)
    exp_cont.load(alg_id_list=alg_id_list, selected_query=query, alg_param_map=alg_param_map)
    query_list, param_list, alg_list, debug_list = exp_cont.getResult()

    graph = exp_cont.save_to_graph(project, datalist, log_scale, ms_to_s)[0]

    return render(request, 'projectManager/datalist/drawGraph.html', {
        'project': project, 'datalist': datalist, 'server': server, 'serverlist': serverlist, 'query': query, 'algorithm_list': alg_list,
        'value_list': debug_list, 'graph': graph, 'result_title': result_title, 'summary': True
    })


def drawParamGraph(request, project_id, datalist_id, server_id, algorithm_id):
    project = get_object_or_404(Project, pk=project_id)
    datalist = get_object_or_404(DataList, pk=datalist_id)
    alg_id_list = [algorithm_id]
    dataset_list = DataContainment.objects.filter(data_list=datalist)

    post = request.POST

    server_list = []
    server = None
    serverlist = None
    if post['server_type'] == 'server':
        server = get_object_or_404(Server, pk=server_id)
        server_list.append( server )
    else:
        serverlist = get_object_or_404(ServerList, pk=server_id)
        for s in serverlist.server_set.all():
            server_list.append(s)

    query = post['query']
    result_title = post['result_title']
    log_scale = post.getlist('logscale')
    method = post['aggregation']

    alg_param_map = {}
    alg_param_map[int(algorithm_id)] = post.getlist('selected_param')

    param_name_list = project.getParamFilterOriginalName()
    query_name_list = project.getQueryFilterOriginalName()

    if "ms_to_s" in post:
        ms_to_s = True
    else:
        ms_to_s = False

    exp_cont = ExpContainer(dataset_list, query_name_list, param_name_list, result_title, server_list, method)
    exp_cont.load(alg_id_list=alg_id_list, selected_query=query, alg_param_map=alg_param_map)
    query_list, param_list, alg_list, debug_list = exp_cont.getResult()

    graph = exp_cont.save_to_param_graph(project, datalist, log_scale, ms_to_s)[0]

    return render(request, 'projectManager/datalist/drawGraph.html', {
        'project': project, 'datalist': datalist, 'server': server, 'serverlist': serverlist, 'query': query, 'algorithm_list': alg_list,
        'value_list': debug_list, 'graph': graph, 'result_title': result_title, 'summary': False
    })


def manageGraph(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    return render(request, 'projectManager/datalist/manageGraph.html', {
        'project': project
    })


def addExpTodo(request, project_id, datalist_id):
    project = get_object_or_404(Project, pk=project_id)
    datalist = get_object_or_404(DataList, pk=datalist_id)
    dataset_list = DataContainment.objects.filter(data_list=datalist)

    param_name_list = project.getParamFilterOriginalName()
    query_name_list = project.getQueryFilterOriginalName()

    if request.method == 'GET':
        server_or_serverlist_id = request.GET.get('server')
        method = None
    elif request.method == 'POST':
        server_or_serverlist_id = request.POST.get('server')


        selected_dataset_list = request.POST.getlist( 'dataset' )
        dataset_list = [ x for x in dataset_list if str(x.dataset.id) in selected_dataset_list ]
        method = "avg"

    result_title = project.getSummaryFilter()[0]

    server_list = []
    server = None
    serverlist = None
    if server_or_serverlist_id.startswith('sl_'): # sl_{{ serverlist.id }}
        # it is serverlist id
        serverlist = get_object_or_404(ServerList, pk=int(server_or_serverlist_id[3:]))
        for s in serverlist.server_set.all():
            server_list.append(s)
    else: # s_{{ server.id }}
        # it is server id
        server = get_object_or_404(Server, pk=int(server_or_serverlist_id[2:]))
        server_list.append(server)

    # since forloop.counter in template starts with 1 

    exp_cont = ExpContainer(dataset_list, query_name_list, param_name_list, result_title, server_list, method)

    if request.method == 'GET':
        exp_cont.load()
        query_list, param_list, alg_list, data_list = exp_cont.getList()

        int_list = list(range(len(alg_list)))
        sorted_param = []

        for alg_name, alg in list(sorted(zip(alg_list, int_list))):
            sorted_param.append((alg_name,sorted(param_list[alg])))

        return render(request, 'projectManager/datalist/addExpTodo.html', {
            'project': project, 'datalist': datalist, 'server_id': server_or_serverlist_id,
            'query_list': query_list, 'param_list': sorted_param, 'alg_list': alg_list, 'dataset_list': data_list,
            })

    else:
        selected_query_list = request.POST[ 'query' ]
        selected_algorithm_list = request.POST.getlist( 'algorithm' )
        
        selected_param_map = {}
        for alg in selected_algorithm_list:
            param_list = request.POST.getlist( 'param_list_' + alg )
            selected_param_map[ int(alg) ] = param_list
        
        exp_cont.load( alg_id_list = selected_algorithm_list, selected_query=selected_query_list, alg_param_map=selected_param_map)
        query_list, param_list, alg_list, data_list = exp_cont.getList()
        repeat = datalist.repeat

        for query_id, query in enumerate(query_list):
            for data_id, data in enumerate(data_list):
                dataset = get_object_or_404(Dataset, pk=data[1])
                for alg_id, alg in enumerate(alg_list):
                    algorithm = get_object_or_404(Algorithm, pk=alg[2])
                    for param_id, param in enumerate(param_list[alg_id]):
                        avg, count, total_count = exp_cont.getValue(query_id, param_id, alg_id, data_id)
                        
                        if count < repeat:
                            param_map = {}
                            for param_name_idx, param_name in enumerate(param_name_list):
                               param_map[param_name] = param[param_name_idx]

                            query_map = {}
                            for query_name_idx, query_name in enumerate(query_name_list):
                                query_map[query_name] = query[query_name_idx]
                            
                            json_param = json.dumps(param_map)
                            json_query = json.dumps(query_map)

                            # add exp todo
                            filtered = ExpTodo.objects.filter(project=project, algorithm=algorithm, dataset=dataset, serverlist=serverlist, server=server, parameter=json_param, query=json_query)
                            if len(filtered) == 0:
                                exp = ExpTodo(project=project, algorithm=algorithm, dataset=dataset, serverlist=serverlist, server=server, parameter=json_param, query=json_query)
                                exp.save()

        return HttpResponseRedirect(reverse('project:exp', args=(project.id,)))

def getExpTodoList(request, project_id):
    # find 
    project = get_object_or_404(Project, pk=project_id)
    server_id = request.POST['server_id']
    server = get_object_or_404(Server, pk = server_id)
    
    exp_list = ExpTodo.objects.filter(project=project, server=server, is_finished=False, is_running=False)
    if server.server_list is not None:
        exp_list_serverlist = ExpTodo.objects.filter(project=project, serverlist=server.server_list, is_finished = False, is_running = False)
        if len(exp_list_serverlist) != 0:
            exp_list = exp_list + exp_list_serverlist
    if len(exp_list) == 0:
        return HttpResponse("Nothing to do")
    else:
        return HttpResponse( ",".join(str(x.id) for x in exp_list) )


def getExpTodo(request, project_id, todo_id):
    project = get_object_or_404(Project, pk=project_id)
    todo = get_object_or_404(ExpTodo, pk=todo_id)
    if not todo.is_finished and not todo.is_running:
        return HttpResponse(todo.to_json())
    else:
        return HttpResponse("skip")


def getExpTodoStat(request, project_id, todo_id):
    todo = get_object_or_404(ExpTodo, pk=todo_id)

    return HttpResponse(todo.is_running + " " + todo.is_finished)

def modExpTodo(request, project_id, todo_id):

    todo = get_object_or_404(ExpTodo, pk=todo_id)
    if request.POST['method'] == 'running':
        todo.is_running = True
        todo.save()
        return HttpResponse("running")
    elif request.POST['method'] == 'finished':
        todo.is_finished = True
        todo.is_running = False
        todo.save()
        return HttpResponse("finished")
    return HttpResponse("method " + request.POST['method'])
        
