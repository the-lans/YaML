# Генератор текста

## Установка

Последовательность действий для установки:

- Для создания виртуальной среды могут использоваться *conda* или *virtualenv*.

- Создайте виртуальное окружение `conda create -n venv`

- Активируйте виртуальное окружение `conda activate venv`

- Установите пакеты `pip install -r requirements.txt`

- Перейдите в папку с проектом 

- Создайте базу данных *\<database\>*

- Выполните миграцию `python pw_migrate.py migrate --database=postgresql://postgres@<host_postgres>:5432/<database>`

  *\<host_postgres\>* - рабочий хост базы данных

  *\<database\>* - имя базы данных

- Настройте конфигурационный файл *conf.yaml*

- Запустите API `uvicorn main:app --reload`

    

## Отладка

Запустите на отладку файл `main.py`

Проверьте API на локальной машине: http://127.0.0.1:8000/

Доступ к REST API Swagger: http://127.0.0.1:8000/docs#/

Доступ к REST API Redoc: http://127.0.0.1:8000/redoc



## **Конечные точки**

| №    | Конечная точка         | Тип  | Параметры                                        | Response             | Описание                              |
| ---- | ---------------------- | ---- | ------------------------------------------------ | -------------------- | ------------------------------------- |
| 1    | api/text/new           | GET  | name: str                                        | QueryDB              | Новый запрос (статья)                 |
| 2    | api/text/next/{id}     | GET  | text: str, next: str, liner: str, text_type: str | text: str, next: str | Генерация следующего куска текста     |
| 3    | api/text/update/{id}   | GET  | text: str, liner: str, text_type: str            | text: str, next: str | Обновление существующего куска текста |
| 4    | api/text/finish/{id}   | GET  | text: str, next: str, liner: str                 | text: str            | Завершение запроса                    |
| 5    | api/template/new       | POST | name: str, file/json                             | QueryTemplateDB      | Добавление шаблона                    |
| 6    | api/template/list      | GET  |                                                  | QueryTemplateDB      | Список шаблонов                       |
| 7    | api/template/{id}      | GET  |                                                  | QueryTemplateDB      | Получение шаблона                     |
| 8    | api/text/generate/{id} | GET  |                                                  | QueryDB              | Генерация текста по шаблону           |
|      |                        |      |                                                  |                      |                                       |

  

## **Заголовки**

| Key           | Value            | Описание          |
| ------------- | ---------------- | ----------------- |
| Authorization | Bearer …         | Токен авторизации |
| Content-Type  | application/json | Тип контента      |
|               |                  |                   |

  

## **Точки пересылки запросов**

| №    | Конечная точка                                | Тип  | Параметры                                  | Response                                                    |
| ---- | --------------------------------------------- | ---- | ------------------------------------------ | ----------------------------------------------------------- |
| 1    | https://zeapi.yandex.net/  lab/api/yalm/text3 | POST | query:  str,   intro:  int,   filter:  int | bad_query:  int,   error:  int,   query:  str,   text:  str |
|      |                                               |      |                                            |                                                             |

  

## База данных

### template_query	

Model: QueryTemplateDB

| Поле    | Тип      | Описание               |
| ------- | -------- | ---------------------- |
| id      | int      | Идентификатор шаблона  |
| created | datetime | Дата создания          |
| name    | str      | Название шаблона       |
| hash    | str      | Хеш загружаемого файла |
|         |          |                        |



### template_rows

Model: TemplateRowsDB

| Поле        | Тип  | Описание                                 |
| ----------- | ---- | ---------------------------------------- |
| id          | int  | Идентификатор записи                     |
| template_id | int  | Шаблон                                   |
| text        | str  | Автоподводка                             |
| symbols     | int  | Количество символов для генерации текста |
| text_type   | int  | Тип текста                               |
|             |      |                                          |



### text_query

Model: QueryDB

| Поле        | Тип      | Описание                |
| ----------- | -------- | ----------------------- |
| id          | int      | Идентификатор запроса   |
| created     | datetime | Дата создания           |
| template_id | int      | Шаблон для создания     |
| name        | str      | Имя конкретного запроса |
| text        | str      | Сгенерированный текст   |
|             |          |                         |



### text_history

Model: TextHistoryDB

| Поле      | Тип      | Описание                               |
| --------- | -------- | -------------------------------------- |
| id        | int      | Идентификатор записи                   |
| created   | datetime | Дата создания записи                   |
| query_id  | int      | Запрос                                 |
| next      | str      | Сгенерированный текст на текущем шаге  |
| liner     | str      | Подводка                               |
| prod      | bool     | Текст используется в итоговом варианте |
| text_type | int      | Тип текста                             |
|           |          |                                        |

