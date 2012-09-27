# -*- coding: utf-8 -*-
import json
import logging
import re
import sys

from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.core.urlresolvers import RegexURLPattern, RegexURLResolver
from django.http import HttpResponse
from django.utils.datastructures import SortedDict
from django.views.generic import View

logger = logging.getLogger(__name__)


__all__ = (
    'DjangoJsJsonView',
)

RE_KWARG = re.compile(r"(\(\?P\<(.*?)\>.*?\))")  # Pattern for recongnizing named parameters in urls
RE_ARG = re.compile(r"(\(.*?\))")  # Pattern for recognizing unnamed url parameters


class DjangoJsJsonView(View):
    '''
    List all registered URLs as a JSON object.
    '''
    def get(self, request, *args, **kwargs):
        if not hasattr(settings, 'ROOT_URLCONF'):
            raise Exception
        module = settings.ROOT_URLCONF
        urls = self.get_urls(module)
        return HttpResponse(
            json.dumps(urls, cls=DjangoJSONEncoder),
            mimetype="application/json"
        )

    def get_urls(self, module, prefix=''):
        urls = SortedDict()
        __import__(module)
        root_urls = sys.modules[module]
        patterns = root_urls.urlpatterns

        for pattern in patterns:
            if issubclass(pattern.__class__, RegexURLPattern):
                if pattern.name:
                    full_url = prefix + pattern.regex.pattern
                    for chr in ['^', '$']:
                        full_url = full_url.replace(chr, '')
                    # handle kwargs, args
                    kwarg_matches = RE_KWARG.findall(full_url)
                    if kwarg_matches:
                        for el in kwarg_matches:
                            # prepare the output for JS resolver
                            full_url = full_url.replace(el[0], "<%s>" % el[1])
                    # after processing all kwargs try args
                    args_matches = RE_ARG.findall(full_url)
                    if args_matches:
                        for el in args_matches:
                            full_url = full_url.replace(el, "<>")  # replace by a empty parameter name
                    urls[pattern.name] = "/" + full_url
            elif issubclass(pattern.__class__, RegexURLResolver):
                if pattern.urlconf_name:
                    urls.update(self.get_urls(pattern.urlconf_name, pattern.regex.pattern))
        return urls