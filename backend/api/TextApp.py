from typing import Optional
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from fastapi import Depends, UploadFile, File
from hashlib import sha256
import json
from os.path import splitext
from pydantic.fields import ModelField

from backend.app import app
from backend.models.template_query import QueryTemplate, TemplateRows, QueryTemplateDB, TemplateRowsDB
from backend.models.text_query import TextQuery, QueryDB
from backend.models.text_history import TextHistoryDB
from backend.api.base import BaseAppAuth

router = InferringRouter()


@cbv(router)
class TextApp(BaseAppAuth):
    @classmethod
    async def get_template_id(cls, item_id):
        return await cls.get_one_object(QueryTemplateDB.select().where(QueryTemplateDB.id == item_id))

    @classmethod
    async def get_template_hash(cls, hash):
        return await cls.get_one_object(QueryTemplateDB.select().where(QueryTemplateDB.hash == hash))

    @staticmethod
    async def json_loads(content):
        return json.loads(content.decode('utf-8'))

    @staticmethod
    async def json_dumps(data):
        return json.dumps(data, sort_keys=False, ensure_ascii=False).encode()

    @classmethod
    async def get_json_hash(cls, content):
        data = await cls.json_loads(content)
        sdata = await cls.json_dumps(data)
        return sha256(sdata).hexdigest()

    @router.get("/api/template/list", tags=["Template"])
    async def get_template_list(self):
        return await self.get_list(QueryTemplateDB)

    @router.get("/api/template/{item_id}", tags=["Template"])
    async def get_template_item(self, item_id: int):
        item_db = await self.get_template_id(item_id)
        res = await self.prepare(item_db)
        if item_db is not None:
            res.update(await item_db.dict)
        return res

    @router.post("/api/template/new", tags=["Template"])
    async def post_template_new(
        self,
        name: Optional[str] = "",
        data: UploadFile = File(..., media_type='application/octet-stream'),
    ):
        content = await data.read()
        if not name:
            name = splitext(data.filename)[0]
        hash = await self.get_json_hash(content)
        obj = await self.get_template_hash(hash)
        if obj is None:
            item = QueryTemplate(name=name, hash=hash)
            json_data = await self.json_loads(content)
            res = await QueryTemplateDB.update_or_create(item, ret={"success": True})
            for row in json_data['items']:
                obj = TemplateRows(
                    template_id=res['id'],
                    text=row.get('text'),
                    symbols=row.get('symbols', 300),
                    text_type=row.get('text_type', 'No style'),
                )
                await TemplateRowsDB.update_or_create(obj, ret={"success": True})
            return res
        else:
            return {"success": False}

    @router.get("/api/text/new", tags=["Text"])
    async def get_text_new(self, name: str):
        item = TextQuery(name=name)
        return await QueryDB.update_or_create(item, ret={"success": True})

    @router.get("/api/text/next/{item_id}", tags=["Text"])
    async def get_text_next(self, item_id: int, text: str, next: str, liner: str):
        pass

    @router.get("/api/text/update/{item_id}", tags=["Text"])
    async def get_text_update(self, item_id: int, text: str):
        pass

    @router.get("/api/text/generate/{item_id}", tags=["Text"])
    async def get_text_update(self, item_id: int):
        pass


app.include_router(router)
