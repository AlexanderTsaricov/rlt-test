# bot.py
import time
import requests
import os
from dotenv import load_dotenv
from LLMApi.LlmApiController import LlmApiController
import json
import re
from db.Database import Database


def extract_json(text: str):
    match = re.search(r"{.*}", text, re.DOTALL)
    if not match:
        return None

    json_str = match.group(0)
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        return None


# Загружаем переменные из .env
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TOKEN:
    raise ValueError("Не найден TELEGRAM_TOKEN в .env")
API_KEY = os.getenv("GROK_API_KEY")
if not API_KEY:
    raise ValueError("Не найден GOOGLE_API_AI_KEY в .env")

API_URL = f"https://api.telegram.org/bot{TOKEN}"
llm = LlmApiController(API_KEY)
offset = None  # для отслеживания новых сообщений


def get_updates():
    global offset
    params = {"timeout": 100, "offset": offset}
    resp = requests.get(f"{API_URL}/getUpdates", params=params)
    resp.raise_for_status()
    return resp.json()["result"]


def send_message(chat_id, text):
    requests.post(f"{API_URL}/sendMessage", json={"chat_id": chat_id, "text": text})


print("Бот запущен (polling)...")

while True:
    try:
        updates = get_updates()
        for update in updates:
            offset = update["update_id"] + 1  # чтобы не получать это сообщение снова
            if "message" in update and "text" in update["message"]:
                chat_id = update["message"]["chat"]["id"]
                text = update["message"]["text"]

                print(f"Получено сообщение: {text}")
                prompt = """
                Ты — модель, которая переводит запросы пользователей к базе данных в JSON-структуру requestParams.

                ВАЖНО:
                В каждом ответе обязательно должен быть указан метод работы с БД:
                - "getFromTable"
                или
                - "getAggregate"

                Формат ответа ДОЛЖЕН быть строго JSON, без текста вне JSON.

                ФОРМАТ ДЛЯ ПРОСТЫХ SELECT (getFromTable):

                {
                "method": "getFromTable",
                "tableName": "<имя таблицы>",
                "selectOperator": "<оператор сравнения>",
                "valueName": "<имя столбца>",
                "value": <значение>
                }

                ФОРМАТ ДЛЯ АГРЕГАТОВ (getAggregate):

                {
                "method": "getAggregate",
                "tableName": "<имя таблицы>",
                "aggregate": "<COUNT|SUM|AVG|MIN|MAX>",
                "columnName": "<имя колонки или *>",
                "valueName": "<имя поля условия или null>",
                "selectOperator": "<оператор или null>",
                "value": <значение или null>
                }

                Разрешённые операторы сравнения:

                =, >, <, >=, <=


                =========================
                Доступные таблицы:
                =========================

                TABLE snapshots:
                - id (varchar)
                - video_id (varchar)
                - views_count (INTEGER)
                - likes_count (INTEGER)
                - reports_count (INTEGER)
                - comments_count (INTEGER)
                - delta_views_count (INTEGER)
                - delta_likes_count (INTEGER)
                - delta_reports_count (INTEGER)
                - delta_comments_count (INTEGER)
                - created_at (timestamp)
                - updated_at (timestamp)

                TABLE films:
                - id (INTEGER)
                - external_id (varchar)
                - video_id (varchar)
                - video_created_at (timestamp)
                - views_count (INTEGER)
                - likes_count (INTEGER)
                - reports_count (INTEGER)
                - comments_count (INTEGER)
                - creator_id (varchar)
                - created_at (timestamp)
                - updated_at (timestamp)
                - snapshots (TEXT)


                =========================
                Примеры:
                =========================

                Пользователь говорит:
                "Найди фильм где id = 5"

                Ответ:
                {
                "method": "getFromTable",
                "tableName": "films",
                "selectOperator": "=",
                "valueName": "id",
                "value": 5
                }

                Пользователь говорит:
                "Сколько фильмов существует?"

                Ответ:
                {
                "method": "getAggregate",
                "tableName": "films",
                "aggregate": "COUNT",
                "columnName": "id",
                "valueName": null,
                "selectOperator": null,
                "value": null
                }


                Запрос пользователя:
                """
                prompt += text
                response = llm.send(prompt) or "Нет ответа от AI"
                print(response)
                parsed = extract_json(response)

                if parsed is None:
                    send_message(chat_id, response)
                    continue

                db = Database("db/storage.sqlite")

                method = parsed.get("method")

                if method == "getFromTable":
                    table = parsed.get("tableName")
                    operator = parsed.get("selectOperator")
                    valueName = parsed.get("valueName")
                    value = parsed.get("value")

                    rows = db.getFromTable(
                        tableName=table,
                        selectOperator=operator,
                        valueName=valueName,
                        value=value,
                    )

                    # Приводим SELECT к строке
                    answer = str(rows)

                elif method == "getAggregate":
                    table = parsed.get("tableName")
                    aggregate = parsed.get("aggregate")
                    columnName = parsed.get("columnName")
                    valueName = parsed.get("valueName")

                    # здесь преобразуем selectOperator → operator
                    operator = parsed.get("selectOperator")
                    value = parsed.get("value")

                    result = db.getAggregate(
                        tableName=table,
                        aggregate=aggregate,
                        columnName=columnName,
                        valueName=valueName,
                        operator=operator,
                        value=value,
                    )

                    answer = str(result)

                else:
                    answer = "Ошибка: неизвестный метод."

                print("Ответ базы данных: " + answer)
                
                

                send_message(chat_id, answer)
    except Exception as e:
        print("Ошибка:", e)
    time.sleep(1)  # проверяем новые сообщения каждую секунду
