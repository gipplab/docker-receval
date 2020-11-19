from django.apps import AppConfig


class AspectKNNConfig(AppConfig):
    name = 'receval.apps.aspect_knn'

    def ready(self):
        from receval.apps.explorer.templatetags import string_filters

        if string_filters:
            pass


# def global_context_processor(request):
#     # print(request.user.is_authenticated())
#
#     return {
#         'title': 'Hello world',
#         'site': {
#             'title': 'Recommender Evaluation'
#         },
#         'wiki': settings.WIKI_DOMAIN,
#         # 'canonical': '',
#         # 'nav': '',
#         'searchQuery': request.GET.get('q') if 'q' in request.GET else '',
#         'user': request.user if hasattr(request, 'user') else None,
#     }