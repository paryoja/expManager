from .models import Dataset, ExpItem, DataList, DataContainment
from projectManager.utils import toDictionary

class ExpContainer:
    def __init__(self, cont_list, query_name_list, param_list, result_title):
        self.alg_list = []
        self.query_list = []
        self.param_list = []
        self.value_list = []
        self.data_list = []
        self.data_length = len(cont_list)
        self.result_title = result_title

        # for each dataset in the datalist
        data_index = 0
        value_map = {}
        for cont in cont_list:
            exp_items = ExpItem.objects.filter(dataset=cont.dataset)
            self.data_list.append( cont.dataset.name ) 

            
            # for each exp for the dataset 
            for exp in exp_items:
                # parameter consists of algorithm, version, and project specific parameters
                alg = [ exp.algorithm.name, exp.algorithm.version ]

                param_dict = toDictionary(exp.parameter)
                param = []
                for p in param_list:
                    param.append( param_dict[p] )

                query = []
                for q in query_name_list:
                    query.append( param_dict[q] )

                self.add_result(query, param, alg, toDictionary(exp.result), value_map, self.result_title, data_index)
            data_index += 1

        self.value_list = self.toValueList(value_map)


    def toValueList(self, value_map):
        value_list = []
        
        for query in range(len(self.query_list)):
            #print( "query " + str(self.query_list[ query ]) )
            value_query = []

            for alg in range(len(self.alg_list)):
                #print( "alg " + str(self.alg_list[alg]))
                value_alg = []

                for data in range(self.data_length):
                    #print( "data " + str(data))
                    value_data = []

                    for param in range(len(self.param_list[alg])):
                        #print( "param " + str(self.param_list[alg][param]))
                        try:
                            value_data.append( value_map[(query, param, alg, data)] )  
                        except KeyError:
                            value_data.append( "" )

                    value_alg.append( (self.data_list[data], value_data) )
                value_query.append((str(self.alg_list[alg]),self.param_list[alg],value_alg))
            value_list.append((str(self.query_list[query]),value_query))
        return value_list

    def getResult(self):
        return self.query_list, self.param_list, self.alg_list, self.value_list


    def add_result(self, query, param, alg, result, value_map, result_title, data_index):
        if alg not in self.alg_list:
            self.alg_list.append(alg)
            self.param_list.append([])
        alg_index = self.alg_list.index(alg)

        if query not in self.query_list:
            self.query_list.append(query)
        query_index = self.query_list.index(query)

        if param not in self.param_list[alg_index]:
            self.param_list[alg_index].append(param)
        param_index = self.param_list[alg_index].index(param)

        value_map[(query_index, param_index, alg_index, data_index)] = result[result_title]

