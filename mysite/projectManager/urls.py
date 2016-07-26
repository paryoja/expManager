from django.conf.urls import url

from . import views

app_name = 'project'
urlpatterns = [
    url(r'^$', views.index, name='index'),

    # related with project
    url(r'^(?P<pk>[0-9]+)/$', views.DetailView.as_view(), name='detail'),
    url(r'^listProjects/$', views.ListProjectView.as_view(), name='listProject'),
    url(r'^projectForm/$', views.addForm, name='projectForm'),
    url(r'^addProject/$', views.addProject, name='addProject'),
    url(r'^getProjectId/(?P<project_name>.+)/$', views.getProjectId, name='getProjectId'),
    url(r'^(?P<project_id>[0-9]+)/addGitUrl/$', views.addGitUrl, name='addGitUrl'),

    # related with server
    url(r'^servers/(?P<pk>[0-9]+)/$', views.ServerView.as_view(), name='servers'),
    url(r'^serverForm/$', views.addServerForm, name='addServerForm'),
    url(r'^addServer/$', views.addServer, name='addServer'),

    # related with experiments
    url(r'^(?P<pk>[0-9]+)/exp/$', views.ExpView.as_view(), name='exp'),
    url(r'^(?P<pk>[0-9]+)/expDetail/$', views.exp, name='expDetail'),
    url(r'^(?P<project_id>[0-9]+)/addExp/$', views.addExp, name='addExp'),
    url(r'^(?P<project_id>[0-9]+)/expForm/$', views.expForm, name='expForm'),

    # related with todo
    url(r'^(?P<project_id>[0-9]+)/addTodo/$', views.addTodo, name='addTodo'),
    url(r'^(?P<project_id>[0-9]+)/(?P<todo_id>[0-9]+)/modifyTodo/$', views.modifyTodo, name='modifyTodo'),

    # related with algorithm
    url(r'^(?P<project_id>[0-9]+)/addAlgorithm/$', views.addAlgorithm, name='addAlgorithm'),
    url(r'^(?P<project_id>[0-9]+)/algorithmForm/$', views.algorithmForm, name='algorithmForm'),
    url(r'^(?P<project_id>[0-9]+)/listAlgorithms/$', views.listAlgorithms, name='listAlgorithms'),
    url(r'^(?P<project_id>[0-9]+)/getAlgorithmId/(?P<algorithm_name>.+)/$', views.getAlgorithmId,
        name='getAlgorithmId'),
    url(r'^(?P<project_id>[0-9]+)/algorithmDetail/(?P<pk>[0-9]+)/$', views.AlgorithmDetailView.as_view(),
        name='algorithmDetail'),

    # related with dataset
    url(r'^(?P<project_id>[0-9]+)/addDataset/$', views.addDataset, name='addDataset'),
    url(r'^(?P<project_id>[0-9]+)/datasetForm/$', views.datasetForm, name='datasetForm'),
    url(r'^(?P<project_id>[0-9]+)/listDatasets/$', views.listDatasets, name='listDatasets'),
    url(r'^(?P<project_id>[0-9]+)/getDatasetId/(?P<dataset_name>.+)/$', views.getDatasetId, name='getDatasetId'),
    url(r'^(?P<project_id>[0-9]+)/datasetDetail/(?P<pk>[0-9]+)/$', views.DatasetDetailView.as_view(),
        name='datasetDetail'),

]
