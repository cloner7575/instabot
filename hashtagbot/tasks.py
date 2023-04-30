import email
import imaplib
import json
import random
import re
import time
from multiprocessing import Process

import django
django.setup()
from django.db.models import Count
from instagrapi import Client
from instagrapi.exceptions import LoginRequired,UserNotFound

from hashtagbot.models import Worker, AccountInfo
from instagrapi.mixins.challenge import ChallengeChoice

def change_password_handler(username):
    # Simple way to generate a random string
    chars = list("abcdefghijklmnopqrstuvwxyz1234567890!&£@#")
    password = "".join(random.sample(chars, 8))
    return password
def get_code_from_sms(username):
    while True:
        code = input(f"Enter code (6 digits) for {username}: ").strip()
        if code and code.isdigit():
            return code
    return None


def challenge_code_handler(username, choice):
    if choice == ChallengeChoice.SMS:
        return get_code_from_sms(username)
    elif choice == ChallengeChoice.EMAIL:
        return get_code_from_email(username)
    return False

def get_code_from_email(username):
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(user="luccopilot@gmail.com",password= "knjkjbxusnapdtlo")
    mail.select("inbox")
    result, data = mail.search(None, "(UNSEEN)")
    assert result == "OK", "Error1 during get_code_from_email: %s" % result
    ids = data.pop().split()
    for num in reversed(ids):
        mail.store(num, "+FLAGS", "\\Seen")  # mark as read
        result, data = mail.fetch(num, "(RFC822)")
        assert result == "OK", "Error2 during get_code_from_email: %s" % result
        msg = email.message_from_string(data[0][1].decode())
        payloads = msg.get_payload()
        if not isinstance(payloads, list):
            payloads = [msg]
        code = None
        for payload in payloads:
            body = payload.get_payload(decode=True).decode()
            if "<div" not in body:
                continue
            match = re.search(">([^>]*?({u})[^<]*?)<".format(u=username), body)
            if not match:
                continue
            print("Match from email:", match.group(1))
            match = re.search(r">(\d{6})<", body)
            if not match:
                print('Skip this email, "code" not found')
                continue
            code = match.group(1)
            if code:
                return code
    return False

def worker_login(worker, accounts):
    try:
        cl = Client()
        cl.challenge_code_handler = challenge_code_handler
        cl.change_password_handler = change_password_handler
        cl.login(worker.username, worker.password)
        print("Login success")
        time.sleep(random.randint(10, 30))
        worker.is_working = True
        worker.save()


        for account in accounts:
            try:
                user_info = cl.user_info_by_username(account.username).dict()
                phone_number = user_info['contact_phone_number']
                if phone_number:
                    account.phone_number = phone_number
                    account.is_business = True
                account.is_checked = True
                account.other_info = json.dumps(user_info)
                account.save()
                print(f"info of {account.username} is: {phone_number}")
                time.sleep(random.randint(90, 300))
            except UserNotFound as e:
                print(e)
                account.is_checked = True
                account.save()
                time.sleep(random.randint(90, 300))
                continue
            except LoginRequired :
                cl.login(worker.username, worker.password)
                continue
        worker.is_working = False
        worker.save()
    except Exception as e:
        print(e)
        worker.is_working = False
        worker.save()
        return



def login(workers, accounts):
    print("cron is running")
    print(f"workers: {workers}")
    print(f"accounts: {accounts}")
    if workers:
        try:

            accounts_start = 0
            accounts_increment = len(accounts) // len(workers)
            for worker in workers:
                accounts_end = accounts_start + accounts_increment
                if accounts_end > len(accounts):
                    accounts_end = len(accounts)
                accounts_to_check = accounts[accounts_start:accounts_end]
                p = Process(target=worker_login, args=(worker, accounts_to_check,))
                p.start()
                accounts_start = accounts_end
        except Exception as e:
            print(e)


def run_bot():
    print("run_bot is running")
    users = AccountInfo.objects.values('user').annotate(user_count=Count('user')).filter(user_count__gt=1)

    print(f"users: {users}")
    for user in users:
        workers = Worker.objects.filter(is_active=True, is_working=False, user_id=user['user'])
        accounts = AccountInfo.objects.filter(is_checked=False, user_id=user['user'])
        p = Process(target=login, args=(workers, accounts,))
        p.start()
