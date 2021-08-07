from peewee import TextField, BooleanField, ForeignKeyField

from backend.models.base import BaseItem
from backend.db.base import BaseDBItem
from backend.db.fields import OptionsField
from backend.models.text_query import QueryDB


class TextHistoryDB(BaseDBItem):
    query = ForeignKeyField(QueryDB, null=True)
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


TextHistory = TextHistoryDB.get_class('TextHistory', BaseItem)
