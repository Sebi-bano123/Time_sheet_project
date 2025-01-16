
from django.contrib import admin
from .models import Role, UserRole, Company, Employee, TimeSheet, Team

# Admin configuration for the Role model
@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)
    list_filter = ('name',)  # Add filtering by name

# Admin configuration for the UserRole model
@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'company')  # Display company for context
    search_fields = ('user__username', 'role__name', 'company__name')  # Enable search by user, role, and company
    list_filter = ('role', 'company')  # Add filtering by role and company

# Admin configuration for the Company model
@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'action')
    search_fields = ('name',)
    list_filter = ('action',)  # Filter by action type

# Admin configuration for the Employee model
@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('name', 'vid', 'email', 'manager_email', 'company')  # Include company in the display
    search_fields = ('name', 'vid', 'email', 'manager_email', 'company__name')  # Search by company name too
    list_filter = ('company',)  # Add filtering by company



from django.contrib import admin
from .models import TimeSheet

@admin.register(TimeSheet)
class TimeSheetAdmin(admin.ModelAdmin):
    list_display = ('employee_name', 'employee_vid', 'date', 'day', 'time_in', 'time_out', 'mode_of_work', 'sub_status', 'approved_status')
    list_filter = ('day', 'mode_of_work', 'sub_status', 'approved_status', 'date')
    search_fields = ('employee__name', 'employee__vid')

    def employee_name(self, obj):
        return obj.employee.name
    employee_name.short_description = 'Employee Name'

    def employee_vid(self, obj):
        return obj.employee.vid
    employee_vid.short_description = 'Employee VID'

    # Custom formatting for time_in and time_out
    def time_in(self, obj):
        return obj.time_in.strftime('%I:%M %p')  # Format as '9:00 AM'
    time_in.short_description = 'Time In'

    def time_out(self, obj):
        return obj.time_out.strftime('%I:%M %p')  # Format as '6:00 PM'
    time_out.short_description = 'Time Out'


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('employee_name', 'employee_vid', 'date', 'sub_status') 
    list_filter = ('sub_status', 'date')  
    search_fields = ('employee__name', 'employee__vid')  

   
    def employee_name(self, obj):
        return obj.employee.name
    employee_name.short_description = 'Employee Name'

    def employee_vid(self, obj):
        return obj.employee.vid
    employee_vid.short_description = 'Employee VID'




from django.contrib import admin
from .models import EmployeeData

# Register the EmployeeData model
@admin.register(EmployeeData)
class EmployeeDataAdmin(admin.ModelAdmin):
    list_display = (
        'employee_number', 
        'employee_name', 
        'job_title', 
        'business_unit', 
        'department', 
        'location', 
        'date', 
        'status'
    )
    list_filter = ('business_unit', 'department', 'status', 'date')
    search_fields = ('employee_number', 'employee_name', 'job_title', 'department', 'reporting_manager')
    ordering = ('-date',)
