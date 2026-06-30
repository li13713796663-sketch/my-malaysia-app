"""PostgreSQL 连接与自动建表（凭证来自 st.secrets["postgres"]["conn_str"]）"""

from __future__ import annotations

import re
import socket
import subprocess
from contextlib import contextmanager
from urllib.parse import urlparse

import psycopg2
import psycopg2.extras
import streamlit as st

_schema_ready = False

USERS_DDL = """
CREATE TABLE IF NOT EXISTS users (
    username      VARCHAR(100) PRIMARY KEY,
    password_hash TEXT         NOT NULL,
    role          VARCHAR(50)  NOT NULL DEFAULT 'admin',
    created_at    TIMESTAMPTZ  DEFAULT NOW()
);
"""

STUDENTS_DDL = """
CREATE TABLE IF NOT EXISTS students (
    id                  VARCHAR(50) PRIMARY KEY,
    name                TEXT NOT NULL DEFAULT '',
    pinyin              TEXT DEFAULT '',
    gender              TEXT DEFAULT '',
    birth_date          TEXT DEFAULT '',
    passport_no         TEXT DEFAULT '',
    departure_city      TEXT DEFAULT '',
    hobbies             TEXT DEFAULT '',
    enrollment_year     TEXT DEFAULT '',
    enrollment_month    TEXT DEFAULT '',
    city_my             TEXT DEFAULT '',
    region              TEXT DEFAULT '',
    school_type         TEXT DEFAULT '',
    initial_grade       TEXT DEFAULT '',
    status              TEXT DEFAULT '',
    transfer_note       TEXT DEFAULT '',
    emergency_phone_cn  TEXT DEFAULT '',
    guardian_my         TEXT DEFAULT '',
    created_by          TEXT DEFAULT '',
    created_at          TEXT DEFAULT '',
    updated_at          TEXT DEFAULT '',
    state               TEXT DEFAULT ''
);
"""


def _conn_str() -> str:
    pg = st.secrets["postgres"]
    return pg.get("pooler_conn_str") or pg["conn_str"]


def _host_resolves(hostname: str) -> bool:
    if not hostname:
        return False
    for family in (socket.AF_INET, socket.AF_INET6):
        try:
            socket.getaddrinfo(hostname, None, family, socket.SOCK_STREAM)
            return True
        except OSError:
            continue
    return False


def _resolve_host_with_nslookup(hostname: str) -> str | None:
    """Windows 上 Python DNS 偶发失败时，尝试用系统 nslookup 取回 IPv6/IPv4 地址。"""
    try:
        completed = subprocess.run(
            ["nslookup", hostname],
            capture_output=True,
            text=True,
            timeout=8,
            check=False,
        )
    except Exception:
        return None

    output = f"{completed.stdout}\n{completed.stderr}"
    # 优先匹配 Supabase 直连常见的 IPv6 地址，其次匹配 IPv4。
    ipv6_matches = re.findall(r"\b(?:[0-9a-fA-F]{1,4}:){2,}[0-9a-fA-F]{1,4}\b", output)
    if ipv6_matches:
        return ipv6_matches[-1]

    ipv4_matches = re.findall(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", output)
    # 第一个 IPv4 往往是本地 DNS 服务器地址，所以取最后一个更可能是目标地址。
    if ipv4_matches:
        return ipv4_matches[-1]
    return None


def _connect_with_hostaddr(conn_str: str, hostaddr: str):
    """使用 libpq 的 hostaddr 绕过本机 DNS，同时保留原始 host。"""
    params = psycopg2.extensions.parse_dsn(conn_str)
    params["host"] = params.get("host") or urlparse(conn_str).hostname
    params["hostaddr"] = hostaddr
    params.setdefault("connect_timeout", "15")
    return psycopg2.connect(**params)


def _connect():
    conn_str = _conn_str()
    parsed = urlparse(conn_str)
    host = parsed.hostname or ""

    if host.endswith(".supabase.co") and not _host_resolves(host):
        hostaddr = _resolve_host_with_nslookup(host)
        if hostaddr:
            try:
                return _connect_with_hostaddr(conn_str, hostaddr)
            except psycopg2.OperationalError:
                pass

        st.error(
            "⚠️ **数据库域名无法解析（DNS 失败）**\n\n"
            f"当前主机：`{host}`\n\n"
            "本机 Python 无法解析 Supabase 直连域名。系统已尝试使用 `nslookup` 绕过 DNS，"
            "但仍无法建立连接。\n\n"
            "请到 Supabase 控制台复制官方 **Session Pooler** 连接串：\n\n"
            "**Project Settings → Database → Connection Pooling → Session mode**\n\n"
            "然后替换 `.streamlit/secrets.toml` 中的 `conn_str`。"
        )
        st.stop()

    try:
        return psycopg2.connect(conn_str, connect_timeout=15)
    except psycopg2.OperationalError as exc:
        msg = str(exc).lower()
        if "tenant/user" in msg or "[enotfound]" in msg:
            st.error(
                "⚠️ **Supabase Pooler 租户识别失败**\n\n"
                "当前已经连接到了 Supabase Pooler，但 Pooler 返回：`tenant/user not found`。\n\n"
                "这通常表示 `.streamlit/secrets.toml` 中的 **Session Pooler 连接串不是该项目官方生成的那一条**，"
                "尤其是以下两处不能靠猜：\n\n"
                "1. `aws-0-区域.pooler.supabase.com` 的区域必须和 Supabase 控制台一致。\n"
                "2. 用户名必须使用控制台给出的 Pooler 用户名，通常形如 `postgres.项目租户ID`。\n\n"
                "请到 Supabase 控制台复制官方连接串：\n\n"
                "**Project Settings → Database → Connection Pooling → Session mode**\n\n"
                "然后把整段连接串覆盖到 `.streamlit/secrets.toml` 的 `conn_str`。"
            )
            st.stop()
        if "could not translate host name" in msg or "name or service not known" in msg:
            st.error(
                "⚠️ **无法连接 Supabase 数据库（DNS 解析失败）**\n\n"
                "请改用 Supabase **Session Pooler** 连接串（含 `pooler.supabase.com`，用户名格式为 "
                "`postgres.项目ID`）。详见 `.streamlit/secrets.toml.example`。"
            )
            st.stop()
        raise


def ensure_schema() -> None:
    global _schema_ready
    if _schema_ready:
        return
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(USERS_DDL)
            cur.execute(STUDENTS_DDL)
        conn.commit()
    _schema_ready = True


@contextmanager
def get_connection():
    conn = _connect()
    try:
        yield conn
    finally:
        conn.close()


def fetch_all(sql: str, params: tuple | None = None) -> list[dict]:
    ensure_schema()
    with get_connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql, params or ())
            rows = cur.fetchall()
    return [_row_to_dict(r) for r in rows]


def fetch_one(sql: str, params: tuple | None = None) -> dict | None:
    rows = fetch_all(sql, params)
    return rows[0] if rows else None


def execute(sql: str, params: tuple | None = None) -> None:
    ensure_schema()
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
        conn.commit()


def _row_to_dict(row: dict) -> dict:
    out = {}
    for k, v in row.items():
        if v is None:
            out[k] = ""
        elif hasattr(v, "isoformat"):
            out[k] = v.isoformat(timespec="seconds")
        else:
            out[k] = str(v)
    return out
