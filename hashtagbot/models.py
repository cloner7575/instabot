from django.db import models

# Create your models here.


class Worker(models.Model):
    username = models.CharField(max_length=100, verbose_name='نام کاربری')
    password = models.CharField(max_length=100, verbose_name='رمز عبور')
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    is_working = models.BooleanField(default=False, verbose_name='در حال کار')
    user = models.ForeignKey('auth.User', on_delete=models.DO_NOTHING, null=True, verbose_name='کاربر')

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = 'کارگر'
        verbose_name_plural = 'کارگران'


class AccountInfo(models.Model):
    username = models.CharField(max_length=100, verbose_name='نام کاربری')
    phone_number = models.CharField(max_length=100,verbose_name='شماره تلفن')
    from_tag = models.CharField(max_length=100,verbose_name='هشتگ')
    is_business = models.BooleanField(default=False, verbose_name='اکانت کسب و کار')
    other_info = models.TextField(verbose_name='اطلاعات دیگر')
    is_checked = models.BooleanField(default=False,verbose_name='بررسی شده')
    user = models.ForeignKey('auth.User', on_delete=models.DO_NOTHING, null=True,verbose_name='کاربر')


    def __str__(self):
        return self.username

    class Meta:
        verbose_name = 'اکانت'
        verbose_name_plural = 'اکانت ها'


