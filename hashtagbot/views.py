import email
import imaplib
import json
import random
import re
import time
import django
django.setup()
from django.shortcuts import render
from django.views import View

from instagrapi import Client
from instagrapi.exceptions import ChallengeRequired
from instagrapi.mixins.challenge import ChallengeChoice

# Create your views here.
from hashtagbot.models import Worker, AccountInfo
from multiprocessing import Process

from hashtagbot.tasks import login


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


def index(request):

    return render(request, 'index.html')




class Search(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return render(request, '403.html')
        return render(request, 'hashtag_search.html')

    def post(self, request):

        hashtag = request.POST.get('hashtag')

        workers = Worker.objects.filter(is_active=True, is_working=False, user=request.user).first()
        if workers:
            try:
                cl = Client()

                cl.challenge_code_handler = challenge_code_handler
                cl.change_password_handler = change_password_handler

                cl.login(workers.username, workers.password)
                workers.is_working = True
                workers.save()
                print("Login success")
                tag = hashtag
                medias = cl.hashtag_medias_top(tag, 100)
                users = []

                for media in medias:
                    users.append(media.dict()['user']['username'])

                print("getting users from medias done")

                # set users to remove duplicates
                users = set(users)
                user_context = []
                for user in users:
                    AccountInfo.objects.get_or_create(username=user, from_tag=tag, user=request.user)
                    print(f"new user added: {user}")
                    if AccountInfo.objects.filter(username=user, from_tag=tag, is_checked=False,
                                                  user=request.user).exists():
                        user_context.append(user)
                context = {
                    'users': user_context
                }
                workers.is_working = False
                workers.save()



            except Exception as e:
                print(e)
                workers.is_working = False
                workers.is_active = False
                workers.save()
                return render(request, 'hashtag_search.html', {'error': 'مشکلی پیش آمده است'})
        else:
            return render(request, 'hashtag_search.html', {'error': 'کارگری یافت نشد'})

        return render(request, 'hashtag_search.html', {'success': 'اطلاعات دریافت شد', 'context': context})

class AccountInfoResult(View):
    def get(self, request):
        accounts = AccountInfo.objects.filter(is_checked=False,user=request.user)
        context = {
            'accounts': accounts
        }
        return render(request, 'account_info.html', context)

    def post(self, request):


        workers = Worker.objects.filter(is_active=True, is_working=False,user=request.user)
        accounts = AccountInfo.objects.filter(is_checked=False,user=request.user)
        if workers:
            try:
                login(workers, accounts)

                return render(request, 'account_info.html', {'success': 'اطلاعات در حال دریافت می باشد'})
            except Exception as e:
                print(e)
                return render(request, 'account_info.html', {'error': 'مشکلی پیش آمده است'})

        return render(request, 'account_info.html', {'error': 'کارگری یافت نشد'})
#

