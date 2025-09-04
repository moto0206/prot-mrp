import os
import pandas as pd
from mrp_logic.calculator import run_mrp_calculation

# --- データ読み込み ---
DATA_DIR = "app/data"
try:
    demand_df = pd.read_csv(os.path.join(DATA_DIR, "demand.csv"))
    bom_df = pd.read_csv(os.path.join(DATA_DIR, "bom.csv"))
    inventory_df = pd.read_csv(os.path.join(DATA_DIR, "inventory.csv"))
    print("--- CSVファイルの読み込み完了 ---")
    print("需要計画:")
    print(demand_df.head())
    print("\n")

except FileNotFoundError as e:
    print(f"エラー: {e}")
    print("データファイルが app/data/ フォルダに存在するか確認してください。")
    exit()


# --- MRP計算の実行 ---
print("--- MRP計算を開始します ---")
order_list_df = run_mrp_calculation(demand_df, bom_df, inventory_df)
print("\n")


# --- 結果表示 ---
print("--- 最終結果：発注リスト ---")
if order_list_df.empty:
    print("発注が必要な部品はありません。")
else:
    print(order_list_df)
