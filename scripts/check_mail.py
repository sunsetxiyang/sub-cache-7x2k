#!/usr/bin/env python3
"""检查 Outlook 收件箱是否有换 IP 触发邮件（主题含 "swap"）
返回 0 = 有触发（继续执行换 IP），1 = 无触发
"""
import imaplib
import sys
import os

MAIL_HOST = "outlook.office365.com"
MAIL_USER = os.environ.get("MAIL_USER", "")
MAIL_PASS = os.environ.get("MAIL_PASS", "")
KEYWORD = "swap"

if not MAIL_USER or not MAIL_PASS:
    print("缺少邮箱凭据")
    sys.exit(1)

try:
    mail = imaplib.IMAP4_SSL(MAIL_HOST, 993, timeout=30)
    mail.login(MAIL_USER, MAIL_PASS)
    mail.select("INBOX")

    # 搜索未读邮件（主题含关键词）
    status, data = mail.search(None, "UNSEEN", f'SUBJECT "{KEYWORD}"')
    if status != "OK":
        print("搜索失败")
        mail.logout()
        sys.exit(1)

    ids = data[0].split()
    if not ids:
        print(f"无触发邮件（未读且主题含 {KEYWORD} 的邮件数量: 0）")
        mail.logout()
        sys.exit(1)

    print(f"发现 {len(ids)} 封触发邮件，执行换 IP")
    # 标记已读，防止下次重复触发
    for mid in ids:
        mail.store(mid, "+FLAGS", "\\Seen")
    mail.logout()
    sys.exit(0)
except Exception as e:
    print(f"邮箱检查失败: {e}")
    sys.exit(1)
