from django.conf.urls import patterns, include, url
from django.contrib import admin
from app_name.views import index, MyChatBotView

urlpatterns = patterns('',
	
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', index, name='HomePage'),
	url(r'^facebook_auth/?$', MyChatBotView.as_view()),
)
