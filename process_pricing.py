import pandas as pd
from pathlib import Path

# ---------- 配置 ----------
RAW_PATH = Path("data/litellm_pricing_raw.csv")
OUT_PATH = Path("data/pricing_standardized.csv")
EXCHANGE_RATE = 7.2  # 美元兑人民币，固定值，后续可替换

# 关注的重点模型关键词（用于筛选）
TARGET_KEYWORDS = [
    "qwen", "deepseek", "glm", "kimi", "moonshot",
    "minimax", "ernie", "hy3", "hunyuan", "seed", "doubao",
    "gpt-6", "gpt-4", "claude", "gemini"
]

# SuperCLUE 2026年7月通用框架总分（手动整理，后续可改为爬虫）
CAPABILITY_SCORES = {
    "qwen3.8-max": 72.62,
    "deepseek-v4.1-flash": 71.81,
    "glm-5.3": 71.29,
    "kimi-k3": 70.68,
    "seed2.1-pro": 65.94,
    "hy3": 62.13,
    "minimax-m3": 56.90,
    "ernie-5.1": 54.56,
    "gpt-6-astra": None,   # 国外模型暂不填，可后续补充
    "claude-fable-5.1": None,
}

def load_raw():
    df = pd.read_csv(RAW_PATH)
    return df

def filter_models(df):
    """筛选重点模型，忽略 embedding、image 等非对话模型"""
    mask = df["model_name"].str.lower().str.contains(
        "|".join(TARGET_KEYWORDS), na=False
    )
    df = df[mask].copy()
    # 只保留对话模型（mode 为 chat 或 completion）
    if "mode" in df.columns:
        df = df[df["mode"].isin(["chat", "completion"])]
    return df

def convert_units(df):
    """美元/Token -> 元/百万Token"""
    df["input_price_cny"] = df["input_cost_per_token"] * 1_000_000 * EXCHANGE_RATE
    df["output_price_cny"] = df["output_cost_per_token"] * 1_000_000 * EXCHANGE_RATE
    # 保留两位小数
    df["input_price_cny"] = df["input_price_cny"].round(2)
    df["output_price_cny"] = df["output_price_cny"].round(2)
    return df

def normalize_name(name):
    """统一模型名：小写、去空格、替换特殊符号"""
    return (
        name.lower()
        .replace(" ", "-")
        .replace("_", "-")
        .replace(".", "-")
    )

def add_capability(df):
    """根据标准化名称匹配能力分数"""
    df["name_key"] = df["model_name"].apply(normalize_name)
    # 尝试模糊匹配：如果 name_key 包含 CAPABILITY_SCORES 的键
    def match_score(key):
        for cap_name, score in CAPABILITY_SCORES.items():
            if cap_name in key:
                return score
        return None
    df["capability_score"] = df["name_key"].apply(match_score)
    return df

def main():
    df = load_raw()
    print(f"原始数据: {len(df)} 行")
    df = filter_models(df)
    print(f"筛选后: {len(df)} 行")
    df = convert_units(df)
    df = add_capability(df)

    # 只保留需要的列
    cols = [
        "model_name", "litellm_provider",
        "input_price_cny", "output_price_cny",
        "max_tokens", "capability_score"
    ]
    df = df[[c for c in cols if c in df.columns]]

    # 去重：同一模型可能有多条记录，保留价格最低的
    df = df.sort_values("input_price_cny").drop_duplicates(
        subset=["model_name"], keep="first"
    )

    Path("data").mkdir(exist_ok=True)
    df.to_csv(OUT_PATH, index=False)
    print(f"标准化数据已保存: {OUT_PATH}，共 {len(df)} 行")
    print(df.head(10))

if __name__ == "__main__":
    main()