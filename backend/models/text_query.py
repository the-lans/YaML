from peewee import TextField, ForeignKeyField

from backend.models.base import BaseItem
from backend.db.base import BaseDBItem
from backend.models.template_query import QueryTemplateDB


class QueryDB(BaseDBItem):
    template = ForeignKeyField(QueryTemplateDB, null=True)
    name = TextField(null=False)
    text = TextField(null=True)

    class Meta:
        table_name = 'text_query'


TextQuery = QueryDB.get_class('TextQuery', BaseItem)
