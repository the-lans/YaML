from peewee import TextField, IntegerField, ForeignKeyField

from backend.models.base import BaseItem
from backend.db.base import BaseDBModel, BaseDBItem
from backend.db.fields import OptionsField


class QueryTemplateDB(BaseDBItem):
    name = TextField(null=False)
    hash = TextField(null=True, unique=True)

    @property
    async def dict(self):
        return {
            'id': self.id,
            'created': self.created,
            'name': self.name,
            'hash': self.hash,
        }

    class Meta:
        table_name = 'template_query'


class TemplateRowsDB(BaseDBModel):
    template = ForeignKeyField(QueryTemplateDB, null=True)
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

    @property
    async def dict(self):
        return {
            'id': self.id,
            'template_id': self.template_id,
            'text': self.text,
            'symbols': self.symbols,
            'text_type': self.text_type,
        }

    class Meta:
        table_name = 'template_rows'


QueryTemplate = QueryTemplateDB.get_class('QueryTemplate', BaseItem)
TemplateRows = TemplateRowsDB.get_class('TemplateRows', BaseItem)
