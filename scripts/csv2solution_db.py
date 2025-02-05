"""
After running this script, the embedded database file will be automatically created in the default location (./db/sqlite.db).
At the same time, the csv file is parsed and written to the solution table.

"""
# !! This script does not have the ability to merge data in solution table

import json

import pandas as pd


def csv2db(csv_path: str, sqlite_db_path: str):
    source_data = pd.read_csv(csv_path)
    source_data = source_data[["name", "os", "arch", "procedure", "url"]]

    duplicated_data = source_data.drop_duplicates()
    duplicated_data["os"].fillna("Universal", inplace=True)
    duplicated_data["arch"].fillna("Universal", inplace=True)

    def f1(row):
        data = {"name": row["name"], "git_url": row["url"]}

        return json.dumps(data, ensure_ascii=False)

    def f2(row):
        data = [
            {
                "env_info": {"platform": row["os"], "arch": row["arch"]},
                "procedure": row["procedure"],
            }
        ]

        return json.dumps(data, ensure_ascii=False)

    duplicated_data["project_meta"] = duplicated_data.apply(f1, axis=1)
    duplicated_data["guides"] = duplicated_data.apply(f2, axis=1)
    duplicated_data.drop(
        columns=["os", "arch", "procedure", "url", "name"], inplace=True
    )

    import sqlite3

    conn = sqlite3.connect(sqlite_db_path)
    table_name = "solution"
    conn.execute(f"""
                CREATE TABLE IF NOT EXISTS {table_name} (
                    project_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guides TEXT NOT NULL,
                    project_meta TEXT NOT NULL)""")

    conn.commit()
    duplicated_data.to_sql("solution", conn, if_exists="append", index=False)
    conn.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="csv from feishu to sqlite as solution knowledge base"
    )

    # 添加可选参数
    parser.add_argument("csvpath")

    parser.add_argument("--sqlite-db-path", default="./db/sqlite.db")

    # 解析参数
    args = parser.parse_args()
    csv2db(csv_path=args.csvpath, sqlite_db_path=args.sqlite_db_path)
