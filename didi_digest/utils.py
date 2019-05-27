import urllib

from django.urls import reverse


def reverse_with_query_params(url, query_params={}):
    return reverse(url) + '?' + urllib.parse.urlencode(query_params)
