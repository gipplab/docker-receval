import csv
import json
import re

from django.core.management import BaseCommand

from receval.apps.explorer.models import RecommendationSet


class Command(BaseCommand):
    help = 'Processes Citolytics ES output'
    country = None

    def add_arguments(self, parser):
        # parser.add_argument('--output', type=str, default='http://localhost:9200')

        parser.add_argument('--input', type=str)
        # parser.add_argument('--storage', type=str, default='es')

        parser.add_argument('--limit', type=int, default=0)
        parser.add_argument('--start', type=int, default=0)

        parser.add_argument('--max-lines', type=int, default=-1)

        # parser.add_argument('--source', type=str, default='juris')
        # parser.add_argument('--post', type=str, default='keep')
        # parser.add_argument('--post-move-path', type=str, default=None)
        #
        parser.add_argument('--verbose', action='store_true', default=False)

        parser.add_argument('--override', action='store_true', default=False, help='Override existing index')
        parser.add_argument('--empty', action='store_true', default=False, help='Empty existing index')

    def empty(self):
        RecommendationSet.objects.all().delete()

    def handle(self, *args, **options):

        # Delete all old items
        if options['empty']:
            self.empty()

        counter = 0

        with open(options['input']) as f:
            line_i = 1
            doc_id = None

            for line in f:
                # print(line)

                if line_i > options['start']:
                    if (line_i % 2) == 0:
                        # doc line
                        recs = json.loads(line)['doc']['citolytics']

                        # print('#%s >> %s' % (doc_id, recs))
                        # break
                        # insert to do

                        rs = RecommendationSet(page_id=doc_id, recommendations=json.dumps(recs), source='cpa')
                        rs.save()
                        counter += 1

                        doc_id = None

                    else:

                        # action line
                        doc_id = json.loads(line)['update']['_id']
                        # print('ACTION = %s ' % line)

                # print('....')
                line_i += 1

                if line_i > options['limit'] > 0:
                    break

        print('done')
        print('docs added: %i' % counter)
