"""
飞书云文档上传：将本地文件上传到指定云文档目录。

使用前请在飞书开放平台创建自建应用，开通「云文档」相关权限，
并获取要上传到的文件夹的 folder token。在 .env 中配置：
  FEISHU_APP_ID=cli_xxx
  FEISHU_APP_SECRET=xxx
  FEISHU_FOLDER_TOKEN=fldcnxxx

文档：https://open.feishu.cn/document/server-docs/docs/drive-v1/upload/upload_all
"""

import os
from pathlib import Path
from typing import Optional

import requests

FEISHU_API_BASE = "https://open.feishu.cn/open-apis"
TOKEN_URL = f"{FEISHU_API_BASE}/auth/v3/tenant_access_token/internal"
UPLOAD_URL = f"{FEISHU_API_BASE}/drive/v1/files/upload_all"

# 单文件最大 20MB，超过需分片上传（本模块未实现）
MAX_FILE_SIZE = 20 * 1024 * 1024


def get_tenant_access_token(app_id: str, app_secret: str) -> str:
    """自建应用获取 tenant_access_token。"""
    resp = requests.post(
        TOKEN_URL,
        json={"app_id": app_id, "app_secret": app_secret},
        headers={"Content-Type": "application/json; charset=utf-8"},
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()
    if data.get("code") != 0:
        raise RuntimeError(f"飞书获取 token 失败: {data.get('msg', data)}")
    return data["tenant_access_token"]


def upload_file_to_feishu(
    file_path: Path,
    folder_token: str,
    app_id: str,
    app_secret: str,
    file_name_override: Optional[str] = None,
) -> str:
    """
    将本地文件上传到飞书云文档指定目录。

    :param file_path: 本地文件路径
    :param folder_token: 云文档目录的 folder token（在浏览器打开该文件夹，URL 中含 fldcn...）
    :param app_id: 飞书自建应用 App ID
    :param app_secret: 飞书自建应用 App Secret
    :param file_name_override: 上传后显示的文件名，默认使用本地文件名
    :return: 上传成功后的文件 token（可用于生成链接等）
    """
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"文件不存在: {path}")

    size = path.stat().st_size
    if size > MAX_FILE_SIZE:
        raise ValueError(f"文件超过 20MB 限制: {path} ({size} bytes)")

    name = file_name_override or path.name
    token = get_tenant_access_token(app_id, app_secret)

    with open(path, "rb") as f:
        # 飞书 upload_all 要求 multipart: file_name, parent_type, parent_node, size, file
        files = {"file": (name, f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
        data = {
            "file_name": name,
            "parent_type": "explorer",
            "parent_node": folder_token,
            "size": str(size),
        }
        resp = requests.post(
            UPLOAD_URL,
            headers={"Authorization": f"Bearer {token}"},
            data=data,
            files=files,
            timeout=30,
        )

    resp.raise_for_status()
    result = resp.json()
    if result.get("code") != 0:
        raise RuntimeError(f"飞书上传失败: {result.get('msg', result)}")

    file_token = (result.get("data") or {}).get("file_token", "")
    return file_token


def upload_if_configured(
    file_path: Path,
    app_id: Optional[str] = None,
    app_secret: Optional[str] = None,
    folder_token: Optional[str] = None,
) -> bool:
    """
    若已配置飞书三项则上传，否则跳过。用于调度脚本中“可选上传”。

    :return: 是否执行了上传
    """
    from config import FEISHU_APP_ID, FEISHU_APP_SECRET, FEISHU_FOLDER_TOKEN

    app_id = app_id or FEISHU_APP_ID
    app_secret = app_secret or FEISHU_APP_SECRET
    folder_token = folder_token or FEISHU_FOLDER_TOKEN
    if not (app_id and app_secret and folder_token):
        return False
    try:
        upload_file_to_feishu(Path(file_path), folder_token, app_id, app_secret)
        print(f"已上传到飞书云文档：{file_path.name}")
        return True
    except Exception as e:
        print(f"飞书上传失败：{e}")
        return False
