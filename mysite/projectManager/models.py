from django.db import models
from django.utils import timezone

from .utils import *


# Create your models here.
class Project(models.Model):
    project_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')
    has_experiments = models.BooleanField(default=False)
    git_url = models.TextField(null=True)
    paramFilter = models.TextField(null=True)
    resultFilter = models.TextField(null=True)

    def getParamFilter(self):
        return self.paramFilter.split(',')

    def getResultFilter(self):
        return self.resultFilter.split(',')

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
        return self.name + ':' + self.project.project_text

    def __eq__(self, other):
        return self.name == other.name

    def __lt__(self, other):
        return self.name < other.name


class Server(models.Model):
    server_name = models.CharField(max_length=20)
    server_ip = models.GenericIPAddressField()
    server_cpu = models.CharField(max_length=100, null=True)

    # memory = models.CharField(max_length=20)
    # os = models.CharField(max_length=20)

    def __str__(self):
        return self.server_name


class Dataset(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    name = models.TextField(null=True)
    is_synthetic = models.BooleanField(default=False)
    synthetic_parameters = models.TextField(null=True)

    def __str__(self):
        return self.name + ':' + self.project.project_text

    def parameterToList(self):
        return toList(self.synthetic_parameters)


class ExpItem(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    algorithm = models.ForeignKey(Algorithm, on_delete=models.CASCADE)
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, null=True)
    exp_date = models.DateTimeField('date experimented')
    parameter = models.TextField('parameters used')
    result = models.TextField('result')
    failed = models.BooleanField('failed', default=False)
    server = models.ForeignKey(Server, default=None, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.exp_date.strftime("%y-%m-%d %H:%M:%S")

    def toParamValueList(self):
        params = self.project.getParamFilter()
        values = toDictionary(self.parameter)
        return self.toMatchedList(params, values)

    def toResultValueList(self):
        params = self.project.getResultFilter()
        values = toDictionary(self.result)
        return self.toMatchedList(params, values)

    def toMatchedList(self, params, values):
        l = []
        for par in params:
            try:
                l.append(values[par.strip()])
            except KeyError:
                l.append('Null')
        return l

        # def toList(self):
        #    return toList(self.parameter) + toList(self.result)


class ExpTodo(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    parameters = models.TextField()
    pub_date = models.DateTimeField('date published')


class RelatedWork(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    authors = models.TextField(null=True)
    url = models.URLField(null=True)
