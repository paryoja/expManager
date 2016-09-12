from django.contrib import admin

from projectManager.models import Algorithm, BookMark, Dataset, ExpItem, Project, \
    RelatedWork, SettingFiles, TodoItem, Server


# Register your models here.
admin.site.register(Algorithm)
admin.site.register(BookMark)
admin.site.register(Dataset)
admin.site.register(ExpItem)
admin.site.register(Project)
admin.site.register(RelatedWork)
admin.site.register(Server)
admin.site.register(SettingFiles)
admin.site.register(TodoItem)





