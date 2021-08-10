from typing import Optional
from peewee import TextField, ForeignKeyField

from backend.models.base import BaseItem
from backend.db.base import BaseDBItem
from backend.models.template_query import QueryTemplateDB


class QueryDB(BaseDBItem):
    template = ForeignKeyField(QueryTemplateDB, null=True)
    name = TextField(null=False)
    text = TextField(null=True)

    @property
    async def dict(self):
        return {
            'id': self.id,
            'created': self.created,
            'template_id': self.template_id,
            'name': self.name,
            'text': self.text,
        }

    class Meta:
        table_name = 'text_query'


# TextQuery = QueryDB.get_class('TextQuery', BaseItem)


class TextQuery(BaseItem):
    template_id: Optional[int] = None
    name: str
    text: Optional[str] = None

    @property
    async def dict(self):
        return {
            'template_id': self.template_id,
            'name': self.name,
            'text': self.text,
        }
