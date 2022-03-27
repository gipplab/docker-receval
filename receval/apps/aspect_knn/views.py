import json
import logging
import os
import random

from django.conf import settings
from django.http import Http404
from django.shortcuts import render
from django.urls import reverse
from gensim.models import KeyedVectors
from smart_open import open
from whoosh import index
from whoosh.analysis import StemmingAnalyzer
from whoosh.fields import Schema, TEXT, KEYWORD, ID
from whoosh.qparser import QueryParser

logger = logging.getLogger(__name__)


class Paper(object):
    """

    {
        "paper_url": "https://paperswithcode.com/paper/on-the-minimal-teaching-sets-of-two",
        "arxiv_id": "1307.1058",
        "title": "On the minimal teaching sets of two-dimensional threshold functions",
        "abstract": "It is known that a minimal teaching set of any threshold function on the\ntwodimensional rectangular grid consists of 3 or 4 points. We derive exact\nformulae for the numbers of functions corresponding to these values and further\nrefine them in the case of a minimal teaching set of size 3. We also prove that\nthe average cardinality of the minimal teaching sets of threshold functions is\nasymptotically 7/2.\n  We further present corollaries of these results concerning some special\narrangements of lines in the plane.",
        "url_abs": "http://arxiv.org/abs/1307.1058v2",
        "url_pdf": "http://arxiv.org/pdf/1307.1058v2.pdf",
        "proceeding": null,
        "authors": ["Max A. Alekseyev", "Marina G. Basova", "Nikolai Yu. Zolotykh"], "tasks": [], "date": "2013-07-03", "methods": [], "aspect_methods": [], "aspect_datasets": [], "aspect_tasks": [],
         "paper_id": "9gWe1QI8-1"
         }

    """
    title = ''
    paper_id = ''
    rank = 0

    def __init__(self, **entries):
        self.__dict__.update(entries)

    def get_absolute_url(self):
        return reverse('recommendations') + '?seed=%s' % self.paper_id

    def get_title(self):
        return self.title

    def set_rank(self, rank):
        self.rank = rank
        return self


paper_schema = Schema(
    paper_id=ID(stored=True),
    title=TEXT(stored=True),
    abstract=TEXT(analyzer=StemmingAnalyzer()),
    paper_url=TEXT(),
    aspect_tasks=KEYWORD,
    aspect_methods=KEYWORD,
    aspect_datasets=KEYWORD,
)

if settings.ASPECT_KNN_WHOOSH_INDEX_PATH and os.path.exists(settings.ASPECT_KNN_WHOOSH_INDEX_PATH):
    ix = index.open_dir(settings.ASPECT_KNN_WHOOSH_INDEX_PATH)  #'/Users/maos01/Desktop/special-docembeds-release-files/output/pwc/whoosh_index'
else:
    ix = None


# Load vector models
generic_vecs = KeyedVectors.load_word2vec_format(settings.ASPECT_KNN_GENERIC_W2V_PATH, limit=settings.ASPECT_KNN_LIMIT) if settings.ASPECT_KNN_GENERIC_W2V_PATH and os.path.exists(settings.ASPECT_KNN_GENERIC_W2V_PATH) else None #  '/Users/maos01/Downloads/specter.1k.w2v.txt'
task_vecs = KeyedVectors.load_word2vec_format(settings.ASPECT_KNN_TASK_W2V_PATH, limit=settings.ASPECT_KNN_LIMIT) if settings.ASPECT_KNN_TASK_W2V_PATH and os.path.exists(settings.ASPECT_KNN_TASK_W2V_PATH) else None
method_vecs = KeyedVectors.load_word2vec_format(settings.ASPECT_KNN_METHOD_W2V_PATH, limit=settings.ASPECT_KNN_LIMIT) if settings.ASPECT_KNN_METHOD_W2V_PATH and os.path.exists(settings.ASPECT_KNN_METHOD_W2V_PATH) else None
dataset_vecs = KeyedVectors.load_word2vec_format(settings.ASPECT_KNN_DATASET_W2V_PATH, limit=settings.ASPECT_KNN_LIMIT) if settings.ASPECT_KNN_DATASET_W2V_PATH and os.path.exists(settings.ASPECT_KNN_DATASET_W2V_PATH) else None


# Normalize vectors
if generic_vecs and task_vecs and method_vecs and dataset_vecs:
    generic_vecs.init_sims(replace=True)
    task_vecs.init_sims(replace=True)
    method_vecs.init_sims(replace=True)
    dataset_vecs.init_sims(replace=True)


paper_id2paper = {}
if settings.ASPECT_KNN_DOCS_PATH and os.path.exists(settings.ASPECT_KNN_DOCS_PATH):  # './data/paperswithcode_docs.jsonl
    with open(settings.ASPECT_KNN_DOCS_PATH, 'r') as f:
        for line in f:
            paper = Paper(**json.loads(line))
            paper_id2paper[paper.paper_id] = paper


def view_recommendations(request):
    seed_id = request.GET.get('seed', None)

    if not (generic_vecs and task_vecs and method_vecs and dataset_vecs):
        raise Http404('Document embeddings are unavailable.')

    if seed_id not in paper_id2paper:
        raise Http404('No paper matches the given query.')

    seed = paper_id2paper[seed_id]

    try:
        generic_recommendations = [paper_id2paper[pid].set_rank(rank) for pid, rank in
                                   generic_vecs.most_similar(seed_id, topn=settings.RECOMMENDATIONS_TOP_K)]
        task_recommendations = [paper_id2paper[pid].set_rank(rank) for pid, rank in
                                   task_vecs.most_similar(seed_id, topn=settings.RECOMMENDATIONS_TOP_K)]
        method_recommendations = [paper_id2paper[pid].set_rank(rank) for pid, rank in
                                   method_vecs.most_similar(seed_id, topn=settings.RECOMMENDATIONS_TOP_K)]
        dataset_recommendations = [paper_id2paper[pid].set_rank(rank) for pid, rank in
                                   dataset_vecs.most_similar(seed_id, topn=settings.RECOMMENDATIONS_TOP_K)]
    except KeyError:
        raise Http404('No recommendations can available for this paper')

    logger.info(f'generic_recommendations: {len(generic_recommendations)}')
    logger.info(f'task_recommendations: {len(task_recommendations)}')
    logger.info(f'method_recommendations: {len(method_recommendations)}')
    logger.info(f'dataset_recommendations: {len(dataset_recommendations)}')
    logger.info(f'RECOMMENDATIONS_TOP_K: {settings.RECOMMENDATIONS_TOP_K}')

    return render(request, 'aspect_knn/recommendations.html', {
        'title': seed.get_title() + ' - Recommendations',
        'seed': seed,
        'generic_recommendations': generic_recommendations,
        'task_recommendations': task_recommendations,
        'method_recommendations': method_recommendations,
        'dataset_recommendations': dataset_recommendations,
    })


def view_search(request):
    q = request.GET.get('q', None)  # type: str
    items = []

    logger.info('Search query: %s' % q)

    if q and len(q) > 3:
        if not ix:
            raise Http404('Search index is not initialized.')

        with ix.searcher() as s:
            qp = QueryParser("title", paper_schema)
            wq = qp.parse(q)
            results = s.search(wq, limit=50)
            for r in results:
                # print(r)
                items.append(paper_id2paper[r['paper_id']])

    # random
    if len(paper_id2paper) > 0:
        random_items = [paper_id2paper[pid] for pid in random.sample(paper_id2paper.keys(), 10)]
    else:
        random_items = []

    return render(request, 'aspect_knn/search.html', {
        'title': 'Search',
        'items': items,
        'random_items': random_items,
    })