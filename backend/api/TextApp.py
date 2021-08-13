from typing import Optional
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from fastapi import Depends, UploadFile, File, Response
from hashlib import sha256
import json
from os.path import splitext
from urllib.parse import urljoin
import aiohttp
from datetime import timedelta
import time

from backend.app import app
from backend.models.template_query import QueryTemplate, TemplateRows, QueryTemplateDB, TemplateRowsDB
from backend.models.text_query import TextQuery, QueryDB
from backend.models.text_history import TextHistory, TextHistoryDB
from backend.api.base import BaseAppAuth
from backend.db.base import manager
from backend.db.types import TEXT_TYPES, ModelTextTypes
from backend.config import API_YALM
from backend.library.transform_text import REPL_LIST, STRIP_CHARS, replacer
from backend.api.user import set_response_headers


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
        sdata = (await cls.json_dumps(data)).encode()
        return sha256(sdata).hexdigest()

    @staticmethod
    async def get_template_rows(item_id):
        return await manager.execute(TemplateRowsDB.select().where(TemplateRowsDB.template_id == item_id))

    @staticmethod
    async def text_generate_query(query: str, text_type: Optional[str] = None):
        if text_type is None:
            text_type = 'No style'
        async with aiohttp.ClientSession(headers={'Content-Type': "application/json"}) as sess:
            qdata = await TextApp.json_dumps({'query': query, 'intro': TEXT_TYPES.index(text_type), 'filter': 1})
            async with sess.post(urljoin(API_YALM['ADRESS'], API_YALM['POINT']), data=qdata) as resp:
                resp_data = await resp.json()
                return resp_data['text']

    @classmethod
    async def text_generate_db(
        cls,
        item_id: int,
        name: Optional[str],
        text_full: Optional[str],
        text_next: Optional[str],
        liner: Optional[str],
        text_type: Optional[str],
        ret: Optional[dict] = None,
    ):
        if text_next is None:
            text_next = ""
        if liner is None:
            liner = ""
        if text_type is None:
            text_type = 'No style'
        if ret is None:
            ret = {"success": True}

        obj_query = await cls.get_query_id(item_id)

        if obj_query is None:
            res_query = await QueryDB.update_or_create({'name': name, 'text': text_full}, ret={"success": True})
        else:
            res_query = await QueryDB.update_or_create({'text': text_full}, obj_query, ret=ret)
            his = TextHistory(query_id=item_id, next=text_next, liner=liner, text_type=text_type, prod=False)
            res_his = await TextHistoryDB.update_or_create(his, ret={"success": True})
        return res_query

    @classmethod
    async def text_generate_update(
        cls, item_id: int, text_sum: str, text_next: Optional[str], liner: str, text_type: str
    ):
        next_gen = await cls.text_generate_query(text_sum, text_type)
        if next_gen is None:
            return {"success": False}
        text_full = await cls.joinner([text_sum, next_gen])
        await cls.text_generate_db(item_id, None, text_full, text_next, liner, text_type)
        return {"success": True, "text": text_sum, "next": next_gen}

    @staticmethod
    async def joinner(slst: list):
        text = " ".join([item.lstrip(" ") for item in slst]).strip(" ")
        text = replacer(text, REPL_LIST, STRIP_CHARS)
        return text

    @classmethod
    async def response_header(cls, response: Response):
        await set_response_headers(response)

    @router.get("/api/template/list", tags=["Template"])
    async def get_template_list(self, response: Response):
        await self.response_header(response)
        return await self.get_list(QueryTemplateDB)

    @router.get("/api/template/{item_id}", tags=["Template"])
    async def get_template_item(self, response: Response, item_id: int):
        await self.response_header(response)
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
        response: Response,
        name: Optional[str] = "",
        data: UploadFile = File(..., media_type='application/octet-stream'),
    ):
        await self.response_header(response)
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
    async def get_text_new(self, response: Response, name: str):
        await self.response_header(response)
        item = TextQuery(name=name)
        return await QueryDB.update_or_create(item, ret={"success": True})

    @router.get("/api/text/next/{item_id}", tags=["Text"])
    async def get_text_next(
        self,
        response: Response,
        item_id: int,
        text: str = "",
        text_next: str = "",
        liner: str = "",
        text_type: ModelTextTypes = 'No style',
    ):
        await self.response_header(response)
        start_time = time.monotonic()
        text_sum = await self.joinner([text, text_next, liner])
        res = await self.text_generate_update(item_id, text_sum, text_next, liner, text_type)
        res['time_query'] = timedelta(seconds=time.monotonic() - start_time)
        return res

    @router.get("/api/text/update/{item_id}", tags=["Text"])
    async def get_text_update(
        self,
        response: Response,
        item_id: int,
        text: str = "",
        text_next: str = "",
        liner: str = "",
        text_type: ModelTextTypes = 'No style',
    ):
        await self.response_header(response)
        start_time = time.monotonic()
        res = await self.text_generate_update(item_id, text, text_next, liner, text_type)
        res['time_query'] = timedelta(seconds=time.monotonic() - start_time)
        return res

    @router.get("/api/text/finish/{item_id}", tags=["Text"])
    async def get_text_finish(
        self, response: Response, item_id: int, text: str = "", text_next: str = "", liner: str = ""
    ):
        await self.response_header(response)
        start_time = time.monotonic()
        text_full = await self.joinner([text, text_next, liner])
        await self.text_generate_db(item_id, None, text_full, text_next, liner, 'No style')
        return {"success": True, "text": text_full, "time_query": timedelta(seconds=time.monotonic() - start_time)}

    @router.get("/api/text/generate/{temp_id}", tags=["Text"])
    async def get_text_generate(self, response: Response, temp_id: int, name: str = ""):
        await self.response_header(response)
        start_time = time.monotonic()
        temp = await self.get_template_id(temp_id)
        item = TextQuery(name=name if name else temp.name, template_id=temp_id)
        item_db_dict, item_db = await QueryDB.update_or_create(item, return_obj_db=True)
        item_id = item_db_dict['id']
        query_rows = await self.get_template_rows(temp_id)
        text_sum = ""
        text_next = ""
        text_type = None
        for row in query_rows:
            text_sum = await self.joinner([text_sum, row.text])
            text_next_acc = ""
            while len(text_next_acc) < row.symbols:
                res = await self.text_generate_update(item_id, text_sum, text_next, row.text, text_type)
                text_next, text_type = (res['next'], row.text_type)
                text_next_acc = await self.joinner([text_next_acc, text_next])
                text_sum = await self.joinner([text_sum, text_next])
        res = await self.text_generate_db(item_id, None, text_sum, text_next, None, text_type, ret={"success": True})
        res['time_query'] = timedelta(seconds=time.monotonic() - start_time)
        return res


app.include_router(router)
