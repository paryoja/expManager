import sys

from dateutil.parser import parse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render

from .models import Algorithm, Dataset, ExpItem, Server, Project
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
