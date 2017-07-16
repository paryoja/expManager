from django.db import models
from django.utils import timezone

from projectManager.utils import splitColon, toList, toDictionary


# Create your models here.
class Project(models.Model):
    project_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published', auto_now_add=True)
    has_experiments = models.BooleanField(default=False)
    git_url = models.TextField(null=True, blank=True)
    paramFilter = models.TextField(null=True, blank=True)
    queryFilter = models.TextField(null=True, blank=True)
    resultFilter = models.TextField(null=True, blank=True)

    def getParamFilter(self):
        return self.paramFilter.split(',')

    def getParamFilterOriginalName(self):
        split = self.paramFilter.split(',')
        return splitColon(split, 0)

    def getParamFilterName(self):
        split = self.paramFilter.split(',')
        return splitColon(split, 1)

    def getQueryFilter(self):
        if self.queryFilter is not None:
            return self.queryFilter.split(',')
        return None

    def getQueryFilterOriginalName(self):
        split = self.queryFilter.split(',')
        return splitColon(split, 0)

    def getQueryFilterName(self):
        if self.queryFilter is not None:
            split = self.queryFilter.split(',')
            return splitColon(split, 1)
        return None

    def getResultFilter(self):
        return self.resultFilter.split(',')

    def getResultFilterOriginalName(self):
        split = self.resultFilter.split(',')
        return splitColon(split, 0)

    def getResultFilterName(self):
        split = self.resultFilter.split(',')
        return splitColon(split, 1)

    def __str__(self):
        return self.project_text


class TodoItem(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    todo_text = models.CharField(max_length=200)
    level = models.IntegerField(default=0)
    pub_date = models.DateTimeField('date published')
    deadline_date = models.DateTimeField('deadline date')
    completed_date = models.DateTimeField(null=True)
    done = models.BooleanField()

    def getDday(self):
        return -(timezone.now() - self.deadline_date).days

    def getMinusDday(self):
        return (timezone.now() - self.deadline_date).days

    def __str__(self):
        return self.todo_text


class Algorithm(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True)
    name = models.TextField('Algorithm name')
    version = models.CharField(max_length=10)
    status = models.CharField(max_length=20)

    def __str__(self):
        return self.name + ':' + self.project.project_text + ":" + self.version

    def __eq__(self, other):
        if not isinstance(other, Algorithm):
            return False
        if self.name == other.name:
            return self.version == other.version
        return False

    def __lt__(self, other):
        if self.name == other.name:
            return self.version < other.version
        return self.name < other.name

    def isNewest(self):
        other_version = Algorithm.objects.filter(name=self.name)
        for other in other_version:
            if other.version > self.version:
                return False
        return True


class Server(models.Model):
    server_name = models.CharField(max_length=20)
    server_ip = models.GenericIPAddressField()
    server_cpu = models.CharField(max_length=100, null=True)
    rsa_pub = models.CharField(max_length=400, null=True)

    # memory = models.CharField(max_length=20)
    # os = models.CharField(max_length=20)

    def __str__(self):
        return self.server_name

    def __eq__(self, other):
        if not isinstance(other, Server):
            return False
        if other is None:
            return False
        return self.server_name == other.server_name

    def __lt__(self, other):
        if other is None:
            return False
        return self.server_name < other.server_name


class Dataset(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    name = models.TextField(null=True)
    is_synthetic = models.BooleanField(default=False)
    synthetic_parameters = models.TextField(null=True)
    data_info = models.TextField(null=True)
    size = models.FloatField(null=True)

    def __str__(self):
        return self.name + ':' + self.project.project_text

    def parameterToList(self):
        return toList(self.synthetic_parameters)

    def infoToList(self):
        if self.data_info is not None:
            return toList(self.data_info)
        else:
            return []
        

    def toOptionString(self, exclude):
        param_list = self.parameterToList()
        result_list = []
        for param in param_list:
            if param[0] != exclude:
                result_list.append(param[0] + '=' + param[1])
        return result_list


class DataList(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    name = models.TextField(null=False)
    description = models.TextField(null=True)

    def __str__(self):
        return self.name + ':' + self.project.project_text


class DataContainment(models.Model):
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    #dataset_list = models.ForeignKey(DataList, on_delete=models.CASCADE)
    data_list = models.ForeignKey(DataList)



class ExpItem(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    algorithm = models.ForeignKey(Algorithm, on_delete=models.CASCADE)
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, null=True)
    upload_date = models.DateTimeField('date uploaded', auto_now_add=True)
    exp_date = models.DateTimeField('date experimented')
    parameter = models.TextField('parameters used')
    result = models.TextField('result')
    failed = models.BooleanField('failed', default=False)
    invalid = models.BooleanField('invalid', default=False)
    server = models.ForeignKey(Server, default=None, on_delete=models.CASCADE, null=True)

    def __str__(self):
        local_time = timezone.localtime(self.exp_date)
        return local_time.strftime("%y-%m-%d %H:%M:%S")

    def toOptionString(self, exclude, param_name):
        return_list = []
        param_list = self.toParamValueList()
        for i in range(len(param_name)):
            if param_name[i] != exclude:
                return_list.append(param_name[i] + '=' + param_list[i])

        return ' '.join(sorted(return_list + self.dataset.toOptionString(exclude)))

    def toParamValueList(self):
        params = self.project.getParamFilter()
        values = toDictionary(self.parameter)
        return self.toMatchedList(params, values)

    def toQueryValueList(self):
        params = self.project.getQueryFilter()
        if params is None:
            return None
        values = toDictionary(self.parameter)
        return self.toMatchedList(params, values)

    def toResultValueList(self):
        params = self.project.getResultFilter()
        values = toDictionary(self.result)
        return self.toMatchedList(params, values)

    def toMatchedList(self, params, values):
        array = []
        for par in params:
            if ':' in par:
                par = par.split(':')[0]
            try:
                array.append(values[par.strip()])
            except KeyError:
                array.append('Null')
        return array


class ExpTodo(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    parameters = models.TextField()
    pub_date = models.DateTimeField('date published')


class RelatedWork(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    title = models.TextField(null=False)
    authors = models.TextField(null=True)
    journal = models.TextField(null=True)
    url = models.URLField(null=True)
    pdf_path = models.FileField(null=True)

    def __str__(self):
        return self.title


class BookMark(models.Model):
    name = models.CharField(max_length=100, null=False)
    url = models.URLField()
    last_visit = models.DateTimeField(null=True, auto_now=True)
    times_visited = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class SettingFiles(models.Model):
    server = models.ForeignKey(Server, on_delete=models.CASCADE)
    name = models.TextField(null=False)
    attachment = models.FileField()
    hashcode = models.CharField(max_length=500, null=False)

    def __str__(self):
        return self.name
