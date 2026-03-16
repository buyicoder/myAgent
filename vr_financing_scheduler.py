"""
定时搜索国内 VR / A 轮融资情况，并整理成 Excel。

当前版本（便于测试）：
- 脚本一运行就立刻抓取一次并生成一份 Excel。
- 之后每分钟再抓取一次，并在控制台打印「距离下次抓取还有 X 秒」的倒计时。
- 每一份 Excel 的文件名精确到分钟，不会覆盖原文件。
- 所有 Excel 文件统一保存在脚本同级目录下的 `vr_reports/` 文件夹中。
"""
import datetime
import time
from pathlib import Path
from typing import List, Dict

import openpyxl
from openpyxl.utils import get_column_letter
import schedule
import requests
from bs4 import BeautifulSoup


def fetch_vr_financing_data() -> List[Dict[str, str]]:
    """
    用必应搜索“国内 VR A轮 融资”，抓取若干条搜索结果标题+链接，整理为结构化数据。

    仅用于测试流程，不保证搜索结果完全精准，只是方便你验证：
    - 定时调度是否正常
    - Excel 文件是否生成、格式是否符合预期
    """
    query = "国内 VR A轮 融资"
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
        print(f"请求必应失败: {e}")
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    results: List[Dict[str, str]] = []

    # 必应搜索结果大致结构：li.b_algo 里的 h2 > a
    for li in soup.select("li.b_algo")[:10]:  # 只取前 10 条
        a = li.select_one("h2 a")
        if not a:
            continue
        title = a.get_text(strip=True)
        link = a.get("href", "")
        snippet_el = li.select_one(".b_caption p")
        snippet = snippet_el.get_text(strip=True) if snippet_el else ""

        results.append(
            {
                "公司名称": title,  # 对测试来说，把标题当成“公司/新闻标题”
                "轮次": "未知",      # 网页没结构化数据，这里仅占位
                "融资金额": "未知",
                "融资时间": datetime.date.today().isoformat(),
                "行业": "VR（搜索关键字）",
                "来源": f"{link}（{snippet}）",
            }
        )

    if not results:
        print("未从必应搜索中解析到结果。")
    return results


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

