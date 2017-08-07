import datetime
import os
import re
import sys
from subprocess import call

from django.conf import settings
from django.shortcuts import get_object_or_404
from projectManager.utils import toDictionary

from .models import ExpItem, Graph, Algorithm


class ExpContainer:
    def __init__(self, cont_list, query_name_list, param_name_list, result_title, server_list, method, skip_old=False):
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
        self.server_list = server_list
        self.method = method
        self.skip_old = skip_old

    def load(self, alg_id_list=None, selected_query=None, alg_param_map=None):
        # alg_id_list = [ '65', '66', ... ]
        # selected_query = ['True']
        # alg_param_map = { 65:["additional: "] }
        self.alg_id_list = alg_id_list

        if alg_id_list is not None:
            for alg_id in alg_id_list:
                # add to self.alg_list
                algorithm = Algorithm.objects.get(pk=alg_id)
                if self.skip_old and not algorithm.isNewest():
                    continue

                self.alg_list.append([algorithm.name, algorithm.version, algorithm.id])
                param_list = []

                if alg_param_map is not None:
                    # add to self.param_list
                    if int(alg_id) in alg_param_map.keys():
                        alg_param = alg_param_map[int(alg_id)]
                        for par in alg_param:
                            param = [par]
                            param_list.append(param)

                self.param_list.append(param_list)

        self.selected_query = selected_query
        self.alg_param_map = alg_param_map

        # for each dataset in the datalist
        data_index = 0
        self.value_map = {}
        for cont in self.cont_list:
            # order of data_list is depending on the id of cont
            self.data_list.append((cont.dataset.name, cont.dataset.id))
            for server in self.server_list:
                exp_items = ExpItem.objects.filter(dataset=cont.dataset, server=server, invalid=False)

                # for each exp for the dataset 
                for exp in exp_items:
                    # parameter consists of algorithm, version, and project specific parameters
                    if alg_id_list is not None:
                        if str(exp.algorithm.id) not in alg_id_list:
                            # skip this exp item
                            continue
                    if self.skip_old and not exp.algorithm.isNewest():
                        # skip old algorithm 
                        continue
                    alg = [exp.algorithm.name, exp.algorithm.version, exp.algorithm.id]

                    param_dict = toDictionary(exp.parameter)

                    param = []
                    for p in self.param_name_list:
                        param.append(param_dict[p])

                    # check skip conditions based on alg_param_map
                    if alg_param_map is not None:
                        if str(param[0]) not in alg_param_map[exp.algorithm.id]:
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

                    self.add_result(query, param, alg, toDictionary(exp.result), self.result_title, data_index, exp)
            data_index += 1

    def toValueList(self):
        value_list = []

        int_list = list(range(len(self.alg_list)))
        alg_sorted = list(sorted(zip(self.alg_list, int_list)))

        for query in range(len(self.query_list)):
            value_query = []
            query_min_list = []

            # query_min_list [0][0] -> list of algorithms for the table header
            # query_min_list [data + 1][1] -> global minimum value for the dataset
            query_min_list.append([['Algorithm'], ""])

            # for alg in self.alg_list:
            for alg in alg_sorted:
                query_min_list[0][0].append(alg[0])

            for data in range(self.data_length):
                query_min_list.append([[self.data_list[data]], sys.maxsize])

            # for alg in range(len(self.alg_list)):
            for alg_name, alg in alg_sorted:

                value_alg = []
                min_index = -1

                for data in range(self.data_length):
                    value_data = []

                    min_value = sys.maxsize
                    max_value = 0

                    int_list = list(range(len(self.param_list[alg])))
                    param_sorted = list(sorted(zip(self.param_list[alg], int_list)))

                    is_failed = False
                    for param_name, param in param_sorted:
                        try:
                            value, count, total_count = self.getValue(query, param, alg, data)
                            if value < min_value:
                                min_value = value
                                min_index = param
                            if value > max_value:
                                max_value = value

                            if value < query_min_list[data + 1][1]:
                                query_min_list[data + 1][1] = value

                            value_data.append((value, count))
                        except KeyError:
                            try:
                                value_data.append(("", count))
                            except:
                                value_data.append(("", 0))
                        except (ValueError, TypeError):
                            if value == "failed":
                                is_failed = True
                                value_data.append(("failed", total_count))
                            else:
                                value_data.append(("", total_count))

                    value_alg.append((self.data_list[data], value_data, min_value, max_value))
                    if min_value is not sys.maxsize:
                        query_min_list[data + 1][0].append(min_value)
                    elif is_failed:
                        query_min_list[data + 1][0].append("failed")
                    else:
                        query_min_list[data + 1][0].append("")

                value_query.append((self.alg_list[alg], param_sorted, value_alg, min_index))
            value_list.append((str(self.query_list[query]), value_query, query_min_list))
        return value_list

    def getResult(self):
        self.value_list = self.toValueList()
        return self.query_list, self.param_list, self.alg_list, self.value_list

    def getList(self):
        return self.query_list, self.param_list, self.alg_list, self.data_list

    def getValue(self, query_id, param_id, alg_id, data_id):
        try:
            value_list = self.value_map[(query_id, param_id, alg_id, data_id)]
        except:
            return ("", 0, 0)

        total_count = 0
        if self.method == "avg":
            count = 0
            total = 0
            is_failed = False
            is_empty = False
            for exp, value in value_list:
                total_count += 1
                if value == "failed" or value == "":
                    if value == "failed":
                        is_failed = True
                    else:
                        is_empty = True
                    continue
                total += float(value)
                count += 1

            if is_failed:
                return ("failed", count, total_count)
            if count != 0:
                return (total / count, count, total_count)
            if is_empty:
                return ("", count, total_count)

        elif self.method == "latest":
            # TODO implement
            min_date = 0
            min_value = None

            total_count += 1
            return (min_value, count, total_count)

        elif self.method == "minmax":
            # assume 0 is minimum
            min_value = sys.maxsize
            max_value = 0

            count = 0
            total = 0
            is_failed = False
            is_empty = False
            for exp, value in value_list:
                total_count += 1
                if value == "failed" or value == "":
                    if value == "failed":
                        is_failed = True
                    else:
                        is_empty = True
                    continue

                f_value = float(value)
                if min_value > f_value:
                    min_value = f_value
                if max_value < f_value:
                    max_value = f_value
                total += f_value
                count += 1

            if count != 0:
                if count > 2:
                    return ((total - min_value - max_value) / (count - 2), count, total_count)
                else:
                    return (total / count, count, total_count)
            if is_failed:
                return ("failed", count, total_count)
            if is_empty:
                return ("", count, total_count)
        return (None, None, None)

    def add_result(self, query, param, alg, result, result_title, data_index, exp):
        # add alg
        if alg not in self.alg_list:
            self.alg_list.append(alg)
            self.param_list.append([])
        alg_index = self.alg_list.index(alg)

        # add query
        if query not in self.query_list:
            self.query_list.append(query)
        query_index = self.query_list.index(query)

        # add param
        if param not in self.param_list[alg_index]:
            self.param_list[alg_index].append(param)
        param_index = self.param_list[alg_index].index(param)

        valuemap_key = (query_index, param_index, alg_index, data_index)
        if valuemap_key not in self.value_map.keys():
            self.value_map[valuemap_key] = []

        if exp.failed:
            self.value_map[valuemap_key].append((exp, "failed"))
        else:
            try:
                self.value_map[valuemap_key].append((exp, result[result_title]))
            except KeyError:
                self.value_map[valuemap_key].append((exp, ""))

    def save_to_graph(self, project, datalist, log_scale, ms_to_s):
        result_list = []
        for query_idx, query in enumerate(self.query_list):
            file_path = os.path.join(settings.MEDIA_ROOT, 'graphs', 'data_file')
            if not os.path.exists(file_path):
                os.makedirs(file_path)
            file_name = re.sub(r'\'|\[|\]| ', '_', os.path.join(file_path,
                                                                datetime.datetime.now().strftime('%Y%m%d-%H%M%S') + str(
                                                                    query) + '_' + datalist.name + '.txt'))

            with open(file_name, 'w') as w:
                for alg_idx, alg in enumerate(self.alg_list):
                    w.write("#" + str(alg) + '\n')
                    for data_idx, data in enumerate(self.data_list):
                        for param_idx, param in enumerate(self.param_list[alg_idx]):
                            if data_idx == 0:
                                w.write("#" + str(param) + '\n')
                            try:
                                value, count, total_count = self.getValue(query_idx, param_idx, alg_idx, data_idx)
                                if ms_to_s:
                                    value = float(value) / 1000
                                w.write(str(self.getSize(data[0], datalist)) + '\t')
                                w.write(str(value) + '\n')
                            except KeyError:
                                pass
                            except ValueError:
                                pass
                            except Exception as e:
                                print(e)
                                print(value)
                    w.write("\n\n")
            plot_name = re.sub(r'\.txt', '.plot', file_name)
            graph_name = re.sub(r'\.txt', '.png', file_name)
            with open(plot_name, 'w') as w:
                if datalist.variable is not None:
                    if datalist.variable == 'rules':
                        w.write('set xlabel \"Number of rules\"\n')
                    else:
                        w.write('set xlabel \"Number of strings\"\n')
                else:
                    w.write('set xlabel \"Number of strings\"\n')
                w.write('set key top left\n')
                if ms_to_s:
                    w.write('set ylabel \"Execution time \(sec\)\"\n')
                else:
                    w.write('set ylabel \"Execution time \(msec\)\"\n')
                # w.write('set term png\n')
                w.write('set term png size 800,600\n')
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
                        w.write('lt rgb "' + alg_obj.color + '" ')
                    w.write('title \"' + alg[0] + " " + str(self.param_list[alg_idx][0][0]) + '\"')
                    if alg_idx != len(self.alg_list) - 1:
                        w.write(',\\\n')
                    else:
                        w.write('\n')
            call(["gnuplot", plot_name])

            new_graph = Graph(project=project, datalist=datalist)
            # new_graph.description = str(self.query_list) + ":" + str(self.data_list) + ":" + str(self.alg_list) + ":" + str(self.param_list) + ":" +  str(self.value_map)
            new_graph.description = str(self.alg_id_list) + ":" + str(self.selected_query) + ":" + str(
                self.alg_param_map)

            new_graph.data_file.name = re.sub(settings.MEDIA_ROOT, '', file_name)
            new_graph.plot_file.name = re.sub(settings.MEDIA_ROOT, '', plot_name)
            new_graph.graph_file.name = re.sub(settings.MEDIA_ROOT, '', graph_name)
            new_graph.save()
            result_list.append(new_graph)
        return result_list

    def save_to_param_graph(self, project, datalist, log_scale, ms_to_s):
        result_list = []
        for query_idx, query in enumerate(self.query_list):
            file_path = os.path.join(settings.MEDIA_ROOT, 'graphs', 'data_file')
            if not os.path.exists(file_path):
                os.makedirs(file_path)
            file_name = re.sub(r'\'|\[|\]| ', '_', os.path.join(file_path,
                                                                datetime.datetime.now().strftime('%Y%m%d-%H%M%S') + str(
                                                                    query) + '_' + datalist.name + '.txt'))
            with open(file_name, 'w') as w:
                for alg_idx, alg in enumerate(self.alg_list):
                    w.write("#" + str(alg) + '\n')
                    for param_idx, param in enumerate(self.param_list[alg_idx]):
                        w.write("#" + str(param) + '\n')
                        for data_idx, data in enumerate(self.data_list):
                            try:
                                value, count, total_count = self.getValue(query_idx, param_idx, alg_idx, data_idx)
                                if ms_to_s:
                                    value = float(value) / 1000
                                else:
                                    value = float(value)
                                w.write(str(self.getSize(data[0], datalist)) + '\t')
                                w.write(str(value) + '\n')
                            except KeyError:
                                pass
                            except ValueError:
                                pass
                            except:
                                e = sys.exc_info()[0]
                                print(e)
                        w.write("\n\n")
            plot_name = re.sub(r'\.txt', '.plot', file_name)
            graph_name = re.sub(r'\.txt', '.png', file_name)

            with open(plot_name, 'w') as w:
                if datalist.variable is not None:
                    if datalist.variable == 'rules':
                        w.write('set xlabel \"Number of rules\"\n')
                    else:
                        w.write('set xlabel \"Number of strings\"\n')
                else:
                    w.write('set xlabel \"Number of strings\"\n')
                w.write('set key top left\n')
                if ms_to_s:
                    w.write('set ylabel \"Execution time \(sec\)\"\n')
                else:
                    w.write('set ylabel \"Execution time \(msec\)\"\n')
                w.write('set term png size 1200,1000\n')

                if log_scale is not None:
                    if 'x' in log_scale:
                        w.write('set logscale x\n')
                    if 'y' in log_scale:
                        w.write('set logscale y\n')
                w.write('set output \"' + graph_name + '\"\n')

                w.write('plot ')
                int_list = list(range(len(self.param_list[0])))
                line_count = 0
                for param, param_idx in sorted(zip(self.param_list[0], int_list)):
                    line_count += 1
                    w.write('\"' + file_name + '\" index ' + str(param_idx) + ' with linespoints ')
                    w.write('title \"' + str(param) + '\"')
                    if line_count != len(self.param_list[0]):
                        w.write(',\\\n')
                    else:
                        w.write('\n')
            call(["gnuplot", plot_name])

            new_graph = Graph(project=project, datalist=datalist)
            # new_graph.description = str(self.query_list) + ":" + str(self.data_list) + ":" + str(self.alg_list) + ":" + str(self.param_list) + ":" +  str(self.value_map)
            new_graph.description = str(self.alg_id_list) + ":" + str(self.selected_query) + ":" + str(
                self.alg_param_map)

            new_graph.data_file.name = re.sub(settings.MEDIA_ROOT, '', file_name)
            new_graph.plot_file.name = re.sub(settings.MEDIA_ROOT, '', plot_name)
            new_graph.graph_file.name = re.sub(settings.MEDIA_ROOT, '', graph_name)
            new_graph.save()
            result_list.append(new_graph)
        return result_list

    def getSize(self, string, datalist):
        if string.startswith('aol') or string.startswith('SPROT') or string.startswith('USPS'):
            m = re.search('[0-9]+', string)
            return m.group(0)
        if string.startswith('usps_s_'):
            size_array = [10000, 15848, 25118, 39810, 63095, 100000, 158489, 251188, 398107, 630957, 1000000]
            m = re.search('[0-9]+', string)
            return size_array[int(m.group(0)) - 1]
        if string.startswith('sample_sprot'):
            size_array = [10000, 15848, 25118, 39810, 63095, 100000, 158489, 251188, 466158]
            m = re.search('[0-9]+', string)
            return size_array[int(m.group(0)) - 1]
        if string.startswith('1'):  # synthetic
            splitted = string.split('_')
            if datalist.variable is not None:
                if datalist.variable == "rules":
                    return int(splitted[17])
            return int(splitted[2])
        return "1"
