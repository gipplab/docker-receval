import json

from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from jsonfield import JSONField


# deprecated
class RecommendationSet(models.Model):
    page_id = models.BigIntegerField()
    recommendations = models.TextField()
    source = models.CharField(max_length=3)
    recs = None

    class Meta:
        indexes = [
            models.Index(fields=['page_id', 'source'])
            ]

    def get_recommendations(self):
        if self.recs is None:
            self.recs = json.loads(self.recommendations)
        # print(recs)

        sorted_recs = sorted(self.recs, key=lambda x: x['score'], reverse=True)

        # print()

        return sorted_recs

    def __str__(self):
        return 'RecommendationSet(page_id=%s, source=%s)' % (self.page_id, self.source)


class Experiment(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return 'Experiment(pk=%s, name=%s)' % (self.pk, self.name)


class Item(models.Model):
    title = models.CharField(
        max_length=200,
        null=True,
        blank=True,
    )
    external_id = models.CharField(max_length=200)
    experiment = models.ForeignKey(
        Experiment,
        on_delete=models.CASCADE
    )
    data = JSONField()

    class Meta:
        unique_together = (('external_id', 'experiment'),)

    def get_absolute_url(self):
        return reverse('recommendations') + '?seed_pk=%s' % self.pk

    def get_title(self):
        if self.title:
            return self.title
        elif 'title' and self.data:
            return self.data['title']
        else:
            return 'Untitled item'

    def __str__(self):
        return 'Item(pk=%s, external_id=%s)' % (self.pk, self.external_id)


class Recommendation(models.Model):
    seed_item = models.ForeignKey(
        Item,
        on_delete=models.CASCADE,
        related_name='seed_item',
    )
    recommended_item = models.ForeignKey(
        Item,
        on_delete=models.CASCADE,
        related_name='recommended_item',
    )
    experiment = models.ForeignKey(
        Experiment,
        on_delete=models.CASCADE
    )
    source = models.CharField(max_length=200, help_text='The system that generated this recommendation')
    rank = models.PositiveSmallIntegerField()
    score = models.FloatField()

    class Meta:
        unique_together = (('seed_item', 'rank', 'source'),)

    def __str__(self):
        return 'Recommendation(seed=%s, recommended=%s)' % (self.seed_item, self.recommended_item)


class Feedback(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    recommendation = models.ForeignKey(
        Recommendation,
        on_delete=models.CASCADE
    )
    created_date = models.DateTimeField(
        auto_now_add=True,
        help_text='Entry is created at this date time',
    )
    updated_date = models.DateTimeField(
        auto_now=True,
        help_text='Date time of last change',
    )
    rating = models.SmallIntegerField(
        null=True,
        blank=True,
        help_text='Likert scale'
    )
    is_relevant = models.NullBooleanField(
    )
    comment = models.TextField(
        null=True,
        blank=True,
        default='',
    )

    class Meta:
        unique_together = (('author', 'recommendation'),)

    def __str__(self):
        return 'Feedback(author=%s, recommendation=%s)' % (self.author, self.recommendation)

