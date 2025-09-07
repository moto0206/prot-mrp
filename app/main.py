import os
import pandas as pd
from fastapi import FastAPI
from mrp_logic.calculator import run_mrp_calculation
import sqlalchemy

# ★★★★★ デバッグ用：DB接続情報を環境変数から取得 ★★★★★
db_url = os.environ.get("DATABASE_URL")
if not db_url:
    raise ValueError("DATABASE_URL environment variable not set")

try:
    engine = sqlalchemy.create_engine(db_url)
    print("✅ データベースエンジン作成成功")
except Exception as e:
    print(f"❌ データベースエンジン作成失敗: {e}")
    # 失敗した場合はここで処理を中断させる
    raise

app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "MRP Calculation API is running"}


@app.get("/run-mrp")
def execute_mrp():
    try:
        with engine.connect() as connection:
            print("\n--- デバッグ開始：DBからDataFrameへの読み込み ---")

            # ★★★★★ デバッグ①：BOMテーブルの読み込み ★★★★★
            bom_df = pd.read_sql("SELECT * FROM bom", connection)
            print(f"1. BOM DFの形状: {bom_df.shape}")  # (4, 4)のはず
            # print("BOM DFの内容:\n", bom_df.head()) # 必要ならコメントアウトを外す

            # ★★★★★ デバッグ②：INVENTORYテーブルの読み込み ★★★★★
            inventory_df = pd.read_sql("SELECT * FROM inventory", connection)
            print(f"2. INVENTORY DFの形状: {inventory_df.shape}")  # (3, 2)のはず
            # print("INVENTORY DFの内容:\n", inventory_df.head())

            # ★★★★★ デバッグ③：DEMANDテーブルの読み込み ★★★★★
            demand_df = pd.read_sql("SELECT * FROM demand", connection)
            print(f"3. DEMAND DFの形状: {demand_df.shape}")  # (2, 3)のはず
            # print("DEMAND DFの内容:\n", demand_df.head())

            print("--- デバッグ終了：読み込み完了、計算処理へ --- \n")

        # MRP計算を実行
        order_list_df = run_mrp_calculation(demand_df, bom_df, inventory_df)

        if order_list_df.empty:
            return {"message": "No parts need to be ordered."}
        else:
            return order_list_df.to_dict(orient="index")

    except Exception as e:
        print(f"❌ MRP計算中にエラーが発生: {e}")
        return {"error": f"An error occurred: {e}"}
