import json
import time
from multiprocessing import Process

from django.db.models import Count
from instagrapi import Client
import django

django.setup()
from hashtagbot.models import Worker, AccountInfo


def worker_login(worker, accounts):
    try:
        cl = Client()
        cl.login(worker.username, worker.password)
        worker.is_working = True
        worker.save()

        print("Login success")
        for account in accounts:
            user_info = cl.user_info_by_username(account.username).dict()
            phone_number = user_info['contact_phone_number']
            if phone_number:
                account.phone_number = phone_number
                account.is_business = True
            account.is_checked = True
            account.other_info = json.dumps(user_info)
            account.save()
            print(f"info of {account.username} is: {phone_number}")
            time.sleep(10)
        worker.is_working = False
        worker.save()
    except Exception as e:
        print(e)
        worker.is_active = False
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
