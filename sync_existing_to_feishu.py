"""
一键将本地已导出的 Excel（vr_reports/、vr_reports_qcc/）同步到飞书云文档。

使用前请在 .env 中配置 FEISHU_APP_ID、FEISHU_APP_SECRET、FEISHU_FOLDER_TOKEN。
已同步过的文件会记录在 .feishu_synced.txt，再次运行不会重复上传。

用法：
  conda activate agent
  python sync_existing_to_feishu.py
"""

from pathlib import Path

from data_sources.feishu_upload import sync_local_excel_to_feishu

if __name__ == "__main__":
    root = Path(__file__).resolve().parent
    n = sync_local_excel_to_feishu(root)
    print(f"同步完成，本次上传 {n} 个文件。")
