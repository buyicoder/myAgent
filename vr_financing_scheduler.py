"""
定时搜索国内 VR / A 轮融资情况，并整理成 Excel。

说明：
- 本示例提供了完整的“调度 + 数据整理 + 写 Excel”流水线。
- 真正“去哪儿抓融资数据”取决于你选用的接口/源站，需要你填入自己的数据源逻辑。
"""
import datetime
import time
from typing import List, Dict

import openpyxl
from openpyxl.utils import get_column_letter
import schedule


def fetch_vr_financing_data() -> List[Dict[str, str]]:
    """
    抓取“国内 VR / A 轮融资”相关数据，返回结构化列表。

    ⚠️ 注意：这里不会真的去爬取某个具体网站，原因是：
    - 各网站的反爬、接口规则不同，容易失效；
    - 你可能有自己授权的内部/第三方数据源。

    使用方式：
    - 把你自己的“数据拉取逻辑”写在这里（调用数据库、内部 HTTP 接口、爬虫等），
      然后返回形如：
      [
        {
          "公司名称": "公司A",
          "轮次": "A轮",
          "融资金额": "数千万元人民币",
          "融资时间": "2024-01-15",
          "行业": "VR/AR",
          "来源": "xxx网站/内部系统",
        },
        ...
      ]
    """
    # 这里先返回一个示例数据，方便你确认 Excel 结构是否符合预期
    today = datetime.date.today().isoformat()
    return [
        {
            "公司名称": "示例公司A",
            "轮次": "A轮",
            "融资金额": "数千万人民币",
            "融资时间": today,
            "行业": "VR",
            "来源": "示例数据源（请替换为真实数据）",
        }
    ]


def export_to_excel(records: List[Dict[str, str]], filename: str) -> None:
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

    wb.save(filename)
    print(f"已写入 Excel 文件：{filename}")


def job_once() -> None:
    """执行一次：抓取数据并写入 Excel。"""
    print(f"[{datetime.datetime.now().isoformat(sep=' ', timespec='seconds')}] 开始抓取 VR / A 轮融资数据...")
    data = fetch_vr_financing_data()
    # 文件名中加日期，避免覆盖历史；你也可以固定为一个文件名
    date_str = datetime.date.today().strftime("%Y%m%d")
    filename = f"vr_financing_{date_str}.xlsx"
    export_to_excel(data, filename)
    print(f"[{datetime.datetime.now().isoformat(sep=' ', timespec='seconds')}] 本次任务完成。")


def run_scheduler() -> None:
    """
    启动定时任务：
    - 下面示例是：每天早上 9:00 执行一次 job_once
    - 如需改时间，把 '09:00' 改成你想要的时间，例如 '10:30'
    """
    schedule.clear()
    schedule.every().day.at("09:00").do(job_once)
    print("定时任务已启动：每天 09:00 抓取并生成 VR 融资 Excel。按 Ctrl+C 可退出。")

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    # 直接运行本文件时，默认启动定时任务
    run_scheduler()

