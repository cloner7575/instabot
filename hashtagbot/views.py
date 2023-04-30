import json
import time

from django.shortcuts import render
from django.views import View

from instagrapi import Client
from instagrapi.exceptions import ChallengeRequired
# Create your views here.
from .models import Worker, AccountInfo
from multiprocessing import Process

from .tasks import login, change_password_handler, challenge_code_handler


def index(request):

    return render(request, 'index.html')

# def worker_login(worker, accounts):
#     try:
#         cl = Client()
#         cl.change_password_handler = change_password_handler
#         cl.challenge_code_handler = challenge_code_handler
#         cl.login(worker.username, worker.password)
#         worker.is_working = True
#         worker.save()
#
#         print("Login success")
#         for account in accounts:
#             user_info = cl.user_info_by_username(account.username).dict()
#             phone_number = user_info['contact_phone_number']
#             if phone_number:
#                 account.phone_number = phone_number
#                 account.is_business = True
#             account.is_checked = True
#             account.other_info = json.dumps(user_info)
#             account.save()
#             print(f"info of {account.username} is: {phone_number}")
#             time.sleep(5)
#         worker.is_working = False
#         worker.save()
#     except Exception as e:
#         print(e)
#         worker.is_working = False
#         worker.save()
#         return


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

