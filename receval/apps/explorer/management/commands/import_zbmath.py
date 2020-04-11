import logging
import os

import pandas as pd
from django.core.management import BaseCommand
from django.db import IntegrityError, DatabaseError
from tqdm import tqdm

from receval.apps.explorer.experiments.zbmath import ZbMath
from receval.apps.explorer.models import Experiment, Item, Recommendation

logger = logging.getLogger(__name__)

LIPSUM_TEXT = '''Lorem ipsum dolor sit amet, consectetur adipiscing elit. 
Nulla condimentum justo orci, eget placerat dolor placerat at. 
Pellentesque euismod sagittis mi, sed porta ex blandit a. 
Lorem ipsum dolor sit amet, consectetur adipiscing elit. 
Ut felis eros, imperdiet eu ligula id, porta lobortis nisi. 
Sed pellentesque dui sit amet tortor scelerisque, in tincidunt purus aliquet. 
Phasellus et tempor risus, sit amet malesuada arcu. 
Proin vitae dui tincidunt, venenatis purus ac, luctus tortor.'''


class Command(BaseCommand):
    help = 'Import zbMATH data'

    def add_arguments(self, parser):
        parser.add_argument('--input', type=str, required=True, help='Path to CSV or "dummy" for example data')
        parser.add_argument('--limit', type=int, default=0, help='Limit number of rows to be imported')
        parser.add_argument('--empty', action='store_true', default=False, help='Empty existing index')
        parser.add_argument('--lipsum', action='store_true', default=False, help='Use `Lorem ipsum` as dummy body text')

    def handle(self, *args, **options):
        exp = Experiment.objects.get(name='zbmath')

        if not exp:
            raise ValueError('Experiment is not set!')

        manager = ZbMath()

        if options['empty']:
            Item.objects.filter(experiment=exp).delete()
            deleted, rows_count = Recommendation.objects.filter(experiment=exp).delete()

            logger.info(f'All existing records deleted for {exp}: {rows_count}')

        if options['input'] == 'dummy':

            zbl_ids = [
                '0532.33006',
                '1040.11074',
                '0665.33008',
                '1173.33305',
            ]

            for zbl_id in zbl_ids:
                item, created = Item.objects.get_or_create(experiment=exp, external_id=zbl_id)
                item.data = manager.get_item_data(zbl_id=zbl_id)
                item.title = item.data['title']
                item.save()

                print(f'Saved: {item}')
        else:
            # read from CSV
            fp = options['input']

            if not os.path.exists(fp) or not os.path.isfile(fp):
                raise ValueError(f'Cannot read input from: {fp}')

            df = pd.read_csv(fp, names=['seed_id', 'recommendation_id', 'rank', 'score'], index_col=None)

            logger.info(f'CSV loaded with {len(df)} records from {fp}')

            if options['limit'] > 0:
                df = df[:options['limit']].copy()
                logger.info(f'Import limited to {options["limit"]} rows')

            # seed_id, recommendation_id, rank_id, score

            unique_item_ids = set(df['seed_id'].values.tolist() + df['recommendation_id'].values.tolist())

            logger.info(f'Adding {len(unique_item_ids)} unique items to db')

            doc_id2item_id = {}

            items_skipped = 0
            recs_skipped = 0

            # Add items for all recs
            for doc_id in tqdm(unique_item_ids, total=len(unique_item_ids)):
                try:
                    data = manager.get_item_data(doc_id=doc_id)

                    if options['lipsum']:
                        data['text'] = LIPSUM_TEXT

                    item = Item(experiment=exp, external_id=data['zbl_id'], data=data)

                    if 'title' in data:
                        # Ensure that title has correct length
                        item.title = data['title'][:Item._meta.get_field('title').max_length-1]

                    try:
                        item.save()

                        doc_id2item_id[doc_id] = item.pk
                    except IntegrityError as e:
                        logger.error(f'Cannot add item (integrity error): {e}; {item}')
                        items_skipped += 1
                    except DatabaseError as e:
                        logger.error(f'Cannot add item (database error): {e}; {item}')
                        items_skipped += 1
                except ValueError as e:
                    logger.error(f'Cannot add item: {e}')
                    items_skipped += 1

            # Adding recommendations
            logger.info(f'Adding {len(df)} recommendations to db')

            for idx, row in tqdm(df.iterrows(), total=len(df)):
                if row['seed_id'] in doc_id2item_id and row['recommendation_id'] in doc_id2item_id:
                    rec = Recommendation(
                        experiment=exp,
                        seed_item_id=doc_id2item_id[row['seed_id']],
                        recommended_item_id=doc_id2item_id[row['recommendation_id']],
                        rank=row['rank'],
                        score=row['score']
                    )
                    try:
                        rec.save()
                    except IntegrityError as e:
                        logger.error(f'Cannot add recommendation (integrity error): {e}; {rec}')
                        items_skipped += 1
                    except DatabaseError as e:
                        logger.error(f'Cannot add recommendation (database error): {e}; {rec}')
                        items_skipped += 1
                else:
                    recs_skipped += 1

            logger.info(f'Items skipped: {items_skipped}; Recommendations skipped: {recs_skipped}')

        logger.info('Done.')