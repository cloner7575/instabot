from django.db import models
import pandas as pd

# Create your models here.


class TelegramWorker(models.Model):
    api_id = models.CharField(max_length=100, verbose_name='api_id')
    api_hash = models.CharField(max_length=100, verbose_name='api_hash')
    session_name = models.CharField(max_length=100, verbose_name='نام سشن')
    user = models.ForeignKey('auth.User', on_delete=models.DO_NOTHING, verbose_name='کاربر')
    is_active = models.BooleanField(default=False, verbose_name='فعال')
    is_working = models.BooleanField(default=False, verbose_name='در حال کار')
    baned_until = models.DateTimeField(null=True, blank=True, verbose_name='محرومیت تا')
    add_contact_today = models.IntegerField(default=0, verbose_name='مخاطب اضافه شده امروز')
    message_sent_today = models.IntegerField(default=0, verbose_name='پیام ارسال شده امروز')

    def __str__(self):
        return self.session_name

    class Meta:
        verbose_name = 'کارگر'
        verbose_name_plural = 'کارگران'


class Contact(models.Model):
    phone_number = models.CharField(max_length=100, verbose_name='شماره تماس',null=True, blank=True)
    username = models.CharField(max_length=100, verbose_name='نام کاربری', null=True, blank=True)
    has_telegram = models.BooleanField(default=False, verbose_name='دارای تلگرام')


    worker = models.ForeignKey(TelegramWorker, on_delete=models.DO_NOTHING, verbose_name='کارگر')

    def __str__(self):
        return self.phone_number

    class Meta:
        verbose_name = 'مخاطب'
        verbose_name_plural = 'مخاطبین'
