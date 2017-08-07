from projectManager.models import *
from projectManager.utils import toDictionary


def getDatasetName( one, two, rule ):
    one_name = one.split('/')[-1]
    two_name = two.split('/')[-1]
    rule_name = rule.split('/')[-1]

    name = one_name
    if one_name == two_name:
        name += '_SelfJoin_wrt_'
    else:
        name += '_JoinWith_' + two_name + '_wrt_'

    name += rule_name
    return name 

project = Project.objects.get(project_text='SynonymRev')

algorithms = project.algorithm_set.all()
datasets = project.dataset_set.all()

algorithm_dic = {}
dataset_dic = {}

for algorithm in algorithms:
    algorithm_dic[ algorithm.name ] = algorithm

for dataset in datasets:
    dataset_dic[ dataset.name ] = dataset

for exp in ExpItem.objects.filter(project=project):
    result = toDictionary(exp.result)
    #print(result)
    if 'cmd_alg' in result:
        if exp.algorithm.name != result['cmd_alg']:
            print( result['cmd_alg'] )
            print( exp.algorithm.name )
            exp.algorithm = algorithm_dic[ result['cmd_alg'] ]
            print( algorithm_dic[ result['cmd_alg'] ].name )
            print( exp.algorithm.name )
            exp.save()
        
        dataset_name = getDatasetName(result['cmd_dataOnePath'], result['cmd_dataTwoPath'], result['cmd_rulePath'])
        if exp.dataset.name != dataset_name:
            print( exp.dataset.name )
            print( dataset_name )
            exp.dataset = dataset_dic[ dataset_name ]
            exp.save()
            


