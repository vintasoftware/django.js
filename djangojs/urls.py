from django.conf.urls import patterns, url
from django.views.generic import TemplateView

from djangojs.views import DjangoJsJsonView


urlpatterns = patterns('',
    url(r'^urls$', DjangoJsJsonView.as_view(), name='django_js_json'),
    url(r'^aaa/(\d+)$', TemplateView.as_view(template_name='test1.html'), name='first_test'),
    url(r'^bbb/(?P<test>\w+)$', TemplateView.as_view(template_name='test1.html'), name='second_test'),
)