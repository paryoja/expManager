from django.conf.urls import url

from . import views

app_name = 'project'
urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^servers/', views.ServerView.as_view(), name='servers'),
    url(r'^(?P<pk>[0-9]+)/$', views.DetailView.as_view(), name='detail'),
    url(r'^(?P<pk>[0-9]+)/exp$', views.ExpView.as_view(), name='exp'),

    url(r'^projectForm/', views.addForm, name='projectForm'),

    url(r'^addProject/', views.addProject, name='addProject'),

    url(r'^(?P<project_id>[0-9]+)/addTodo$', views.addTodo, name='addTodo'),
    url(r'^(?P<project_id>[0-9]+)/(?P<todo_id>[0-9]+)/deleteTodo$', views.deleteTodo, name='deleteTodo'),
]
