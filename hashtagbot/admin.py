from django import forms
from django.contrib import admin
from django.http import HttpResponse
from django.template.context_processors import csrf
from django.urls import reverse
from django.utils.html import format_html
from instagrapi import Client
from openpyxl.workbook import Workbook

# Register your models here.

from .models import Worker, AccountInfo


class WorkerAdmin(admin.ModelAdmin):
    list_display = ('username', 'is_active', 'is_working')
    list_filter = ('is_active', 'is_working')
    readonly_fields = ('user',)

    def save_model(self, request, obj, form, change):
        if not change:
            obj.user = request.user
            cl = Client()
            cl.login(obj.username, obj.password)


        obj.save()

    # filter query set by user
    def get_queryset(self, request):
        qs = super(WorkerAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)


class AccountInfoAdmin(admin.ModelAdmin):
    change_list_template = "change_list.html"
    list_display = ('username', 'phone_number', 'from_tag', 'is_business', 'is_checked')
    list_filter = ('is_business', 'is_checked')
    readonly_fields = ('user',)

    def save_model(self, request, obj, form, change):
        if not change:
            obj.user = request.user
        obj.save()

    # filter query set by user
    def get_queryset(self, request):
        qs = super(AccountInfoAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)

    def export_to_excel(self, request, queryset):
        # ساخت فایل اکسل
        wb = Workbook()
        ws = wb.active

        # افزودن ستون‌ها
        ws['A1'] = 'نام'
        ws['B1'] = 'شماره'

        # افزودن داده‌ها
        for obj in queryset:
            if obj.is_business:
                row = [obj.username, obj.phone_number]
                ws.append(row)


        # نام فایل اکسل
        filename = 'my_data.xlsx'

        # ذخیره فایل اکسل
        wb.save(filename)

        # ارسال فایل به کاربر
        with open(filename, 'rb') as f:
            response = HttpResponse(f.read(),
                                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = f'attachment; filename={filename}'
            return response







admin.site.register(Worker, WorkerAdmin)
admin.site.register(AccountInfo, AccountInfoAdmin)


admin.site.site_header = "نئون پدیا"
admin.site.site_title = "نئون پدیا"
admin.site.index_title = "پنل مدیریت ربات اینستاگرام"



