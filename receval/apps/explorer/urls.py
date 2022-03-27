from django.conf.urls import url

from . import views

# app_name = 'explorer'
urlpatterns = [
    # ex: /polls/
    url(r'^$', views.view_search, name='search'),
    url(r'^recommendations$', views.view_recommendations, name='recommendations'),
    url(r'^feedback$', views.view_feedback_rating, name='feedback'),
    # url(r'^imprint$', views.imprint, name='imprint'),
    # url(r'^api', views.api, name='api'),
    # url(r'^contact', views.contact, name='contact'),

]

