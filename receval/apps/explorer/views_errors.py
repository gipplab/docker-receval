import logging

from django.conf import settings
from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _


logger = logging.getLogger(__name__)


def view_error500(request, exception=None):
    return render(request, 'errors/500.html', {
        'title': _('Error') + ' 500',
        'exception': exception
    }, status=500)


def view_error404(request, exception=None):
    return render(request, 'errors/404.html', {
        'title': '%s - %s' % (_('Error'), _('Not found')),
        'exception': exception
    }, status=404)


def view_error_permission_denied(request, exception=None):
    return render(request, 'errors/permission_denied.html', {
        'title': '%s - %s' % (_('Error'), _('Permission denied')),
        'exception': exception
    }, status=401)


def view_error_bad_request(request, exception=None):
    return render(request, 'errors/bad_request.html', {
        'title': '%s - %s' % (_('Error'), _('Bad request')),
        'exception': exception
    }, status=400)
