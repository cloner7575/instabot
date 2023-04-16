import asyncio
import datetime

import pandas as pd
from django.db.models import Q, Count
from django.shortcuts import render
from telethon import TelegramClient, functions, types
from telethon.errors import FloodWaitError
from .forms import ContactAdminForm

from telegrambot.models import Contact, TelegramWorker


# Create your views here.
async def save_contact_to_telegram(phone, least_used_worker):
    client = TelegramClient(least_used_worker.session_name, int(least_used_worker.api_id),
                            least_used_worker.api_hash)
    await client.connect()

    # save contact to telegram
    try:
        print(f"adding {phone} to telegram")
        result = await client(functions.contacts.ImportContactsRequest(
            contacts=[types.InputPhoneContact(phone=phone, first_name=phone,
                                              last_name='', client_id=0)]))
        await client.disconnect()

        return result
    except FloodWaitError as e:
        await client.disconnect()
        raise e


def save_contacts(request):
    if request.method == 'GET':
        form = ContactAdminForm()
        return render(request, 'save_contacts.html', {'form': form})
    if request.method == 'POST':
        excel_file = request.FILES['excel_file']
        df = pd.read_excel(excel_file, dtype=str)
        existing_contacts = Contact.objects.filter(worker__user=request.user)

        for _, row in df.iterrows():

            for _, cell in row.items():

                if len(cell) > 10:
                    if existing_contacts.filter(phone_number=cell).exists():
                        continue
                    workers = TelegramWorker.objects.filter(
                        Q(is_active=True) & Q(add_contact_today__lt=100) & Q(user=request.user) & (
                                ~Q(baned_until__gte=datetime.datetime.utcnow()) | Q(baned_until=None)))
                    if workers:
                        least_used_worker = None
                        worker_count = Contact.objects.values('worker').annotate(
                            count=Count('worker')).order_by(
                            'count')
                        for worker in workers:
                            if Contact.objects.filter(worker=worker).exists():
                                continue
                            else:
                                least_used_worker = worker
                                break
                        if not least_used_worker:
                            if worker_count:
                                least_used_worker_id = worker_count.first()['worker']
                                least_used_worker = TelegramWorker.objects.get(pk=least_used_worker_id)
                            else:
                                least_used_worker = workers.first()

                        try:
                            least_used_worker.is_working = True
                            least_used_worker.save()
                            res = asyncio.run(save_contact_to_telegram(cell, least_used_worker))
                            if res.users:
                                Contact.objects.create(phone_number=cell, username=res.users[0].username,
                                                       worker=least_used_worker, has_telegram=True)

                                print(f"contact {cell} saved")
                            else:
                                Contact.objects.create(phone_number=cell, username=None,
                                                       worker=least_used_worker, has_telegram=False)

                                print(f"contact {cell} saved")

                            least_used_worker.add_contact_today += 1
                            least_used_worker.is_working = False
                            least_used_worker.save()
                        except FloodWaitError as e:
                            least_used_worker.is_working = False
                            least_used_worker.baned_until = datetime.datetime.utcnow() + datetime.timedelta(
                                seconds=e.seconds)
                            least_used_worker.save()
                            print(f"worker {least_used_worker.session_name} banned for {e.seconds} seconds")

                        except Exception as e:
                            least_used_worker.is_working = False
                            least_used_worker.save()
                            print(e)
                    else:
                        return render(request, 'save_contacts.html', {'error': 'هیچ کارگری فعال نیست'})

        return render(request, 'save_contacts.html', {'success': 'برای هر کارگر 100 مخاطب اضافه شد'})
