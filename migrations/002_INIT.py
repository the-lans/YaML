"""Peewee migrations -- 002_INIT.py.
"""

from peewee import SQL, Model, AutoField, DateTimeField, TextField, BooleanField, IntegerField, ForeignKeyField
from backend.db.fields import OptionsField


def migrate(migrator, database, fake=False, **kwargs):
    @migrator.create_model
    class QueryTemplateDB(Model):
        id = AutoField()
        created = DateTimeField(constraints=[SQL('DEFAULT now()')])
        name = TextField(null=False)
        hash = TextField(null=True, unique=True)

        class Meta:
            table_name = 'template_query'

    @migrator.create_model
    class TemplateRowsDB(Model):
        id = AutoField()
        template = ForeignKeyField(
            backref='template_rows_set',
            column_name='template_id',
            field='id',
            model=migrator.orm['template_query'],
            null=True,
        )
        text = TextField(null=False)
        symbols = IntegerField(null=False)
        text_type = OptionsField(
            [
                'No style',
                'Conspiracy theories',
                'TV-reports',
                'Toast',
                'Boy quotes',
                'Advertising slogans',
                'Short stories',
                'Instagram signatures',
                'Wikipedia',
                'Movie synopsis',
                'Horoscope',
                'Folk wisdom',
                'Garage',
            ],
            default='No style',
        )

        class Meta:
            table_name = 'template_rows'

    @migrator.create_model
    class QueryDB(Model):
        id = AutoField()
        created = DateTimeField(constraints=[SQL('DEFAULT now()')])
        template = ForeignKeyField(
            backref='text_query_set',
            column_name='template_id',
            field='id',
            model=migrator.orm['template_query'],
            null=True,
        )
        name = TextField(null=False)
        text = TextField(null=True)

        class Meta:
            table_name = 'text_query'

    @migrator.create_model
    class TextHistoryDB(Model):
        id = AutoField()
        created = DateTimeField(constraints=[SQL('DEFAULT now()')])
        query = ForeignKeyField(
            backref='text_history_set', column_name='query_id', field='id', model=migrator.orm['text_query'], null=False
        )
        next = TextField(null=True)
        liner = TextField(null=True)
        prod = BooleanField(default=False)
        text_type = OptionsField(
            [
                'No style',
                'Conspiracy theories',
                'TV-reports',
                'Toast',
                'Boy quotes',
                'Advertising slogans',
                'Short stories',
                'Instagram signatures',
                'Wikipedia',
                'Movie synopsis',
                'Horoscope',
                'Folk wisdom',
                'Garage',
            ],
            default='No style',
        )

        class Meta:
            table_name = 'text_history'


def rollback(migrator, database, fake=False, **kwargs):
    migrator.remove_model('template_query')
    migrator.remove_model('template_rows')
    migrator.remove_model('text_query')
    migrator.remove_model('text_history')
