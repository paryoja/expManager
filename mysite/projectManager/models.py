from django.db import models


# Create your models here.
class Project(models.Model):
    project_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')

    def __str__(self):
        return self.project_text


class TodoItem(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    todo_text = models.CharField(max_length=200)
    level = models.IntegerField(default=0)
    pub_date = models.DateTimeField('date published')
    deadline_date = models.DateTimeField('')
    done = models.BooleanField()

    def __str__(self):
        return self.todo_text


class ExpItem(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    exp_date = models.DateTimeField('date experimented')
    parameter = models.TextField('parameters used')
    result = models.TextField('result used')


class ExpTodo(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    parameters = models.TextField()
    pub_date = models.DateTimeField('date published')


class Server(models.Model):
    server_name = models.CharField(max_length=20)
    server_ip = models.GenericIPAddressField()
    server_cpu = models.CharField(max_length=20, null=True)
