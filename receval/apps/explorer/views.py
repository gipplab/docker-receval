import json
import logging
import re

import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from requests.exceptions import ConnectionError

# Create your views here.
from receval.apps.explorer.models import RecommendationSet, Item, Experiment, Recommendation, Feedback

logger = logging.getLogger(__name__)


def get_mlt_from_db(page_id):
    # Fetch mlt from db
    try:
        mlt = RecommendationSet.objects.get(page_id=page_id, source='mlt')

    except RecommendationSet.DoesNotExist:
        mlt = None
    return mlt


def get_mlt_from_api(page_title):
    # From API
    mlt_query = 'morelike:' + page_title
    api_url = 'https://%s/w/api.php?action=query&list=search&srsearch=%s&utf8=&format=json' % (settings.WIKI_DOMAIN, mlt_query)
    api_res = requests.get(api_url).text

    res = json.loads(api_res)
    recs = []
    for key, item in enumerate(res['query']['search']):
        recs.append({
            'title': item['title'],
            'score': len(res['query']['search']) - key,
        })

    mlt = RecommendationSet()
    mlt.recs = recs

    return mlt


def get_mlt_from_es(page_id):
    # MLT request
    req = {
        "_source": [
            "title"
        ],
        "query": {
            "more_like_this": {
                "fields": ["title", "text"],
                "like": [
                    {
                        "_index": settings.ES_INDEX,
                        "_type": settings.ES_TYPE,
                        "_id": page_id
                    }
                ],
                "min_term_freq": 1,
                "max_query_terms": 12
            }
        }
    }
    # print(json.dumps(req))
    res = requests.get(settings.ES_URL + '/_search?pretty', proxies=settings.ES_PROXY, json=req, verify=False)
    # print(res.text)

    # Build recommendation set
    if 'hits' in res.json():
        recs = []
        for hit in res.json()['hits']['hits']:
            # print(hit['_score'])
            # print(hit['_source']['title'])

            recs.append({
                'title': hit['_source']['title'],
                'score': hit['_score'],
            })
        mlt = RecommendationSet()
        mlt.recs = recs
        return mlt

    return None


def old_index(request):
    query = request.GET.get('query') or request.GET.get('q')
    error = None
    seeds = None

    cpa = None
    mlt_popular = None
    mlt_plain = None

    if query is not None:
        # Find seed article
        api_url = 'https://%s/w/api.php?action=query&list=search&srsearch=%s&utf8=&format=json' % (WIKI_DOMAIN, query)
        api_res = requests.get(api_url).text

        res = json.loads(api_res)

        seeds = res['query']['search']
        seed = res['query']['search'][0]

        # Load CPA recommendations
        try:
            cpa = RecommendationSet.objects.get(page_id=seed['pageid'], source='cpa')
        except RecommendationSet.DoesNotExist:
            cpa = None

        # Load MLT recommendations (from api and ES)
        try:
            mlt_popular = get_mlt_from_api(seed['title'])
            mlt_plain = get_mlt_from_es(seed['pageid'])
        except ConnectionError:
            error = 'Could not retrieve MLT results. SSH Tunnel running?'
    else:
        query = ''

    return render(request, 'explorer/old_index.html', {
        'title': 'Explorer',
        'searchQuery': query,
        'seeds': seeds,
        'cpa': cpa,
        'mlt_popular': mlt_popular,
        'mlt_plain': mlt_plain,
        'error': error
    })


@login_required
def view_feedback_delete(request, feedback_id):
    feedback = get_object_or_404(Feedback, pk=feedback_id, author=request.user)
    feedback.delete()

    return redirect(reverse('feedback'))


@login_required
def view_feedback_rating(request):
    rec = get_object_or_404(Recommendation, pk=request.POST.get('recommendation_pk'))

    feedback, created = Feedback.objects.get_or_create(recommendation=rec, author=request.user)

    feedback.is_relevant = request.POST.get('is_relevant')
    feedback.save()

    # request.user.

    messages.success(request, _('Your feedback has been saved. Thank you!'))

    return redirect(reverse('recommendations') + '?seed_pk=%s' % rec.seed_item.pk)


@login_required
def view_feedback_comment(request):
    rec = get_object_or_404(Recommendation, pk=request.POST.get('recommendation_pk'))

    print(request.POST)

    feedback, created = Feedback.objects.get_or_create(recommendation=rec, author=request.user)


    feedback.comment = request.POST.get('comment')
    feedback.save()

    messages.success(request, _('Your comment has been saved. Thank you!'))

    return redirect(reverse('recommendations') + '?seed_pk=%s' % rec.seed_item.pk)


@login_required
def view_feedback(request):
    feedbacks = Feedback.objects.filter(author=request.user).select_related('recommendation')

    return render(request, 'explorer/feedback.html', {
        'title': 'My Feedback',
        'feedbacks': feedbacks,
    })


def view_recommendations(request):
    exp = Experiment.objects.get(name='zbmath')
    exp.base_url = 'https://zbmath.org'

    if request.GET.get('seed_pk'):
        logger.debug('Select seed by pk: %s' % request.GET.get('seed_pk'))

        seed_item = get_object_or_404(Item, experiment=exp, pk=request.GET.get('seed_pk'))
    elif request.GET.get('seed_external_id'):
        logger.debug('Select seed by external ID: %s' % request.GET.get('seed_external_id'))

        seed_item = get_object_or_404(Item, experiment=exp, external_id=request.GET.get('seed_external_id'))
    else:
        logger.debug('Random seed for experiment: %s' % exp)

        # random
        try:
            seed_item = Item.objects.filter(experiment=exp).order_by('?')[0]
        except IndexError:
            # no items available
            logger.warning('No items available for experiment: %s' % exp)
            seed_item = None

    # get recommendations from seed
    if seed_item:
        # recs = Recommendation.objects.filter(experiment=exp, seed_item=seed_item).order_by('rank')
        recs = Recommendation.objects.filter(experiment=exp, seed_item=seed_item).order_by('rank')

        # limit to top k
        if settings.RECOMMENDATIONS_TOP_K > 0:
            recs = recs[:settings.RECOMMENDATIONS_TOP_K]

        rec_pks = [rec.pk for rec in recs]
    else:
        recs = None
        rec_pks = []

    if request.user.is_authenticated:
        feedbacks = Feedback.objects.filter(recommendation_id__in=rec_pks, author=request.user)
        feedbacks_by_recommendation = {f.recommendation_id: f for f in feedbacks}

        print(feedbacks)
        print(feedbacks_by_recommendation)
    else:
        feedbacks = []
        feedbacks_by_recommendation = {}

    # Recommendation().feedback_set.get(author=request.user)

    return render(request, 'explorer/recommendations.html', {
        'title': '%s - Explorer' % seed_item.title,
        'experiment': exp,
        'seed': seed_item,
        'recommendations': recs,
        'feedbacks_by_recommendation': feedbacks_by_recommendation,
    })


def view_search(request):
    # exp = Experiment.objects.get(name='zbmath')

    q = request.GET.get('q', None)  # type: str
    zbl_id_pattern = re.compile(r'^([0-9]+)\.([0-9]+)$')

    if q:
        # is id?
        if q.isnumeric():
            items = Item.objects.filter(id=q)
        elif zbl_id_pattern.search(q):
            items = Item.objects.filter(external_id=q)

        else:
            # keyword search
            items = Item.objects.filter(title__contains=q, seed_item__isnull=False).distinct()[:100]

    else:
        items = []

    # Random items
    random_items = Item.objects.filter(seed_item__isnull=False).select_related('experiment').order_by('?').distinct()[:100]

    return render(request, 'explorer/search.html', {
        'title': 'Search',
        'items': items,
        'random_items': random_items,
    })