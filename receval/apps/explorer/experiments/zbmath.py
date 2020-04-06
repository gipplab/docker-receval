import logging

from django.conf import settings
from sqlalchemy.exc import OperationalError

from receval.apps.explorer.experiments import BaseExperiment
from sqlalchemy import create_engine
from sqlalchemy.sql import text

logger = logging.getLogger(__name__)


class ZbMath(BaseExperiment):
    db = None

    def get_db(self):
        if not self.db:
            if not settings.ZBMATH_DATABASE_URL:
                raise ValueError('ZBMATH_DATABASE_URL is not set!')

            conn_string = settings.ZBMATH_DATABASE_URL
            logger.info(f'ZB MATH database: {conn_string}')

            if settings.ZBMATH_SSL_CERT and settings.ZBMATH_SSL_KEY and settings.ZBMATH_SSL_ROOTCERT:
                conn_args = {
                    # "sslmode": "verify-full",
                    "sslcert": settings.ZBMATH_SSL_CERT,
                    "sslkey": settings.ZBMATH_SSL_KEY,
                    "sslrootcert": settings.ZBMATH_SSL_ROOTCERT,
                }

                logger.info(f'SSL connection: {conn_args}')
            else:
                conn_args = {}

            try:
                self.db = create_engine(conn_string, connect_args=conn_args)
            except OperationalError:
                # try again
                self.db = create_engine(conn_string, connect_args=conn_args)

        return self.db

    def get_item_data(self, doc_id=None, zbl_id=None) -> dict:

        if doc_id:
            s = text("""SELECT * FROM zbmath.math_documents WHERE id = :doc_id""")
        elif zbl_id:
            s = text("""SELECT * FROM zbmath.math_documents WHERE zbl_id = :zbl_id""")
        else:
            raise ValueError('Either doc_id or zbl_id must be set')

        res = self.get_db().execute(s, doc_id=doc_id, zbl_id=zbl_id)
        rows = [dict(row) for row in res]

        if len(rows) == 1:

            data = rows[0]

            # Get text
            s = text("""SELECT text FROM zbmath.math_reviews WHERE document = :doc_id LIMIT 1""")
            res = self.get_db().execute(s, doc_id=data['id'])

            rows = [dict(row) for row in res]

            if len(rows) == 1:
                data['text'] = rows[0]['text']
            else:
                raise ValueError('Invalid number of rows returned')

            # Citation count
            s = text("""SELECT COUNT(*) FROM zbmath.math_references WHERE zbl_id = :zbl_id""")
            res = self.get_db().execute(s, zbl_id=data['zbl_id'])

            rows = [dict(row) for row in res]

            if len(rows) == 1:
                data['citation_count'] = rows[0]['count']
            else:
                raise ValueError('Invalid number of rows returned')

            return data
        else:
            raise ValueError('Invalid number of rows returned')

