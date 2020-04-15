from django.contrib import admin

from receval.apps.explorer.models import RecommendationSet, Recommendation, Item, Experiment, Feedback

admin.site.register(RecommendationSet)
admin.site.register(Recommendation)


@admin.register(Experiment)
class ExperimentAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'external_id', 'experiment')
    list_filter = ('experiment__name', )
    actions = []
    list_select_related = ('experiment', )
    # autocomplete_fields = ['experiment']
    search_fields = ['experiment']
    exclude = []


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'recommendation', 'is_relevant', 'comment', 'updated_date')
    # list_filter = ('experiment__name', )
    actions = []
    # list_select_related = ('experiment', )
    # autocomplete_fields = ['experiment']
    # search_fields = ['experiment']
    exclude = []