# encoding: utf-8

from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps import GenericSitemap, Sitemap

from zds.article.models import Article
from zds.forum.models import Category, Forum, Topic
from zds.tutorial.models import Tutorial

from . import settings


# SiteMap data
class TutoSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 1

    def items(self):
        return Tutorial.objects.filter(sha_public__isnull=False)

    def lastmod(self, tuto):
        if tuto.update is None:
            return tuto.pubdate
        else:
            return tuto.update

    def location(self, tuto):
        return tuto.get_absolute_url_online()


class ArticleSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 1

    def items(self):
        return Article.objects.filter(sha_public__isnull=False)

    def lastmod(self, article):
        if article.update is None:
            return article.pubdate
        else:
            return article.update

    def location(self, article):
        return article.get_absolute_url_online()

sitemaps = {
    'tutos': TutoSitemap,
    'articles': ArticleSitemap,
    'categories': GenericSitemap(
        {'queryset': Category.objects.all()},
        changefreq='yearly',
        priority=0.7
    ),
    'forums': GenericSitemap(
        {'queryset': Forum.objects.filter(group__isnull=True).exclude(pk=settings.ZDS_APP['forum']['beta_forum_id'])},
        changefreq='yearly',
        priority=0.7
    ),
    'topics': GenericSitemap(
        {'queryset': Topic.objects.filter(is_locked=False,
                                          forum__group__isnull=True).exclude(forum__pk=settings.ZDS_APP['forum']['beta_forum_id']),
         'date_field': 'pubdate'},
        changefreq='hourly',
        priority=0.7
    ),
}


admin.autodiscover()


urlpatterns = patterns('',
                       url(r'^tutoriels/', include('zds.tutorial.urls')),
                       url(r'^articles/', include('zds.article.urls')),
                       url(r'^forums/', include('zds.forum.urls')),
                       url(r'^mp/', include('zds.mp.urls')),
                       url(r'^membres/', include('zds.member.urls')),
                       url(r'^admin/', include(admin.site.urls)),
                       url(r'^pages/', include('zds.pages.urls')),
                       url(r'^galerie/', include('zds.gallery.urls')),
                       url(r'^rechercher/', include('zds.search.urls')),
                       url(r'^munin/', include('zds.munin.urls')),
                       url('', include('social.apps.django_app.urls', namespace='social')),
                       url('', include('django.contrib.auth.urls', namespace='auth')),
                       ('^munin/', include('munin.urls')),

                       url(r'^$', 'zds.pages.views.home'),

                       ) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# API
urlpatterns += patterns('',
                        url(r'^api/', include('rest_framework_swagger.urls')),
                        url(r'^oauth2/', include('oauth2_provider.urls', namespace='oauth2_provider')),
                        url(r'^api/membres/', include('zds.member.api.urls')),
                        )

# SiteMap URLs
urlpatterns += patterns('django.contrib.sitemaps.views',
                        (r'^sitemap\.xml$',
                         'index',
                         {'sitemaps': sitemaps}),
                        (r'^sitemap-(?P<section>.+)\.xml$',
                            'sitemap',
                            {'sitemaps': sitemaps}),
                        )

if settings.SERVE:
    urlpatterns += patterns('',
                            (r'^static/(?P<path>.*)$',
                             'django.views.static.serve',
                             {'document_root': settings.STATIC_ROOT}),
                            (r'^media/(?P<path>.*)$',
                                'django.views.static.serve',
                                {'document_root': settings.MEDIA_ROOT}),
                            )

# custom view for 500 errors
handler500 = "zds.pages.views.custom_error_500"