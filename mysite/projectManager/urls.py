from django.conf.urls import url

from . import views

app_name = 'project'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^servers/(?P<pk>[0-9]+)/$', views.ServerView.as_view(), name='servers'),
    url(r'^(?P<pk>[0-9]+)/$', views.DetailView.as_view(), name='detail'),
    url(r'^(?P<pk>[0-9]+)/exp$', views.ExpView.as_view(), name='exp'),

    url(r'^projectForm/', views.addForm, name='projectForm'),
    url(r'^addProject/', views.addProject, name='addProject'),

    url(r'^serverForm/', views.addServerForm, name='addServerForm'),
    url(r'^addServer/', views.addServer, name='addServer'),

    url(r'^addExp/(?P<project_id>[0-9]+)/', views.addExp, name='addExp' ),
    url(r'^expForm/(?P<project_id>[0-9]+)/', views.expForm, name='expForm' ),
    url(r'^expDetail/(?P<pk>[0-9]+)/$', views.exp, name='expDetail'),

    url(r'^(?P<project_id>[0-9]+)/addTodo$', views.addTodo, name='addTodo'),
    url(r'^(?P<project_id>[0-9]+)/(?P<todo_id>[0-9]+)/modifyTodo$', views.modifyTodo, name='modifyTodo'),
]
