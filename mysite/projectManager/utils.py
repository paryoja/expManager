import json
from json import JSONDecodeError


def toList(result):
    try:
        dumped = json.loads(result)
    except JSONDecodeError:
        return []
    return list(dumped.items())


def toDictionary(result):
    try:
        dumped = json.loads(result)
    except JSONDecodeError:
        return {}
    return dumped


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

    resultFilter = dataset.project.getResultFilter()

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
                    total += float(resultDictionary[exp][par])
                    count += 1

                result.append(total / count)
            # append count
            result.append(count)
            avg_alg_list[(key, k)] = result

    # count
    resultFilter.append('count')

    context['avg_alg_list'] = sorted(avg_alg_list.items(), key=lambda x: (x[0][0][1] is None, x))
    context['param_filter'] = paramFilter
    context['result_filter'] = resultFilter

    return context

