from .base import Janitor
import logging
import sqlalchemy


LOG = logging.getLogger(__name__)


class PostgresJanitor(Janitor):
    ALLOWED_SCHEMES = {'postgres'}

    def clean(self):
        engine = sqlalchemy.create_engine(self.url)

        meta = sqlalchemy.MetaData()
        meta.reflect(bind=engine)

        for name, table in meta.tables.iteritems():
            LOG.debug('Deleting table %s', name)
            engine.execute(table.drop())
