# Generated by Django 5.1.4 on 2025-01-14 19:32

import TimeSheet.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('TimeSheet', '0013_remove_timesheet_status_timesheet_day_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='timesheet',
            name='remarks',
        ),
        migrations.RemoveField(
            model_name='timesheet',
            name='shift_out',
        ),
        migrations.RemoveField(
            model_name='timesheet',
            name='shift_time',
        ),
        migrations.AddField(
            model_name='timesheet',
            name='approved_status',
            field=models.CharField(choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected')], default='Pending', max_length=50),
        ),
        migrations.AddField(
            model_name='timesheet',
            name='time_in',
            field=models.DateTimeField(default=TimeSheet.models.default_time_in),
        ),
        migrations.AddField(
            model_name='timesheet',
            name='time_out',
            field=models.DateTimeField(default=TimeSheet.models.default_time_out),
        ),
    ]
