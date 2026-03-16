"""
定时搜索国内 VR / A 轮融资情况，并整理成 Excel。

当前版本（便于测试）：
- 脚本一运行就立刻抓取一次并生成一份 Excel。
- 之后每分钟再抓取一次，并在控制台打印「距离下次抓取还有 X 秒」的倒计时。
- 每一份 Excel 的文件名精确到分钟，不会覆盖原文件。
- 所有 Excel 文件统一保存在脚本同级目录下的 `vr_reports/` 文件夹中。
- 与 LLM 联动：对抓取到的网页正文让 AI 做结构化抽取，再整理成统一格式写入 Excel。
"""
import datetime
import json
import time
from pathlib import Path
from typing import List, Dict, Any

import openpyxl
from openpyxl.utils import get_column_letter
import schedule
import requests
from bs4 import BeautifulSoup
from openai import OpenAI

from config import OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_MODEL, QCC_API_KEY, QCC_SECRET_KEY
from data_sources.qcc_client import fetch_vr_financing_qcc


SEARCH_CONFIGS = [
    # 更偏向新闻/信息站，而不是问答社区
    {"query": "site:36kr.com VR A轮 融资", "industry": "VR"},
    {"query": "site:36kr.com 虚拟现实 A轮 融资", "industry": "VR"},
    {"query": "site:36kr.com XR AR VR A轮 融资", "industry": "VR/AR/XR"},
    {"query": "site:36kr.com 元宇宙 A轮 融资", "industry": "VR/AR/XR"},
    # 兜底：不限定站点的通用查询（可能夹杂问答社区）
    {"query": "国内 VR 公司 A轮 融资", "industry": "VR"},
]


def _get_llm_client() -> OpenAI:
    kwargs: Dict[str, Any] = {"api_key": OPENAI_API_KEY}
    if OPENAI_BASE_URL:
        kwargs["base_url"] = OPENAI_BASE_URL
    return OpenAI(**kwargs)


def _search_bing(query: str, limit: int = 10) -> List[Dict[str, str]]:
    url = "https://www.bing.com/search"
    params = {"q": query}
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/123.0 Safari/537.36"
        )
    }

    try:
        resp = requests.get(url, params=params, headers=headers, timeout=10)
        resp.raise_for_status()
    except Exception as e:
        print(f"请求必应失败（{query}）: {e}")
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    results: List[Dict[str, str]] = []
    for li in soup.select("li.b_algo"):
        a = li.select_one("h2 a")
        if not a:
            continue
        title = a.get_text(strip=True)
        link = a.get("href", "")
        # 跳过容易 403 或文本价值较低的站点（如知乎问答页）
        if any(bad in link for bad in ["zhihu.com/question", "zhihu.com/topic"]):
            continue
        snippet_el = li.select_one(".b_caption p")
        snippet = snippet_el.get_text(strip=True) if snippet_el else ""
        results.append({"title": title, "link": link, "snippet": snippet})
        if len(results) >= limit:
            break
    return results


def _fetch_page_text(url: str) -> str:
    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/123.0 Safari/537.36"
            )
        }
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
    except Exception as e:
        print(f"获取网页失败：{url} - {e}")
        return ""

    soup = BeautifulSoup(resp.text, "html.parser")
    text = soup.get_text(separator="\n", strip=True)
    # 避免内容过长导致 token 爆炸，这里截断前 8000 字符
    return text[:8000]


def _extract_json_from_text(text: str) -> Any:
    """尽量从模型返回中提取 JSON（容错处理，引号、Markdown 包裹等）。"""
    text = text.strip()
    # 去掉 ```json ``` 包裹
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:].strip()
    # 找到第一个 '[' 或 '{'
    start_idx = len(text)
    for ch in ("[", "{"):
        i = text.find(ch)
        if i != -1:
            start_idx = min(start_idx, i)
    if start_idx == len(text):
        raise ValueError("未找到 JSON 起始符号")
    text = text[start_idx:]
    # 从尾部开始找最后一个 ']' 或 '}'
    end_idx = -1
    for ch in ("]", "}"):
        j = text.rfind(ch)
        if j > end_idx:
            end_idx = j
    if end_idx == -1:
        raise ValueError("未找到 JSON 结束符号")
    text = text[: end_idx + 1]
    return json.loads(text)


def _llm_structured_extract(client: OpenAI, page_text: str, url: str, industry: str) -> List[Dict[str, str]]:
    if not page_text:
        return []
    system_prompt = (
        "你是一个专业的一级市场投融资分析助手。"
        "现在给你一篇网页的正文内容，请你从中提取**所有与国内 VR / AR / XR 等相关公司 A 轮、A+ 轮、A++ 轮、Pre-A 轮等相近早期轮次融资事件**。"
        "输出严格的 JSON 数组，每个元素是一个对象，字段包括：\n"
        "- 公司名称（string）\n"
        "- 轮次（string，如 A轮、A+轮、Pre-A轮）\n"
        "- 融资金额（string，例如 “数千万元人民币”、“1亿元人民币”等）\n"
        "- 融资时间（string，尽量用 YYYY-MM 或 YYYY-MM-DD；若无法确定，可写“未知”）\n"
        "- 行业（string，例如 VR、AR、XR，若无法确定，可写“未知”）\n"
        "- 来源（string，写简短来源说明，可包含该网页 URL）\n"
        "如果网页中没有任何相关融资事件，请输出空数组 []。"
    )
    user_prompt = (
        f"网页 URL：{url}\n\n"
        "网页正文内容如下（可能不完整）：\n"
        "--------------------\n"
        f"{page_text}\n"
        "--------------------\n\n"
        "请按照系统提示，提取相关融资事件，并只输出 JSON。"
    )
    try:
        resp = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.1,
        )
    except Exception as e:
        print(f"调用 LLM 解析网页失败：{url} - {e}")
        return []

    content = resp.choices[0].message.content or ""
    try:
        data = _extract_json_from_text(content)
    except Exception as e:
        print(f"解析 LLM 返回 JSON 失败：{e}，原始内容截断：{content[:200]}...")
        return []

    if isinstance(data, dict):
        data = [data]
    if not isinstance(data, list):
        return []

    records: List[Dict[str, str]] = []
    for item in data:
        if not isinstance(item, dict):
            continue
        records.append(
            {
                "公司名称": str(item.get("公司名称") or item.get("company") or "未知"),
                "轮次": str(item.get("轮次") or item.get("round") or "未知"),
                "融资金额": str(item.get("融资金额") or item.get("amount") or "未知"),
                "融资时间": str(item.get("融资时间") or item.get("date") or "未知"),
                "行业": str(item.get("行业") or industry or "未知"),
                "来源": str(item.get("来源") or url),
            }
        )
    return records


def fetch_vr_financing_data() -> List[Dict[str, str]]:
    """
    优先使用企查查 API（若已配置 QCC_API_KEY、QCC_SECRET_KEY），
    否则回退到：必应搜索 → 抓网页正文 → LLM 抽取 → 统一格式。
    """
    if QCC_API_KEY and QCC_SECRET_KEY:
        print("使用企查查 API 拉取 VR 融资数据...")
        try:
            records = fetch_vr_financing_qcc(QCC_API_KEY, QCC_SECRET_KEY)
            if records:
                print(f"企查查共返回 {len(records)} 条 VR 融资记录。")
            else:
                print("企查查未返回符合条件的数据。")
            return records
        except Exception as e:
            print(f"企查查 API 调用失败，回退到网页+LLM 方式: {e}")

    # 回退：必应 + 网页正文 + LLM 抽取
    client = _get_llm_client()
    all_records: Dict[str, Dict[str, str]] = {}

    for cfg in SEARCH_CONFIGS:
        query = cfg["query"]
        industry = cfg["industry"]
        print(f"正在搜索：{query}")
        results = _search_bing(query, limit=5)
        for r in results:
            url = r["link"]
            print(f"  解析网页：{url}")
            page_text = _fetch_page_text(url)
            if not page_text:
                continue
            extracted = _llm_structured_extract(client, page_text, url, industry)
            for item in extracted:
                key = f"{item.get('公司名称','')}|{item.get('轮次','')}|{item.get('融资时间','')}"
                if key in all_records:
                    continue
                all_records[key] = item

    records = list(all_records.values())
    if not records:
        print("本次未能从网页中提取到任何 VR 融资记录。")
    else:
        print(f"本次共从网页中提取出 {len(records)} 条 VR 融资记录。")
    return records


def export_to_excel(records: List[Dict[str, str]], filename: Path) -> None:
    """将融资数据写入 Excel 文件（覆盖写）。"""
    if not records:
        print("没有可写入的数据，跳过生成 Excel。")
        return

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "VR融资情况"

    # 表头顺序
    headers = ["公司名称", "轮次", "融资金额", "融资时间", "行业", "来源"]
    ws.append(headers)

    for item in records:
        row = [item.get(h, "") for h in headers]
        ws.append(row)

    # 自动列宽（简单根据最大长度估算）
    for idx, header in enumerate(headers, start=1):
        max_len = len(header)
        for cell in ws[get_column_letter(idx)]:
            try:
                max_len = max(max_len, len(str(cell.value)))
            except Exception:
                pass
        ws.column_dimensions[get_column_letter(idx)].width = max_len + 2

    # 确保父目录存在
    filename.parent.mkdir(parents=True, exist_ok=True)
    wb.save(str(filename))
    print(f"已写入 Excel 文件：{filename}")


def job_once() -> None:
    """执行一次：抓取数据并写入 Excel。"""
    print(f"[{datetime.datetime.now().isoformat(sep=' ', timespec='seconds')}] 开始抓取 VR / A 轮融资数据...")
    data = fetch_vr_financing_data()
    # 文件名中包含日期 + 小时分钟，避免覆盖历史版本
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    reports_dir = Path(__file__).resolve().parent / "vr_reports"
    filename = reports_dir / f"vr_financing_{ts}.xlsx"
    export_to_excel(data, filename)
    print(f"[{datetime.datetime.now().isoformat(sep=' ', timespec='seconds')}] 本次任务完成。")


def run_scheduler() -> None:
    """
    启动定时任务：
    - 启动时立刻执行一次 job_once（方便测试）。
    - 之后每 1 分钟执行一次 job_once，并在控制台打印倒计时。
    - 真正上线时可以改回每天某个固定时间。
    """
    schedule.clear()
    schedule.every(1).minutes.do(job_once)
    print("定时任务已启动：每 1 分钟抓取一次必应搜索结果并生成 VR 融资 Excel。按 Ctrl+C 可退出。")

    # 先立即执行一次，方便测试
    job_once()

    while True:
        # 计算距离下一次执行的剩余秒数
        # schedule.next_run 是一个函数，需要调用得到下次运行时间
        next_run = schedule.next_run()
        if next_run is None:
            # 理论上不会出现，没有任务时简单等 1 秒
            sleep_seconds = 1
        else:
            now = datetime.datetime.now()
            delta = (next_run - now).total_seconds()
            sleep_seconds = max(1, int(delta))  # 至少等待 1 秒

        for remaining in range(sleep_seconds, 0, -1):
            print(f"\r距离下次抓取还有 {remaining:3d} 秒", end="", flush=True)
            time.sleep(1)
        print()  # 换行

        schedule.run_pending()


if __name__ == "__main__":
    # 直接运行本文件时，默认启动定时任务
    run_scheduler()

