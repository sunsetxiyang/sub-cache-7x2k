#!/usr/bin/env python3
"""检查 QQ 收件箱是否有换 IP 触发邮件，按主题区分目标
主题规则（不区分大小写匹配子串）：
  "swap-us"  → 只换 us（美西 A）
  "swap-tw"  → 只换 tw（台湾 B）
  "swap"     → 两台都换
输出: 有触发时打印 TARGET=xxx 并退出 0；无触发退出 1
"""
import imaplib
import sys
import os

MAIL_HOST = "imap.qq.com"
MAIL_USER = os.environ.get("MAIL_USER", "")
MAIL_PASS = os.environ.get("MAIL_PASS", "")

if not MAIL_USER or not MAIL_PASS:
    print("缺少邮箱凭据")
    sys.exit(1)

try:
    mail = imaplib.IMAP4_SSL(MAIL_HOST, 993, timeout=30)
    mail.login(MAIL_USER, MAIL_PASS)
    mail.select("INBOX")

    # 优先级：先搜具体的（swap-us / swap-tw），再搜通用 swap
    target = None
    found_ids = None
    for keyword, t in [("swap-us", "us"), ("swap-tw", "tw"), ("swap", "both")]:
        status, data = mail.search(None, "UNSEEN", f'SUBJECT "{keyword}"')
        if status == "OK" and data[0].split():
            target = t
            found_ids = data[0].split()
            break

    if target is None:
        print("无触发邮件")
        mail.logout()
        sys.exit(1)

    print(f"发现触发邮件，目标: {target}")
    for mid in found_ids:
        mail.store(mid, "+FLAGS", "\\Seen")
    mail.logout()
    print(f"TARGET={target}")
    sys.exit(0)
except Exception as e:
    print(f"邮箱检查失败: {e}")
    sys.exit(1)
