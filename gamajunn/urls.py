from django.conf.urls import url

from . import views

app_name = 'gamajunn'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<article_id>[0-9]+)/$', views.detail, name='detail'),
    url(r'^new_art/', views.new_art, name='new_art'),
    url(r'^sign_up/', views.register_user, name='register_user'),
    url(r'^login/', views.login, name='login'),
    url(r'^logout/', views.logout, name='logout')
]