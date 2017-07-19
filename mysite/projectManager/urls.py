import django.contrib.auth.views as auth_views
from django.conf.urls import url

from . import exp_views
from . import views

app_name = 'project'
urlpatterns = [
    url(r'^$', views.index, name='index'),

    # login/logout
    url(r'^accounts/login/', auth_views.login, name='login', kwargs={'template_name': 'projectManager/login.html'}),
    url(r'^accounts/logout/', auth_views.logout, name='logout'),

    # related with project
    url(r'^(?P<pk>[0-9]+)/$', views.DetailView.as_view(), name='detail'),
    url(r'^listProjects/$', views.ListProjectView.as_view(), name='listProject'),
    url(r'^projectForm/$', views.addProjectWithForm, name='projectForm'),
    url(r'^addProject/$', views.addProjectWithForm, name='addProjectWithForm'),
    url(r'^getProjectId/(?P<project_name>.+)/$', views.getProjectId, name='getProjectId'),
    url(r'^(?P<project_id>[0-9]+)/addGitUrl/$', views.addGitUrl, name='addGitUrl'),
    url(r'^addRelatedWork/(?P<pk>[0-9]+)/$', views.addRelatedWork, name='addRelatedWork'),

    # related with server
    url(r'^servers/(?P<pk>[0-9]+)/$', views.ServerView.as_view(), name='servers'),
    url(r'^serverForm/$', views.addServerForm, name='addServerForm'),
    url(r'^addServer/$', views.addServer, name='addServer'),
    url(r'^getServerId/(?P<server_name>.+)/$', views.getServerId, name='getServerId'),

    # related with experiments
    url(r'^(?P<pk>[0-9]+)/exp/$', views.ExpView.as_view(), name='exp'),
    url(r'^(?P<pk>[0-9]+)/expDetail/$', exp_views.exp, name='expDetail'),
    url(r'^(?P<project_id>[0-9]+)/expCompare/$', exp_views.expCompare, name='expCompare'),
    url(r'^(?P<project_id>[0-9]+)/addExp/$', exp_views.addExp, name='addExp'),
    url(r'^(?P<project_id>[0-9]+)/expForm/$', exp_views.expForm, name='expForm'),
    url(r'^(?P<pk>[0-9]+)/expListAll/$', exp_views.expListAll, name='expListAll'),
    url(r'^(?P<project_id>[0-9]+)/(?P<exp_id>[0-9]+)/modifyExp/$', exp_views.modifyExp, name='modifyExp'),
    url(r'^(?P<project_id>[0-9]+)/InvalidateOld/$', views.invalidateOld, name='invalidateOld'),
    url(r'^(?P<project_id>[0-9]+)/InvalidateOldAction/$', views.invalidateOldAction, name='invalidateOldAction'),
    url(r'^(?P<project_id>[0-9]+)/(?P<dataset_id>[0-9]+)/(?P<algorithm_id>[0-9]+)/listSameExp/$', exp_views.listSameExp,
        name='listSameExp'),

    # related with datasetlist
    url(r'^(?P<project_id>[0-9]+)/addDataList/$', views.addDataList, name='addDataList'),
    url(r'^(?P<project_id>[0-9]+)/(?P<datalist_id>[0-9]+)/datalistConfigure/$', exp_views.datalistConfigure,
        name='datalistConfigure'),
    url(r'^(?P<project_id>[0-9]+)/(?P<datalist_id>[0-9]+)/datalistResult/$', exp_views.datalistResult,
        name='datalistResult'),
    url(r'^(?P<project_id>[0-9]+)/(?P<datalist_id>[0-9]+)/datalistResultSelect/$', exp_views.datalistResultSelect,
        name='datalistResultSelect'),
    url(r'^(?P<project_id>[0-9]+)/(?P<datalist_id>[0-9]+)/(?P<dataset_id>[0-9]+)/addToDataList/$',
        exp_views.addToDataList, name='addToDataList'),
    url(r'^(?P<project_id>[0-9]+)/(?P<datalist_id>[0-9]+)/(?P<dataset_id>[0-9]+)/removeFromDataList/$',
        exp_views.removeFromDataList, name='removeFromDataList'),

    # related with graphs
    url(r'^(?P<pk>[0-9]+)/graph/$', views.graph, name='graph'),
    url(r'^(?P<pk>[0-9]+)/addGraph/$', views.addGraph, name='addGraph'),
    url(r'^(?P<pk>[0-9]+)/graphExp/$', views.graphExp, name='graphExp'),
    url(r'^(?P<project_id>[0-9]+)/(?P<datalist_id>[0-9]+)/(?P<server_id>[0-9]+)/drawGraph', exp_views.drawGraph, name='drawGraph'),

    # related with todo
    url(r'^(?P<project_id>[0-9]+)/addTodo/$', views.addTodo, name='addTodo'),
    url(r'^(?P<project_id>[0-9]+)/(?P<todo_id>[0-9]+)/modifyTodo/$', views.modifyTodo, name='modifyTodo'),

    # related with algorithm
    url(r'^(?P<project_id>[0-9]+)/addAlgorithm/$', views.addAlgorithm, name='addAlgorithm'),
    url(r'^(?P<project_id>[0-9]+)/algorithmForm/$', views.algorithmForm, name='algorithmForm'),
    url(r'^(?P<project_id>[0-9]+)/listAlgorithms/$', views.listAlgorithms, name='listAlgorithms'),
    url(r'^(?P<project_id>[0-9]+)/getAlgorithmId/(?P<algorithm_name>.+)/(?P<algorithm_version>.+)/$',
        views.getAlgorithmId,
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

    # related with settings
    url(r'^hadoopSetting/$', views.hadoopSetting, name='hadoopSetting'),
    url(r'^vimSetting/$', views.vimSetting, name='vimSetting'),
    url(r'^hostSetting/$', views.hostSetting, name='hostSetting'),
    url(r'^eclipseSetting/$', views.eclipseSetting, name='eclipseSetting'),
    url(r'^ubuntuPreseed/$', views.ubuntuPreseed, name='ubuntuPreseed'),
    url(r'^jupyterSetting/$', views.jupyterSetting, name='jupyterSetting'),

    # file download
    url(r'^expUploader/$', views.expUploader, name='expUploader'),

    # related with bookmark
    url(r'^addBookMark/$', views.addBookMark, name='addBookMark'),
    url(r'redirectBookMark/(?P<bookmark_id>[0-9]+)/$', views.redirectBookMark, name='redirectBookMark'),
    url(r'^map/$', views.showMap, name='map'),

    url(r'glossary/$', views.glossary, name='glossary'),
]
