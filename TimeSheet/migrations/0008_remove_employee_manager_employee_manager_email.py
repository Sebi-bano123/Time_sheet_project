# Generated by Django 5.1.4 on 2025-01-08 06:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('TimeSheet', '0007_remove_employee_manager_email_employee_manager_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='employee',
            name='manager',
        ),
        migrations.AddField(
            model_name='employee',
            name='manager_email',
            field=models.EmailField(default='no_manager@example.com', max_length=254),
            preserve_default=False,
        ),
    ]
