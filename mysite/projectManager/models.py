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

    def __str__(self):
        return self.todo_text


''' Check on_delete CASCADE '''


class ExpItem(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    exp_date = models.DateTimeField('date experimented')
    parameter = models.TextField('parameters used')
    result = models.TextField('result used')
