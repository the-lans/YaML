from peewee import TextField, BooleanField, ForeignKeyField

from backend.models.base import BaseItem
from backend.db.base import BaseDBItem
from backend.db.fields import OptionsField
from backend.models.text_query import QueryDB
from backend.db.types import TEXT_TYPES


class TextHistoryDB(BaseDBItem):
    query = ForeignKeyField(QueryDB, null=True)
    next = TextField(null=True)
    liner = TextField(null=True)
    prod = BooleanField(default=False)
    text_type = OptionsField(TEXT_TYPES, default='No style')

    @property
    async def dict(self):
        return {
            'id': self.id,
            'created': self.created,
            'query_id': self.query_id,
            'next': self.next,
            'liner': self.liner,
            'prod': self.prod,
            'text_type': self.text_type,
        }

    class Meta:
        table_name = 'text_history'


TextHistory = TextHistoryDB.get_class('TextHistory', BaseItem)
