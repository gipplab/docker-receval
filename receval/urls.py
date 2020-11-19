"""receval URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import url, include
from django.contrib import admin

# Error handlers
handler500 = 'receval.apps.explorer.views_errors.view_error500'
handler404 = 'receval.apps.explorer.views_errors.view_error404'
handler403 = 'receval.apps.explorer.views_errors.view_error_permission_denied'
handler400 = 'receval.apps.explorer.views_errors.view_error_bad_request'


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^accounts/', include('receval.apps.accounts.urls')),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^explorer/', include('receval.apps.explorer.urls')),
    url(r'', include('receval.apps.aspect_knn.urls')),

]

# DEBUG only views
if settings.DEBUG:
    # Django debug toolbar
    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
