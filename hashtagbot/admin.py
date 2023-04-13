from django import forms
from django.contrib import admin
from django.template.context_processors import csrf
from django.urls import reverse
from django.utils.html import format_html

# Register your models here.

from .models import Worker, AccountInfo


class WorkerAdmin(admin.ModelAdmin):
    list_display = ('username', 'is_active', 'is_working')
    list_filter = ('is_active', 'is_working')
    readonly_fields = ('user',)

    def save_model(self, request, obj, form, change):
        if not change:
            obj.user = request.user
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







admin.site.register(Worker, WorkerAdmin)
admin.site.register(AccountInfo, AccountInfoAdmin)


admin.site.site_header = "نئون پدیا"
admin.site.site_title = "نئون پدیا"
admin.site.index_title = "پنل مدیریت ربات اینستاگرام"



