#!/usr/bin/env python3
"""
用法（在 backend/ 目录下执行）：

    python scripts/create_user.py <用户名>

示例：
    python scripts/create_user.py shinichi
"""

import asyncio
import getpass
import sys
import os

# 将 backend/ 目录加入路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from passlib.context import CryptContext
from sqlalchemy import select

from app.database import AsyncSessionLocal, engine
from app.models import Base, User

_pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def create_user(username: str, password: str) -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        existing = await db.execute(select(User).where(User.username == username))
        if existing.scalar_one_or_none():
            print(f"错误：用户 '{username}' 已存在")
            return

        user = User(username=username, hashed_password=_pwd.hash(password))
        db.add(user)
        await db.commit()
        print(f"✅ 成功创建用户：{username}")


async def main() -> None:
    if len(sys.argv) < 2:
        print("用法：python scripts/create_user.py <用户名>")
        sys.exit(1)

    username = sys.argv[1]
    password = getpass.getpass("请输入密码：")
    confirm = getpass.getpass("确认密码：")

    if password != confirm:
        print("错误：两次密码不一致")
        sys.exit(1)

    if len(password) < 6:
        print("错误：密码长度至少 6 位")
        sys.exit(1)

    await create_user(username, password)


if __name__ == "__main__":
    asyncio.run(main())
