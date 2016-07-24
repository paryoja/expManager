from django.contrib import admin

# Register your models here.
from .models import *

admin.site.register(Project)
admin.site.register(TodoItem)
admin.site.register(ExpItem)
admin.site.register(Server)
admin.site.register(Algorithm)
admin.site.register(Dataset)
