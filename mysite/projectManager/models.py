from django.db import models
from django.utils import timezone

from .utils import *


# Create your models here.
class Project(models.Model):
    project_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')
    has_experiments = models.BooleanField(default=False)
    git_url = models.TextField(null=True)
    experimentParams = models.TextField(null=True)

    def getParamList(self):
        return self.experimentParams.split(',')

    def __str__(self):
        return self.project_text


class TodoItem(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    todo_text = models.CharField(max_length=200)
    level = models.IntegerField(default=0)
    pub_date = models.DateTimeField('date published')
    deadline_date = models.DateTimeField('')
    completed_date = models.DateTimeField(null=True)
    done = models.BooleanField()

    def getDday(self):
        return -(timezone.now() - self.deadline_date).days

    def __str__(self):
        return self.todo_text


class Algorithm(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True)
    name = models.TextField('Algorithm name')
    version = models.CharField(max_length=10)

    def __str__(self):
        return self.name


class Dataset(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    name = models.TextField(null=True)
    is_synthetic = models.BooleanField(default=False)
    synthetic_parameters = models.TextField(null=True)

    def __str__(self):
        return self.name


class ExpItem(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    algorithm = models.ForeignKey(Algorithm, on_delete=models.CASCADE)
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, null=True)
    exp_date = models.DateTimeField('date experimented')
    parameter = models.TextField('parameters used')
    result = models.TextField('result')

    def __str__(self):
        return self.exp_date.strftime("%y-%m-%d %H:%M:%S")

    def toPrintList(self):
        l = []
        params = self.project.experimentParams.split(",")
        result = toDictionary(self.result)

        print(result)

        for par in params:
            print(par.strip())
            try:
                l.append(result[par.strip()])
            except KeyError:
                l.append('Null')

        return l

    def toList(self):
        return toList(self.parameter) + toList(self.result)


class ExpTodo(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    parameters = models.TextField()
    pub_date = models.DateTimeField('date published')


class Server(models.Model):
    server_name = models.CharField(max_length=20)
    server_ip = models.GenericIPAddressField()
    server_cpu = models.CharField(max_length=100, null=True)
    # memory = models.CharField(max_length=20)
    # os = models.CharField(max_length=20)
