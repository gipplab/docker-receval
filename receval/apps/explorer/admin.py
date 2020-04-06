from django.contrib import admin

from receval.apps.explorer.models import RecommendationSet, Recommendation, Item, Experiment, Feedback

admin.site.register(RecommendationSet)
admin.site.register(Recommendation)
admin.site.register(Item)
admin.site.register(Experiment)
admin.site.register(Feedback)
