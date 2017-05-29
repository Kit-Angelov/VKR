from django.contrib import admin

from .models import Article, Theme, ExpertArticle


class ThemeInline(admin.TabularInline):
    model = Article.themes.through


class ThemeExpertInline(admin.TabularInline):
    model = ExpertArticle.expert_themes.through


class ArticleAdmin(admin.ModelAdmin):
    inlines = [
        ThemeInline,
    ]
    exclude = ('themes',)


class ExpertArticleAdmin(admin.ModelAdmin):
    inlines = [
        ThemeExpertInline,
    ]
    exclude = ('themes',)


class ThemeAdmin(admin.ModelAdmin):
    inlines = [
        ThemeInline,
        ThemeExpertInline,
    ]


admin.site.register(Article, ArticleAdmin)
admin.site.register(Theme, ThemeAdmin)
admin.site.register(ExpertArticle, ExpertArticleAdmin)