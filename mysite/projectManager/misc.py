import sys

from projectManager.utils import toDictionary
from django.conf import settings
from django.shortcuts import get_object_or_404

import os 
import re
from subprocess import call
import datetime
from .models import ExpItem, Server, Graph, Algorithm


class ExpContainer:
    def __init__(self, cont_list, query_name_list, param_name_list, result_title, server_id):
        self.alg_list = []
        self.query_list = []
        self.query_name_list = query_name_list
        self.param_list = []
        self.param_name_list = param_name_list
        self.value_list = []
        self.data_list = []
        self.data_length = len(cont_list)
        self.cont_list = cont_list
        self.result_title = result_title
        self.server = Server.objects.get(pk=server_id)

    def load(self, alg_id_list=None, selected_query=None, alg_param_map=None):
        self.alg_id_list = alg_id_list
        self.selected_query = selected_query
        self.alg_param_map = alg_param_map

        # for each dataset in the datalist
        data_index = 0
        self.value_map = {}
        for cont in self.cont_list:
            exp_items = ExpItem.objects.filter(dataset=cont.dataset, server=self.server, invalid=False, failed=False)
            self.data_list.append(cont.dataset.name)

            # for each exp for the dataset 
            for exp in exp_items:
                # parameter consists of algorithm, version, and project specific parameters
                if alg_id_list is not None:
                    if str(exp.algorithm.id) not in alg_id_list:
                        # skip this exp item
                        continue
                alg = [exp.algorithm.name, exp.algorithm.version, exp.algorithm.id]

                param_dict = toDictionary(exp.parameter)

                param = []
                for p in self.param_name_list:
                    param.append(param_dict[p])

                # check skip conditions based on alg_param_map
                if alg_param_map is not None:
                    if str(param[0]) != alg_param_map[exp.algorithm.id]:
                        continue

                query = []
                if self.query_name_list is not None:
                    for q in self.query_name_list:
                        query.append(param_dict[q])
                else:
                    query.append("None")

                # check skip conditions based on selected_query
                if selected_query is not None:
                    if str(query) != selected_query:
                        continue

                self.add_result(query, param, alg, toDictionary(exp.result), self.result_title, data_index)
            data_index += 1

        self.value_list = self.toValueList(self.value_map)

    def toValueList(self, value_map):
        value_list = []
        
        int_list = list(range(len(self.alg_list)))
        alg_sorted = list(sorted(zip(self.alg_list, int_list)))
        #print(alg_sorted)

        for query in range(len(self.query_list)):
            # print( "query " + str(self.query_list[ query ]) )
            value_query = []
            query_min_list = []
            
            query_min_list.append([['Algorithm'],""])
            #for alg in self.alg_list:
            for alg in alg_sorted:
                query_min_list[0][0].append(alg[0])
            
            #print(query_min_list)

            for data in range(self.data_length):
                query_min_list.append([[self.data_list[data]],sys.maxsize])

            # print(query_min_list)

            #for alg in range(len(self.alg_list)):
            for alg_name, alg in alg_sorted:

                #print( "alg " + str(self.alg_list[alg]))
                value_alg = []
                min_index = -1

                for data in range(self.data_length):
                    # print( "data " + str(data))
                    value_data = []

                    min_value = sys.maxsize
                    max_value = 0

                    int_list = list(range(len(self.param_list[alg])))
                    param_sorted = list(sorted(zip(self.param_list[alg],int_list)))
                    print(param_sorted)

                    for param_name, param in param_sorted:
                        print( "param " + str(self.param_list[alg][param]))
                        try:
                            value = int(self.value_map[(query, param, alg, data)])
                            if value < min_value:
                                min_value = value
                                min_index = param
                            if value > max_value:
                                max_value = value

                            if value < query_min_list[data + 1][1]:
                                query_min_list[data + 1][1] = value

                            value_data.append(value)
                        except (KeyError, ValueError):
                            value_data.append("")

                    value_alg.append((self.data_list[data], value_data, min_value, max_value))
                    if min_value is not sys.maxsize:
                        query_min_list[data + 1][0].append(min_value)
                    else:
                        query_min_list[data + 1][0].append("")

                value_query.append((self.alg_list[alg], param_sorted, value_alg, min_index))
            value_list.append((str(self.query_list[query]), value_query, query_min_list))
        return value_list

    def getResult(self):
        return self.query_list, self.param_list, self.alg_list, self.value_list

    def add_result(self, query, param, alg, result, result_title, data_index):
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

        try:
            self.value_map[(query_index, param_index, alg_index, data_index)] = result[result_title]
        except KeyError:
            self.value_map[(query_index, param_index, alg_index, data_index)] = ""

    def save_to_graph(self, project, datalist, log_scale, ms_to_s):
        for query_idx, query in enumerate(self.query_list):
            file_path = os.path.join(settings.MEDIA_ROOT, 'graphs', 'data_file')
            if not os.path.exists(file_path):
                os.makedirs(file_path)
            file_name = re.sub(r'\'|\[|\]| ', '_', os.path.join( file_path, datetime.datetime.now().strftime('%Y%m%d-%H%M%S') + str(query) + '_' + datalist.name + '.txt'))
            with open( file_name, 'w') as w:
                for alg_idx, alg in enumerate(self.alg_list):
                    w.write( "#" + str(alg) + '\n' )
                    for data_idx, data in enumerate(self.data_list):
                        for param_idx, param in enumerate(self.param_list[alg_idx]):
                            try:
                                value = self.value_map[(query_idx, param_idx, alg_idx, data_idx)]
                                if ms_to_s:
                                    value = float(value) / 1000
                                w.write( str(self.getSize(data)) + '\t')
                                w.write( str(value) + '\n' )
                            except KeyError:
                                pass
                            except:
                                e = sys.exc_info()[0]
                                print(e)
                    w.write( "\n\n" ) 
            plot_name = re.sub(r'\.txt', '.plot', file_name)
            graph_name = re.sub(r'\.txt', '.png', file_name)
            with open( plot_name, 'w') as w:
                w.write('set xlabel \"Number of strings\"\n')
                w.write('set key top left\n')
                if ms_to_s:
                    w.write('set ylabel \"Execution time \(sec\)\"\n')
                else:
                    w.write('set ylabel \"Execution time \(msec\)\"\n')
                w.write('set term png\n')
                if log_scale is not None:
                    if 'x' in log_scale:
                        w.write('set logscale x\n')
                    if 'y' in log_scale:
                        w.write('set logscale y\n')
                w.write('set output \"' + graph_name + '\"\n') 

                w.write('plot ')
                for alg_idx, alg in enumerate(self.alg_list):
                    alg_obj = get_object_or_404(Algorithm, pk=alg[2])
                    w.write('\"' + file_name + '\" index ' + str(alg_idx) + ' with linespoints ')
                    if alg_obj.color is not None and alg_obj.color != "":
                        w.write( 'lt rgb "' + alg_obj.color + '" ' ) 
                    w.write( 'title \"' + alg[0] + '\"')
                    if alg_idx != len(self.alg_list) - 1:
                        w.write(',\\\n')
                    else:
                        w.write('\n')
            call(["gnuplot", plot_name])        

            new_graph = Graph( project=project, datalist=datalist)
            #new_graph.description = str(self.query_list) + ":" + str(self.data_list) + ":" + str(self.alg_list) + ":" + str(self.param_list) + ":" +  str(self.value_map)
            new_graph.description = str(self.alg_id_list) + ":" + str(self.selected_query) + ":" + str(self.alg_param_map)

            new_graph.data_file.name = re.sub(settings.MEDIA_ROOT, '', file_name)
            new_graph.plot_file.name = re.sub(settings.MEDIA_ROOT, '', plot_name)
            new_graph.graph_file.name = re.sub(settings.MEDIA_ROOT, '', graph_name)
            new_graph.save()
        return new_graph

    def getSize(self, string):
        if string.startswith('aol') or string.startswith('SPROT'):
            m = re.search('[0-9]+',string)
            return m.group(0)
        if string.startswith('usps_s_'):
            size_array = [10000, 15848, 25118, 39810, 63095, 100000, 158489, 251188, 398107, 630957, 1000000]
            m = re.search('[0-9]+', string)
            return size_array[int(m.group(0)) - 1]
        if string.startswith('1'): # synthetic
            splitted = string.split('_')
            return int(splitted[2])
        return "1"
