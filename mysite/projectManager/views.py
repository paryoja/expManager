from django.views import generic

from .models import Project, ExpItem


# Create your views here.

class IndexView(generic.ListView):
    template_name = 'projectManager/index.html'
    context_object_name = 'project_list'

    def get_queryset(self):
        return Project.objects.all()


class DetailView(generic.DetailView):
    model = Project
    template_name = 'projectManager/detail.html'


class ExpView(generic.DetailView):
    model = Project
    template_name = 'projectManager/exp.html'
