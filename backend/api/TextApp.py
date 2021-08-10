from typing import Optional
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from fastapi import Depends, UploadFile, File
from hashlib import sha256
import json
from os.path import splitext
from urllib.parse import urljoin
import aiohttp

from backend.app import app
from backend.models.template_query import QueryTemplate, TemplateRows, QueryTemplateDB, TemplateRowsDB
from backend.models.text_query import TextQuery, QueryDB
from backend.models.text_history import TextHistory, TextHistoryDB
from backend.api.base import BaseAppAuth
from backend.db.base import manager
from backend.db.types import TEXT_TYPES
from backend.config import API_YALM


router = InferringRouter()


@cbv(router)
class TextApp(BaseAppAuth):
    @classmethod
    async def get_template_id(cls, item_id):
        return await cls.get_one_object(QueryTemplateDB.select().where(QueryTemplateDB.id == item_id))

    @classmethod
    async def get_query_id(cls, item_id):
        return await cls.get_one_object(QueryDB.select().where(QueryDB.id == item_id))

    @classmethod
    async def get_template_hash(cls, hash):
        return await cls.get_one_object(QueryTemplateDB.select().where(QueryTemplateDB.hash == hash))

    @staticmethod
    async def json_loads(content):
        return json.loads(content.decode('utf-8'))

    @staticmethod
    async def json_dumps(data):
        return json.dumps(data, sort_keys=False, ensure_ascii=False)

    @classmethod
    async def get_json_hash(cls, content):
        data = await cls.json_loads(content)
        sdata = await cls.json_dumps(data).encode()
        return sha256(sdata).hexdigest()

    @staticmethod
    async def get_template_rows(item_id):
        return await manager.execute(TemplateRowsDB.select().where(TemplateRowsDB.template_id == item_id))

    @router.get("/api/template/list", tags=["Template"])
    async def get_template_list(self):
        return await self.get_list(QueryTemplateDB)

    @router.get("/api/template/{item_id}", tags=["Template"])
    async def get_template_item(self, item_id: int):
        item_db = await self.get_template_id(item_id)
        res = await self.prepare(item_db)
        if item_db is not None:
            res.update(await item_db.dict)
        query_rows = await self.get_template_rows(item_id)
        res['items'] = [
            {'text': item.text, 'symbols': item.symbols, 'text_type': item.text_type} for item in query_rows
        ]
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

    @staticmethod
    async def text_generate_query(query: str, text_type: str):
        async with aiohttp.ClientSession(headers={'Content-Type': "application/json"}) as sess:
            qdata = await TextApp.json_dumps({'query': query, 'intro': TEXT_TYPES.index(text_type), 'filter': 1})
            async with sess.post(urljoin(API_YALM['ADRESS'], API_YALM['POINT']), data=qdata) as resp:
                resp_data = await resp.json()
                return resp_data['text']

    @classmethod
    async def text_generate_db(
        cls, item_id: int, name: Optional[str], text_full: str, text_next: str, liner: str, text_type: str
    ):
        obj_query = await cls.get_query_id(item_id)
        if obj_query is None:
            res_query = await QueryDB.update_or_create({'name': name, 'text': text_full}, ret={"success": True})
        else:
            res_query = await QueryDB.update_or_create({'text': text_full}, obj_query, ret={"success": True})
            his = TextHistory(query_id=item_id, next=text_next, liner=liner, text_type=text_type, prod=False)
            res_his = await TextHistoryDB.update_or_create(his, ret={"success": True})

    @classmethod
    async def text_generate_update(
        cls, item_id: int, text_sum: str, text_next: Optional[str], liner: str, text_type: str
    ):
        next_gen = await cls.text_generate_query(text_sum, text_type)
        if next_gen is None:
            return {"success": False}
        text_full = f"{text_sum} {next_gen}"
        await cls.text_generate_db(item_id, None, text_full, "", liner, text_type)
        return {"success": True, "text": text_sum, "next": next_gen}

    @router.get("/api/text/next/{item_id}", tags=["Text"])
    async def get_text_next(
        self, item_id: int, text: str = "", text_next: str = "", liner: str = "", text_type: str = 'No style'
    ):
        text_sum = f"{text} {text_next} {liner}"
        return await self.text_generate_update(item_id, text_sum, text_next, liner, text_type)

    @router.get("/api/text/update/{item_id}", tags=["Text"])
    async def get_text_update(self, item_id: int, text: str = "", liner: str = "", text_type: str = 'No style'):
        return await self.text_generate_update(item_id, text, None, liner, text_type)

    @router.get("/api/text/finish/{item_id}", tags=["Text"])
    async def get_text_finish(self, item_id: int, text: str = "", text_next: str = "", liner: str = ""):
        text_full = f"{text} {text_next} {liner}"
        await self.text_generate_db(item_id, None, text_full, text_next, liner, 'No style')
        return {"success": True, "text": text_full}

    @router.get("/api/text/generate/{temp_id}", tags=["Text"])
    async def get_text_generate(self, temp_id: int, name: str = ""):
        temp = await self.get_template_id(temp_id)
        item = TextQuery(name=name if name else temp['name'], template_id=temp_id)
        item_db = await QueryDB.update_or_create(item)
        item_id = item_db['id']
        query_rows = await self.get_template_rows(temp_id)
        text_sum = ""
        text_next = ""
        for row in query_rows:
            text_sum = " ".join([text_sum.rstrip(), row.text])
            text_next_acc = ""
            while len(text_next_acc) < row.symbols:
                res = await self.text_generate_update(item_id, text_sum, text_next, row.text, row.text_type)
                text_next = res['next']
                text_next_acc = " ".join([text_next_acc.rstrip(), text_next])
                text_sum = " ".join([text_sum.rstrip(), text_next])
        return await QueryDB.update_or_create({'text': text_sum}, item_db, ret={"success": True})


app.include_router(router)
