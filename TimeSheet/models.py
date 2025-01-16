from django.db import models
from django.contrib.auth.models import User
from datetime import date
from datetime import datetime
from datetime import datetime, time



from django.db import models
from django.contrib.auth.models import User


class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Company(models.Model):
    name = models.CharField(max_length=255)
    action = models.CharField(max_length=255, default="Open Time Sheet")

    def __str__(self):
        return self.name


class UserRole(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True)  

    def __str__(self):
        role_name = self.role.name if self.role else 'No Role'
        company_name = self.company.name if self.company else 'No Company'
        return f"{self.user.username} - {role_name} - {company_name}"
        
class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, default=None)
    name = models.CharField(max_length=255)
    vid = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    manager_email = models.EmailField()

    def __str__(self):
        return f"{self.name} ({self.company.name if self.company else 'No Company'})"


def default_time_in():
    return datetime.combine(date.today(), time(9, 30))  # Default time is 9:30 AM

def default_time_out():
    return datetime.combine(date.today(), time(18, 30))  # Default time is 6:30 PM


class TimeSheet(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)  
    date = models.DateField(default=date.today)  
    day = models.CharField(
        max_length=50,
        choices=[
            ('Holiday', 'Holiday'),
            ('Weekday', 'Weekday'),
            ('Weekend', 'Weekend'),
        ],
        default='Weekday'
    )
    time_in = models.DateTimeField(default=default_time_in)  # Reference the standalone function
    time_out = models.DateTimeField(default=default_time_out)  # Reference the standalone function
    mode_of_work = models.CharField(
        max_length=50,
        choices=[
            ('work-from-home', 'Work-from-home'),
            ('work-from-office', 'Work-from-office'),
        ],
        default='work-from-office' 
    )
    
    sub_status = models.CharField(
        max_length=55,
        choices=[
            ('working', 'Working'),
            ('On Leave', 'On Leave'),
        ],
        default='Present'
    )

    approved_status = models.CharField(  
        max_length=50,
        choices=[
            ('Pending', 'Pending'),
            ('Approved', 'Approved'),
            ('Rejected', 'Rejected'),
        ],
        default='Pending'
    )

    def __str__(self):
        return f"{self.employee.name} - {self.date} ({self.day})"





class Team(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)  # Link to Employee
    date = models.DateField(default=date.today)  # Date for the record
    sub_status = models.CharField(
        max_length=55,
        choices=[
            ('Approved Pending', 'Approved Pending'),
            ('Approved', 'Approved'),
            ('Rejected', 'Rejected'),
        ],
        default='Approved Pending'
    )

    def __str__(self):
        return f"{self.employee.name} ({self.employee.vid}) - {self.sub_status}"
    



from django.db import models

class EmployeeData(models.Model):
    employee_number = models.CharField(max_length=10)  # Employee ID
    employee_name = models.CharField(max_length=100)  # Employee Name
    job_title = models.CharField(max_length=100)
    business_unit = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    sub_department = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    cost_center = models.CharField(max_length=50)
    reporting_manager = models.CharField(max_length=100)
    date = models.DateField()  # Date of the record
    shift = models.CharField(max_length=50)
    shift_start = models.TimeField()  # Shift Start Time
    shift_end = models.TimeField()  # Shift End Time
    in_time = models.TimeField(null=True, blank=True)  # Actual In Time
    out_time = models.TimeField(null=True, blank=True)  # Actual Out Time
    late_by = models.DurationField(null=True, blank=True)  # Late by (e.g., 00:08)
    early_by = models.DurationField(null=True, blank=True)  # Early by duration
    status = models.CharField(max_length=50)  # Status (e.g., H, P, WO) Work mode (WFO, WFH)
    effective_hours = models.DurationField(null=True, blank=True)  # Effective hours worked
    total_hours = models.DurationField(null=True, blank=True)  # Total hours
    break_duration = models.DurationField(null=True, blank=True)  # Break duration
    over_time = models.DurationField(null=True, blank=True)  # Overtime hours
    total_short_hours_effective = models.DurationField(null=True, blank=True)  # Total short hours (effective)
    total_short_hours_gross = models.DurationField(null=True, blank=True)  # Total short hours (gross)
    
    def __str__(self):
        return f"{self.employee_name} - {self.date}"




