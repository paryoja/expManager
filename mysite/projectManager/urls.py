from django.conf.urls import url

from . import views

app_name = 'project'
urlpatterns = [
    url(r'^$', views.index, name='index'),

    # related with project
    url(r'^(?P<pk>[0-9]+)/$', views.DetailView.as_view(), name='detail'),
    url(r'^projectForm/', views.addForm, name='projectForm'),
    url(r'^addProject/', views.addProject, name='addProject'),

    # related with server
    url(r'^servers/(?P<pk>[0-9]+)/$', views.ServerView.as_view(), name='servers'),
    url(r'^serverForm/', views.addServerForm, name='addServerForm'),
    url(r'^addServer/', views.addServer, name='addServer'),

    # related with experiments
    url(r'^(?P<pk>[0-9]+)/exp$', views.ExpView.as_view(), name='exp'),
    url(r'^(?P<pk>[0-9]+)/expDetail/$', views.exp, name='expDetail'),
    url(r'^(?P<project_id>[0-9]+)/addExp/', views.addExp, name='addExp' ),
    url(r'^(?P<project_id>[0-9]+)/expForm/', views.expForm, name='expForm' ),

    # related with todo
    url(r'^(?P<project_id>[0-9]+)/addTodo$', views.addTodo, name='addTodo'),
    url(r'^(?P<project_id>[0-9]+)/(?P<todo_id>[0-9]+)/modifyTodo$', views.modifyTodo, name='modifyTodo'),

    # related with algorithm
    url(r'^(?P<project_id>[0-9]+)/addAlgorithm$', views.addAlgorithm, name='addAlgorithm' ),
    url(r'^(?P<project_id>[0-9]+)/algorithmForm$', views.algorithmForm, name='algorithmForm' ),

    # related with dataset
    url(r'^(?P<project_id>[0-9]+)/addDataset$', views.addDataset, name='addDataset' ),
    url(r'^(?P<project_id>[0-9]+)/datasetForm$', views.datasetForm, name='datasetForm' ),

]
