import json
from json import JSONDecodeError


def toList(result):
    try:
        dumped = json.loads(result)
    except JSONDecodeError:
        return []
    return list(dumped.items())


def appendDict(result, appendDict, index):
    if index == 0:
        for key, value in appendDict.items():
            result[key] = [value]

    else:
        for key, value in result.items():
            if key in appendDict:
                value.append(appendDict[key])
            else:
                value.append('')
        for key, value in appendDict.items():
            if key not in result:
                noneList = []
                for i in range(index):
                    noneList.append('')
                noneList.append(value)
                result[key] = noneList


def toDictionary(result):
    try:
        dumped = json.loads(result)
    except JSONDecodeError:
        return {}
    return dumped


def splitColon(itemList, index):
    for i in range(len(itemList)):
        if ':' in itemList[i]:
            itemList[i] = itemList[i].split(':')[index]
    return itemList


def getDatasetContextData(context):
    from .models import ExpItem
    dataset = context['dataset']
    expList = ExpItem.objects.filter(dataset=dataset)

    paramFilter = dataset.project.getParamFilter()

    exp_alg_list = {}
    for exp in expList:
        alg = exp.algorithm
        server = exp.server
        if (alg, server) in exp_alg_list:
            alg_param = exp_alg_list[(alg, server)]
        else:
            alg_param = {}
            exp_alg_list[(alg, server)] = alg_param

        exp_param = tuple(exp.toParamValueList())

        if exp_param in alg_param:
            alg_param[exp_param].append(exp)
        else:
            alg_param[exp_param] = [exp]

    resultFilter = dataset.project.getResultFilterOriginalName()

    avg_alg_list = {}
    for key, val in exp_alg_list.items():
        for k, v in val.items():
            result = []

            resultDictionary = {}
            for exp in v:
                resultDictionary[exp] = toDictionary(exp.result)

            for par in resultFilter:
                total = 0.0
                count = 0.0
                for exp in v:
                    try:
                        total += float(resultDictionary[exp][par])
                        count += 1
                    except KeyError:
                        pass

                if count != 0:
                    result.append(total / count)
                else:
                    result.append(total)
            # append count
            result.append(count)
            avg_alg_list[(key, k)] = result

    # count
    resultFilter.append('count')

    context['avg_alg_list'] = sorted(avg_alg_list.items(), key=lambda x: (x[0][0][1] is None, x))
    context['param_filter'] = paramFilter
    context['result_filter'] = resultFilter

    return context
