import asyncio
import datetime
from django.contrib import admin
from django.db.models import Count, Q
from telethon.errors import FloodWaitError
from telegrambot.models import TelegramWorker, Contact
from telethon import TelegramClient, functions, types


class TelegramWorkerAdmin(admin.ModelAdmin):
    list_display = ('session_name', 'is_active', 'is_working')
    list_filter = ('is_active', 'is_working')
    readonly_fields = ('user',)

    def save_model(self, request, obj, form, change):
        if not change:
            obj.user = request.user
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            try:
                client = TelegramClient(obj.session_name, int(obj.api_id), obj.api_hash)
                client.start()

                obj.is_active = True
                client.disconnect()
                loop.close()
            except Exception as e:
                # show error message
                print(e)
        obj.save()

    # filter query set by user
    def get_queryset(self, request):
        qs = super(TelegramWorkerAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)


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


class ContactAdmin(admin.ModelAdmin):
    change_list_template = "telegram_save_contact_changelist.html"
    list_display = ('phone_number', 'username', 'worker', 'has_telegram')
    list_filter = ('worker', 'has_telegram')

    def save_model(self, request, obj, form, change):
        if not change:
            workers = TelegramWorker.objects.filter(
                Q(is_active=True) & Q(add_contact_today__lt=100) & Q(user=request.user) & (
                        ~Q(baned_until__gte=datetime.datetime.utcnow()) | Q(baned_until=None)))
            if workers:
                worker_count = Contact.objects.values('worker').annotate(count=Count('worker')).order_by('count')
                if worker_count:
                    least_used_worker_id = worker_count.first()['worker']
                    least_used_worker = TelegramWorker.objects.get(pk=least_used_worker_id)
                else:
                    least_used_worker = workers.first()
                obj.worker = least_used_worker

                try:
                    least_used_worker.is_working = True
                    least_used_worker.save()
                    res = asyncio.run(save_contact_to_telegram(obj.phone_number, least_used_worker))
                    if res:
                        obj.username = res.users[0].username
                        obj.save()

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


admin.site.register(TelegramWorker, TelegramWorkerAdmin)
admin.site.register(Contact, ContactAdmin)
