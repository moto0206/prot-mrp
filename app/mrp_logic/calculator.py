import pandas as pd


def run_mrp_calculation(demand_df, bom_df, inventory_df):
    """
    MRP計算を実行し、発注が必要な部品のリストを返す関数

    Args:
        demand_df (pd.DataFrame): 需要計画データ
        bom_df (pd.DataFrame): 部品表データ
        inventory_df (pd.DataFrame): 在庫データ

    Returns:
        pd.DataFrame: 正味所要量（不足分）のデータフレーム
    """
    inventory_df = inventory_df.set_index("item_id")
    gross_requirements = {}

    print("--- 1. 総所要量の計算 (BOM展開) ---")
    # 需要計画から製品ごとに必要な部品の総量を計算
    for _, demand_row in demand_df.iterrows():
        product_id = demand_row["product_id"]
        quantity = demand_row["quantity"]

        required_parts = bom_df[bom_df["parent_id"] == product_id]

        for _, part_row in required_parts.iterrows():
            child_id = part_row["child_id"]
            qty_per_parent = part_row["quantity_per_parent"]

            total_required = quantity * qty_per_parent
            gross_requirements[child_id] = (
                gross_requirements.get(child_id, 0) + total_required
            )

    print(pd.Series(gross_requirements, name="総所要量"))
    print("\n")

    print("--- 2. 正味所要量の計算 ---")
    net_requirements = {}
    # 部品ごとに総所要量と在庫を引き算
    for part_id, gross_qty in gross_requirements.items():
        current_stock = (
            inventory_df.loc[part_id, "stock_quantity"]
            if part_id in inventory_df.index
            else 0
        )

        net_qty = gross_qty - current_stock

        if net_qty > 0:
            net_requirements[part_id] = {
                "gross_requirement": gross_qty,
                "current_stock": current_stock,
                "net_requirement_shortage": net_qty,
            }

    if not net_requirements:
        print("すべての部品の在庫は充足しています。")
        return pd.DataFrame()

    return pd.DataFrame.from_dict(net_requirements, orient="index")
