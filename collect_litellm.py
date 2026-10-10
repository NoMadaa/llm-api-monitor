import requests
import pandas as pd
import json
from pathlib import Path

URL = "https://cdn.jsdelivr.net/gh/BerriAI/litellm@main/model_prices_and_context_window.json"

def fetch_data():
    resp = requests.get(URL, timeout=30)
    resp.raise_for_status()
    return resp.json()

def parse_data(raw):
    rows = []
    for model_name, info in raw.items():
        if not isinstance(info, dict):
            continue
        rows.append({
            "model_name": model_name,
            "input_cost_per_token": info.get("input_cost_per_token"),
            "output_cost_per_token": info.get("output_cost_per_token"),
            "max_tokens": info.get("max_tokens"),
            "litellm_provider": info.get("litellm_provider"),
            "mode": info.get("mode"),
        })
    return pd.DataFrame(rows)

def main():
    print("Fetching LiteLLM pricing data...")
    raw = fetch_data()
    df = parse_data(raw)
    # 换算成 元/百万Token 的列先不急着做，第一天只保存原始数据
    Path("data").mkdir(exist_ok=True)
    df.to_csv("data/litellm_pricing_raw.csv", index=False)
    print(f"Saved {len(df)} models to data/litellm_pricing_raw.csv")

if __name__ == "__main__":
    main()