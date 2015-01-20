from .base import Janitor
import logging
import sqlalchemy


LOG = logging.getLogger(__name__)


class PostgresJanitor(Janitor):
    ALLOWED_SCHEMES = {'postgres'}

    def clean(self):
        engine = sqlalchemy.create_engine(self.url)

        meta = sqlalchemy.MetaData(bind=engine, reflect=True)

        connection = engine.connect()
        with connection.begin():
            for table_name, table in meta.tables.iteritems():
                for foreign_key in table.foreign_keys:
                    LOG.debug('Removing foreign key %s from table %s',
                              dir(foreign_key.constraint), table_name)
                    self.drop_fk(connection, table_name, foreign_key)

        with connection.begin():
            meta.drop_all()

    def drop_fk(self, connection, table_name, foreign_key):
        connection.execute(
            'ALTER TABLE IF EXISTS %s DROP CONSTRAINT IF EXISTS %s' % (
                table_name,
                foreign_key.constraint.name,
            )
        )
