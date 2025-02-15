# Generated by Django 5.1.4 on 2025-01-08 07:13

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('TimeSheet', '0008_remove_employee_manager_employee_manager_email'),
    ]

    operations = [
        migrations.AlterField(
            model_name='timesheet',
            name='date',
            field=models.DateField(default=datetime.date.today),
        ),
        migrations.AlterField(
            model_name='timesheet',
            name='mode_of_work',
            field=models.CharField(choices=[('work-form-home', 'work-form-home'), ('work-from-Office', 'work-from-Office')], default='work-from-Office', max_length=50),
        ),
        migrations.AlterField(
            model_name='timesheet',
            name='status',
            field=models.CharField(choices=[('Holiday', 'Holiday'), ('Weekday', 'Weekday'), ('weekend', 'weekend')], default='Weekday', max_length=50),
        ),
    ]
