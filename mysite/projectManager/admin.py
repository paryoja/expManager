from django.contrib import admin

# Register your models here.
from .models import Project, TodoItem, ExpItem

admin.site.register(Project)
admin.site.register(TodoItem)
admin.site.register(ExpItem)
