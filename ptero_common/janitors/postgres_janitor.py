from .base import Janitor
from ptero_common import nicer_logging
import sqlalchemy


LOG = nicer_logging.getLogger(__name__)


class PostgresJanitor(Janitor):
    ALLOWED_SCHEMES = {'postgres'}

    def clean(self):
        engine = sqlalchemy.create_engine(self.url)

        self.drop_all_foreign_keys(engine)
        self.drop_all_tables(engine)

    def drop_all_foreign_keys(self, engine):
        meta = sqlalchemy.MetaData(bind=engine, reflect=True)

        with engine.begin() as connection:
            for table_name, table in meta.tables.iteritems():
                for foreign_key in table.foreign_keys:
                    LOG.debug('Removing foreign key %s from table %s',
                              dir(foreign_key.constraint), table_name)
                    self.drop_fk(connection, table_name, foreign_key)

    def drop_all_tables(self, engine):
        meta = sqlalchemy.MetaData(bind=engine, reflect=True)
        meta.drop_all()

    def drop_fk(self, connection, table_name, foreign_key):
        connection.execute(
            'ALTER TABLE IF EXISTS %s DROP CONSTRAINT IF EXISTS %s' % (
                table_name,
                foreign_key.constraint.name,
            )
        )
