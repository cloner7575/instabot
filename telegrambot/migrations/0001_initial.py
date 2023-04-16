# Generated by Django 4.2 on 2023-04-14 18:12

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="TelegramWorker",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("api_id", models.CharField(max_length=100, verbose_name="api_id")),
                ("api_hash", models.CharField(max_length=100, verbose_name="api_hash")),
                (
                    "session_name",
                    models.CharField(max_length=100, verbose_name="نام سشن"),
                ),
                ("is_active", models.BooleanField(default=False, verbose_name="فعال")),
                (
                    "is_working",
                    models.BooleanField(default=False, verbose_name="در حال کار"),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="کاربر",
                    ),
                ),
            ],
            options={
                "verbose_name": "کارگر",
                "verbose_name_plural": "کارگران",
            },
        ),
        migrations.CreateModel(
            name="Contact",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "username",
                    models.CharField(
                        blank=True, max_length=100, null=True, verbose_name="نام کاربری"
                    ),
                ),
                (
                    "phone_number",
                    models.CharField(
                        blank=True, max_length=100, null=True, verbose_name="شماره تماس"
                    ),
                ),
                (
                    "worker",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        to="telegrambot.telegramworker",
                        verbose_name="کارگر",
                    ),
                ),
            ],
        ),
    ]