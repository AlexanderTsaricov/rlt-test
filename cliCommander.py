from db.Database import Database
from db.Column import Column
import argparse
import json
from LLMApi.LlmApiController import LlmApiController

def llmTest():
    ai = LlmApiController()
    question = 'это тест. Ответь "да", если получил'
    answer = ai.send(question)

    if answer:
        # проверяем, есть ли в ответе слово "да" (игнорируем регистр)
        print("Ответ: " + answer.lower())
        if "да" in answer.lower():
            print("Тест пройден")
        else:
            print("Тест не пройден, ответ:", answer)
    else:
        print("Нет ответа от AI")

def main():
    db = Database("db/storage.sqlite")

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "command",
        choices=["add", "create", "test"],
        help="add - Добавить данные в БД, create - создать табилцу",
    )
    parser.add_argument("--path", type=str, help="Путь к файлу")

    args = parser.parse_args()

    if args.command == "add":
        print("start: add " + args.path)

        with open(args.path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
            for video in data["videos"]:

                snapshot_db_ids = []

                # SNAPSHOTS
                for snap in video.get("snapshots", []):

                    db.insertIntoTable(
                        "snapshots",
                        [
                            Column("id", value=snap["id"]),
                            Column("video_id", value=snap["video_id"]),
                            Column("views_count", value=snap["views_count"]),
                            Column("likes_count", value=snap["likes_count"]),
                            Column("reports_count", value=snap["reports_count"]),
                            Column("comments_count", value=snap["comments_count"]),
                            Column("delta_views_count", value=snap["delta_views_count"]),
                            Column("delta_likes_count", value=snap["delta_likes_count"]),
                            Column("delta_reports_count", value=snap["delta_reports_count"]),
                            Column("delta_comments_count", value=snap["delta_comments_count"]),
                            Column("created_at", value=snap["created_at"]),
                            Column("updated_at", value=snap["updated_at"]),
                        ],
                    )

                    snapshot_db_ids.append(snap["id"])  # PK snapshots

                # FILM
                db.insertIntoTable(
                    "films",
                    [
                        Column("video_id", value=video["id"]),
                        Column("video_created_at", value=video["video_created_at"]),
                        Column("views_count", value=video["views_count"]),
                        Column("likes_count", value=video["likes_count"]),
                        Column("reports_count", value=video["reports_count"]),
                        Column("comments_count", value=video["comments_count"]),
                        Column("creator_id", value=video["creator_id"]),
                        Column("created_at", value=video["created_at"]),
                        Column("updated_at", value=video["updated_at"]),
                        Column("snapshots", value=json.dumps(snapshot_db_ids)),
                    ],
                )
                
        print("add end")

            
        

    if args.command == "create":
        print("start create")

        db.createTable(
            "films",
            [
                Column("id", "integer primary key AUTOINCREMENT"),
                Column("external_id", "varchar"),
                Column("video_id", "varchar"),
                Column("video_created_at", "timestamp"),
                Column("views_count", "integer"),
                Column("likes_count", "integer"),
                Column("reports_count", "integer"),
                Column("comments_count", "integer"),
                Column("creator_id", "varchar"),
                Column("created_at", "timestamp"),
                Column("updated_at", "timestamp"),
                Column("snapshots", "TEXT"),
            ],
        )

        db.createTable(
            "snapshots",
            [
                Column("id", "varchar primary key"),
                Column("video_id", "varchar"),
                Column("views_count", "integer"),
                Column("likes_count", "integer"),
                Column("reports_count", "integer"),
                Column("comments_count", "integer"),
                Column("delta_views_count", "integer"),
                Column("delta_likes_count", "integer"),
                Column("delta_reports_count", "integer"),
                Column("delta_comments_count", "integer"),
                Column("created_at", "timestamp"),
                Column("updated_at", "timestamp"),
            ],
        )

        
        print("end create")
        
    if args.command == "test":
        llmTest()



if __name__ == "__main__":
    main()
