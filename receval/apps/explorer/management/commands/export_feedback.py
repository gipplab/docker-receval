import logging
import os

import pandas as pd
from django.core.management import BaseCommand

from receval.apps.explorer.models import Experiment, Feedback

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Export feedback data'

    def add_arguments(self, parser):
        parser.add_argument('experiment', type=str, help='Name of experiment')
        parser.add_argument('output', type=str, help='Write output CSV to this path')
        parser.add_argument('--limit', type=int, default=0, help='Limit number of rows to be exported')
        parser.add_argument('--override', action='store_true', default=False, help='Override if a file exists already at output path')

    def handle(self, *args, **options):

        #Tried= "zbmath" and worked
        exp = Experiment.objects.get(name=options['experiment'])
        # exp = Experiment.objects.get(name='zbmath')

        if not options['override'] and os.path.exists(options['output']):
            raise ValueError('Output path exists already')

        # Fetch all feedback
        feedbacks = Feedback.objects.filter(recommendation__experiment=exp)\
            .select_related('recommendation', 'recommendation__seed_item', 'recommendation__recommended_item')

        rows = []
        for f in feedbacks:  # type: Feedback
            rows.append(dict(
                id=f.id,
                created_date=f.created_date.strftime('%Y-%m-%d %H:%M'),
                updated_date=f.updated_date.strftime('%Y-%m-%d %H:%M'),
                is_relevant=f.is_relevant,
                rating=f.rating,
                comment=f.comment,
                # author
                author__id=f.author.id,
                author__username=f.author.username,
                author__email=f.author.email,
                # recommendation
                recommendation__rank=f.recommendation.rank,
                recommendation__score=f.recommendation.score,
                # seed item
                seed_item__id=f.recommendation.seed_item.id,
                seed_item__external_id=f.recommendation.seed_item.external_id,
                seed_item__title=f.recommendation.seed_item.title,
                # recommended item
                recommended_item__id=f.recommendation.recommended_item.id,
                recommended_item__external_id=f.recommendation.recommended_item.external_id,
                recommended_item__title=f.recommendation.recommended_item.title,
            ))
        df = pd.DataFrame(rows)

        if options['limit'] > 0:
            df = df[:options['limit']].copy()

        df.to_csv(options['output'], index=False)

        logger.info(f'Exported: {len(df)} rows to {options["output"]}')
