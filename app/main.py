import os
import pandas as pd
from fastapi import FastAPI

# この行にドットがないことを確認してください
from mrp_logic.calculator import run_mrp_calculation

app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "MRP Calculation API is running"}


@app.get("/run-mrp")
def execute_mrp():
    DATA_DIR = "data"
    try:
        demand_df = pd.read_csv(os.path.join(DATA_DIR, "demand.csv"))
        bom_df = pd.read_csv(os.path.join(DATA_DIR, "bom.csv"))
        inventory_df = pd.read_csv(os.path.join(DATA_DIR, "inventory.csv"))

        order_list_df = run_mrp_calculation(demand_df, bom_df, inventory_df)

        if order_list_df.empty:
            return {"message": "No parts need to be ordered."}
        else:
            return order_list_df.to_dict(orient="index")

    except FileNotFoundError as e:
        return {"error": f"Data file not found: {e}"}
    except Exception as e:
        return {"error": f"An error occurred: {e}"}
