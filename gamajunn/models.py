from django.db import models
from django.contrib.auth.models import User, UserManager


class Theme(models.Model):
    theme_name = models.CharField(max_length=200)

    def __str__(self):
        return self.theme_name


class Article(models.Model):
    article_title = models.CharField(max_length=200)
    article_text = models.TextField()
    pub_date = models.DateTimeField('date published')
    themes = models.ManyToManyField(Theme)
    author = models.ForeignKey(User, on_delete=models.CASCADE, default=1)

    def __str__(self):
        return self.article_title


class ExpertArticle(models.Model):
    expert_art_title = models.CharField(max_length=200)
    expert_art_text = models.TextField()
    expert_themes = models.ManyToManyField(Theme)

    def __str__(self):
        return self.expert_art_title
