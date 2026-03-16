"""
企查查开放平台 API 客户端 — 融资信息核查（ApiCode 950）

使用前请在 https://openapi.qcc.com 注册并开通「融资信息核查」接口，
在控制台获取 AppKey 与 SecretKey，写入 .env：
  QCC_API_KEY=你的AppKey
  QCC_SECRET_KEY=你的SecretKey

认证方式（开放平台通用）：
  Token = MD5(Key + Timespan + SecretKey)，32 位大写
  Timespan = 当前 Unix 时间戳（秒）
 请求头：Token, Timespan
"""
import hashlib
import time
from typing import List, Dict, Any, Optional

import requests

# 融资信息核查 ApiCode 950，官方路径如下
QCC_FINANCING_URL = "https://api.qichacha.com/CompanyFinancingSearch/GetList"


def make_token(key: str, secret: str) -> tuple:
    """生成 Token 与 Timespan。返回 (Token, Timespan)。"""
    timespan = str(int(time.time()))
    raw = f"{key}{timespan}{secret}"
    token = hashlib.md5(raw.encode()).hexdigest().upper()
    return token, timespan


def fetch_financing(
    key: str,
    secret: str,
    search_key: str = "VR A轮",
    page_index: int = 1,
    page_size: int = 10,
) -> List[Dict[str, Any]]:
    """
    调用企查查「融资信息核查」接口（ApiCode 950），按关键字查询融资信息。

    官方文档：https://openapi.qcc.com/dataApi/950
    接口地址：GET https://api.qichacha.com/CompanyFinancingSearch/GetList

    :param key: 开放平台 AppKey
    :param secret: 开放平台 SecretKey
    :param search_key: 搜索关键词（企业名称、统一社会信用代码等）
    :param page_index: 页码，默认 1
    :param page_size: 每页条数，默认 10，最大 20
    :return: 标准化后的融资记录列表
    """
    token, timespan = make_token(key, secret)
    headers = {"Token": token, "Timespan": timespan}
    params = {
        "key": key,
        "searchKey": search_key,
        "pageIndex": page_index,
        "pageSize": min(20, max(1, page_size)),
    }

    try:
        resp = requests.get(QCC_FINANCING_URL, params=params, headers=headers, timeout=15)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        raise RuntimeError(f"企查查 API 请求失败: {e}") from e

    status = data.get("Status") or data.get("status") or data.get("code")
    if status and str(status) != "200":
        msg = data.get("Message") or data.get("message") or data.get("msg") or str(data)
        raise RuntimeError(f"企查查 API 返回错误: {msg}")

    # 官方返回：VerifyResult, Data（List，元素为 Date/ProductName/Round/Amount/Valuation/Investment/NewsUrl）
    data_list = data.get("Data") or data.get("data") or []
    if not isinstance(data_list, list):
        data_list = []

    records: List[Dict[str, str]] = []
    for item in data_list:
        if not isinstance(item, dict):
            continue
        company = item.get("ProductName") or item.get("productName") or ""
        round_ = item.get("Round") or item.get("round") or "未知"
        amount = item.get("Amount") or item.get("amount") or "未知"
        date_str = item.get("Date") or item.get("date") or "未知"
        investment = item.get("Investment") or item.get("investment") or ""
        news_url = item.get("NewsUrl") or item.get("newsUrl") or ""
        source = f"企查查 | 投资方: {investment}"
        if news_url:
            source += f" | {news_url}"
        records.append(
            {
                "公司名称": company or "未知",
                "轮次": str(round_),
                "融资金额": str(amount),
                "融资时间": str(date_str),
                "行业": "VR/AR/XR",
                "来源": source.strip(" |"),
            }
        )
    return records


def fetch_vr_financing_qcc(
    key: str,
    secret: str,
    keywords: Optional[List[str]] = None,
) -> List[Dict[str, str]]:
    """
    按多组关键字查询 VR/AR 相关融资，合并去重后返回。

    :param key: QCC_API_KEY
    :param secret: QCC_SECRET_KEY
    :param keywords: 搜索关键字列表，默认 ["VR", "虚拟现实", "XR AR"]
    :return: 统一格式的融资记录列表
    """
    keywords = keywords or ["VR", "虚拟现实", "XR AR"]
    seen: set = set()
    out: List[Dict[str, str]] = []
    for kw in keywords:
        try:
            records = fetch_financing(key, secret, search_key=kw, page_size=20)
        except Exception as e:
            print(f"企查查查询「{kw}」失败: {e}")
            continue
        for r in records:
            key_ = (r.get("公司名称"), r.get("轮次"), r.get("融资时间"))
            if key_ in seen:
                continue
            seen.add(key_)
            out.append(r)
    return out
