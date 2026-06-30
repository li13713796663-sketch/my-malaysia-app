"""
留学生档案管理系统 — 专属最高权限底层安全验证引擎
数据层：PostgreSQL（psycopg2 + st.secrets["postgres"]["conn_str"]）
"""

from __future__ import annotations

import hashlib
from datetime import datetime

import db

ROLE_SUPER = "super_admin"
ROLE_ADMIN = "admin"
ROOT_USERNAME = "liuweifeng"
ROOT_INIT_PASSWORD = "lwf1234"


def hash_password(password: str) -> str:
    return hashlib.sha256(password.strip().encode("utf-8")).hexdigest()


def _password_matches(stored: str, raw: str) -> bool:
    stored = str(stored or "").strip()
    raw = raw.strip()
    if not stored:
        return False
    if stored == hash_password(raw):
        return True
    return stored == raw


def _load_users_raw() -> list[dict]:
    return db.fetch_all("SELECT * FROM users ORDER BY username")


def _ensure_root_account() -> None:
    db.ensure_schema()
    root = db.fetch_one("SELECT username FROM users WHERE username = %s", (ROOT_USERNAME,))
    if root:
        return
    db.execute("DELETE FROM users WHERE username = %s", ("admin",))
    db.execute(
        """
        INSERT INTO users (username, password_hash, role, created_at)
        VALUES (%s, %s, %s, %s)
        """,
        (
            ROOT_USERNAME,
            hash_password(ROOT_INIT_PASSWORD),
            ROLE_SUPER,
            datetime.now().isoformat(timespec="seconds"),
        ),
    )


def _upgrade_plaintext_if_needed(username: str, raw_password: str) -> None:
    user = db.fetch_one("SELECT password_hash FROM users WHERE username = %s", (username,))
    if not user:
        return
    stored = user["password_hash"]
    if stored and stored != hash_password(raw_password) and stored == raw_password:
        db.execute(
            "UPDATE users SET password_hash = %s WHERE username = %s",
            (hash_password(raw_password), username),
        )


def load_users() -> list[dict]:
    _ensure_root_account()
    return _load_users_raw()


def verify_login(username: str, password: str) -> dict | None:
    username = username.strip()
    if not username or not password:
        return None
    for u in load_users():
        if u["username"] == username and _password_matches(u["password_hash"], password):
            _upgrade_plaintext_if_needed(username, password)
            return u
    return None


def change_my_password(username: str, old_pass: str, new_pass: str) -> tuple[bool, str]:
    new_pass = new_pass.strip()
    if len(new_pass) < 6:
        return False, "新密码长度至少需要 6 个字符。"

    user = db.fetch_one("SELECT password_hash FROM users WHERE username = %s", (username.strip(),))
    if not user:
        return False, "用户不存在。"
    if not _password_matches(user["password_hash"], old_pass):
        return False, "旧密码验证错误，修改失败。"

    db.execute(
        "UPDATE users SET password_hash = %s WHERE username = %s",
        (hash_password(new_pass), username.strip()),
    )
    return True, "密码修改成功，请牢记新密码。"


def create_admin(
    new_user: str,
    new_pass: str,
    current_operator: str,
    operator_pass: str,
) -> tuple[bool, str]:
    if current_operator.strip() != ROOT_USERNAME:
        return False, f"越权拦截：仅超级管理员 {ROOT_USERNAME} 可创建账号。"

    if not verify_login(current_operator, operator_pass):
        return False, "身份核验失败：当前操作人密码错误，无权创建。"

    new_user = new_user.strip()
    new_pass = new_pass.strip()
    if len(new_user) < 3:
        return False, "账号名至少需要 3 个字符。"
    if len(new_pass) < 6:
        return False, "初始密码至少需要 6 个字符。"

    exists = db.fetch_one("SELECT username FROM users WHERE username = %s", (new_user,))
    if exists:
        return False, f"账号「{new_user}」已存在。"

    db.execute(
        """
        INSERT INTO users (username, password_hash, role, created_at)
        VALUES (%s, %s, %s, %s)
        """,
        (new_user, hash_password(new_pass), ROLE_ADMIN, datetime.now().isoformat(timespec="seconds")),
    )
    return True, f"已成功创建普通管理员：{new_user}"


def delete_admin(
    username_to_del: str,
    current_operator: str,
    operator_pass: str,
) -> tuple[bool, str]:
    if current_operator.strip() != ROOT_USERNAME:
        return False, f"越权拦截：仅超级管理员 {ROOT_USERNAME} 可注销账号。"

    if not verify_login(current_operator, operator_pass):
        return False, "身份核验失败：当前操作人密码错误，无权注销。"

    target = username_to_del.strip()
    if target == ROOT_USERNAME:
        return False, "核心安全锁：超级管理员账号不可删除。"

    exists = db.fetch_one("SELECT username FROM users WHERE username = %s", (target,))
    if not exists:
        return False, "未找到该账号。"

    db.execute("DELETE FROM users WHERE username = %s", (target,))
    return True, f"已注销账号：{target}"


def list_admins() -> list[dict]:
    return load_users()


def is_super_admin(username: str) -> bool:
    return str(username).strip() == ROOT_USERNAME
