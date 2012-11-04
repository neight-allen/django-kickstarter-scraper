from django.conf.urls import patterns, include, url
from crawler.api import ProjectResource, RewardResource
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

project_resource = ProjectResource()
reward_resource = RewardResource()


urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'ks_django.views.home', name='home'),
    # url(r'^ks_django/', include('ks_django.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^crawler/$', 'crawler.views.index'),
    # url(r'^crawler/categories/$', 'crawler.views.by_category'),
    url(r'^wordcloud/$', 'crawler.views.wordcloud'),
    url(r'^rewordcloud/$', 'crawler.views.rewordcloud'),
    url(r'^rewordcloud/(?P<category>.+)/$', 'crawler.views.rewordcloud'),
    url(r'^priceof/(?P<word>\w+)/$', 'crawler.views.priceof'),
    url(r'^priceof/(?P<category>.+)/(?P<word>\w+)/$', 'crawler.views.priceof'),
    url(r'^report/(?P<category>.+)/(?P<amount>\d+)/$', 'crawler.views.report'),
    url(r'^api/', include(project_resource.urls)),
    url(r'^api/', include(reward_resource.urls)),
)
