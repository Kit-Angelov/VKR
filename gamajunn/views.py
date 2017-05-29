from django.shortcuts import render, get_object_or_404, render_to_response
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import RequestContext, loader
from django.core.urlresolvers import reverse
from .models import Article
from django.contrib.auth.models import User
from .forms import ArtForm, AuthForm
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import auth
from django.utils import timezone


def index(request):
    latest_article_list = Article.objects.order_by('-pub_date')[:5]
    context = {'latest_article_list': latest_article_list}
    return render(request, 'gamajunn/index.html', context)


def detail(request, article_id):
    article = get_object_or_404(Article, pk=article_id)
    return render(request, 'gamajunn/detail.html', {'article': article})


def new_art(request):
    if request.method == 'POST':
        form = ArtForm(request.POST)
        if form.is_valid():
            form_data = form.cleaned_data
            new_article = Article(article_title=form_data['title'],
                                                    article_text=form_data['text'],
                                                    pub_date=timezone.now(), author=request.user)
            new_article.save()
            return HttpResponseRedirect(reverse('gamajunn:index'))
    else:
        form = ArtForm
        return render(request, 'gamajunn/new_art.html', {'form': form})


def register_user(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('gamajunn:index'))

    else:
        form = UserCreationForm()
    return render(request, 'reg_auth/registration.html', {'form': form})


def login(request):
    if request.method == 'POST':
        form = AuthForm(request.POST)
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            user = auth.authenticate(username=username, password=password)
            if user is not None and user.is_active:
                # Правильный пароль и пользователь "активен"
                auth.login(request, user)
                # Перенаправление на "правильную" страницу
                return HttpResponseRedirect(reverse('gamajunn:index'))
    else:
        form = AuthForm()
    return render(request, 'reg_auth/auth.html', {'form': form})


def logout(request):
    auth.logout(request)
    return HttpResponseRedirect(reverse('gamajunn:index'))
