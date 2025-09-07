import os
import pandas as pd
from fastapi import FastAPI
from mrp_logic.calculator import run_mrp_calculation
import sqlalchemy
import boto3  # 👈 boto3をインポート
import json  # 👈 jsonをインポート


# --- Secrets Managerからパスワードを取得する関数 ---
def get_secret(secret_name):
    region_name = (
        "ap-northeast-1"  # 👈 Secrets Managerがあるリージョンに合わせてください
    )

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(service_name="secretsmanager", region_name=region_name)

    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    except Exception as e:
        print(f"❌ Secrets Managerからのシークレット取得に失敗: {e}")
        raise e

    # Secrets Managerは通常、JSON形式で値を返す
    secret = get_secret_value_response["SecretString"]
    return json.loads(secret)


# --- アプリケーションのメイン処理 ---
try:
    # ★★★★★ ここからが修正箇所 ★★★★★
    # 1. ハードコードせず、環境変数からシークレットのARNを取得
    SECRET_ARN = os.environ.get("SECRET_ARN")
    if not SECRET_ARN:
        raise ValueError("SECRET_ARN environment variable not set")

    secrets = get_secret(SECRET_ARN)

    # 2. Secrets Managerから取得した情報でデータベースURLを組み立てる
    db_username = secrets["username"]
    db_password = secrets["password"]
    db_host = secrets["host"]  # エンドポイント
    db_port = secrets["port"]
    db_name = secrets["dbname"]

    DATABASE_URL = (
        f"postgresql://{db_username}:{db_password}@{db_host}:{db_port}/{db_name}"
    )

    print("✅ Secrets ManagerからDB情報を取得し、接続URLを生成しました")

    engine = sqlalchemy.create_engine(DATABASE_URL)

except Exception as e:
    print("❌ データベースエンジンの作成中にエラーが発生しました。")
    raise

app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "MRP Calculation API is running"}


# /run-mrp 以下の処理は変更なし
@app.get("/run-mrp")
def execute_mrp():
    try:
        with engine.connect() as connection:
            bom_df = pd.read_sql("SELECT * FROM bom", connection)
            inventory_df = pd.read_sql("SELECT * FROM inventory", connection)
            demand_df = pd.read_sql("SELECT * FROM demand", connection)

        order_list_df = run_mrp_calculation(demand_df, bom_df, inventory_df)

        if order_list_df.empty:
            return {"message": "No parts need to be ordered."}
        else:
            return order_list_df.to_dict(orient="index")

    except Exception as e:
        return {"error": f"An error occurred: {e}"}
