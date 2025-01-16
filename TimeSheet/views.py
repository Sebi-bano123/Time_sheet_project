import json
import secrets
from django.core.mail import send_mail
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from .models import Role, UserRole
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.conf import settings
from .decorator import login_required, role_required
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from .models import Employee, Team
import jwt
from django.views import View
from django.shortcuts import get_object_or_404
import calendar
from datetime import datetime
from .models import Company, Employee, TimeSheet
import pandas as pd
from django.shortcuts import render
from .models import EmployeeData





@csrf_exempt
def signup(request):
    if request.method == 'POST':
        try:
            roles = ['manager', 'employee', 'admin']
            data = json.loads(request.body.decode('utf-8'))
            username = data.get('username')
            email = data.get('email')
            password = data.get('password')
            role_name = data.get('role', '').strip().lower()  

            
            if not username or not email or not password:
                return JsonResponse({'error': 'All fields are required'}, status=400)

           
            try:
                validate_email(email)
            except ValidationError:
                return JsonResponse({'error': 'Invalid email format'}, status=400)

            # Check if username or email already exists
            if User.objects.filter(username=username).exists():
                return JsonResponse({'error': 'Username already exists'}, status=400)
            if User.objects.filter(email=email).exists():
                return JsonResponse({'error': 'Email already registered'}, status=400)

           
            if role_name == '':  
                role_name = 'user'
            elif role_name not in roles:  
                return JsonResponse({'error': 'Invalid role name'}, status=400)

          
            user = User.objects.create_user(username=username, email=email, password=password)

           
            role, _ = Role.objects.get_or_create(name=role_name)
            UserRole.objects.create(user=user, role=role)

            return JsonResponse({'message': f'User with role {role_name.capitalize()} created successfully'}, status=201)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=405)



@csrf_exempt
def signin(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            email = data.get('email')
            password = data.get('password')

           
            if not email or not password:
                return JsonResponse({'error': 'Email and password are required'}, status=400)

           
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return JsonResponse({'error': 'Invalid email or password'}, status=401)

            
            user = authenticate(username=user.username, password=password)
            if user is not None:

                
                user_role = UserRole.objects.filter(user=user).first()
                role_name = user_role.role.name if user_role else 'No role assigned'
                payload = {
                    'user_id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'role': role_name,
                    # 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1) 
                }
                token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

                return JsonResponse({
                    'message': 'Login successful',
                    'role': role_name,
                    'token': token
                }, status=200)

            return JsonResponse({'error': 'Invalid email or password'}, status=401)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=405)






@csrf_exempt
@login_required
@role_required(['admin'])
def company_list(request):
    if request.method == 'GET':
        companies = list(Company.objects.values())
        return JsonResponse({"companies": companies}, status=200)

    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            name = data.get('name')
            action = data.get('action', 'Open Time Sheet')
            if not name:
                return JsonResponse({"error": "Name is required"}, status=400)
            company = Company.objects.create(name=name, action=action)
            return JsonResponse({"id": company.id, "message": "Company created successfully"}, status=201)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

    elif request.method == 'PUT':
        try:
            data = json.loads(request.body)
            company_id = data.get('id')
            name = data.get('name')
            action = data.get('action')

            if not company_id or not name:
                return JsonResponse({"error": "ID and Name are required"}, status=400)

            try:
                company = Company.objects.get(id=company_id)
                company.name = name
                company.action = action if action else company.action
                company.save()
                return JsonResponse({"message": "Company updated successfully"}, status=200)
            except Company.DoesNotExist:
                return JsonResponse({"error": "Company not found"}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

    elif request.method == 'DELETE':
        try:
            data = json.loads(request.body)
            company_id = data.get('id')
            if not company_id:
                return JsonResponse({"error": "ID is required"}, status=400)

            try:
                company = Company.objects.get(id=company_id)
                company.delete()
                return JsonResponse({"message": "Company deleted successfully"}, status=200)
            except Company.DoesNotExist:
                return JsonResponse({"error": "Company not found"}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

    return JsonResponse({"error": "Invalid request method"}, status=405)



@csrf_exempt
def invite_employee(request, company_id=None, employee_id=None):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            name = data.get('name')
            vid = data.get('vid')
            email = data.get('email')
            manager_email = data.get('manager_email')
            role_name = data.get('role', 'user')  # Default role is 'user'
            password = secrets.token_urlsafe(4)

            # Validate required fields
            if not all([name, vid, email, manager_email]):
                return JsonResponse({'error': 'Name, VID, email, and manager email are required'}, status=400)

            # Validate email format
            try:
                validate_email(email)
            except ValidationError:
                return JsonResponse({'error': 'Invalid email format'}, status=400)

            # Ensure the company exists or get the first company if not provided
            if not company_id:
                company = Company.objects.all().first()  # Get the first company if no company_id is provided
                if not company:
                    return JsonResponse({'error': 'No company found'}, status=400)
            else:
                company = get_object_or_404(Company, id=company_id)

            # Check if email is already in use (for new users)
            if not employee_id and Employee.objects.filter(email=email).exists():
                return JsonResponse({'error': 'Email is already associated with an employee'}, status=400)

            if employee_id:
                # Update existing employee if employee_id is provided
                employee = get_object_or_404(Employee, id=employee_id)
                user = employee.user
                user.email = email
                user.save()
                employee.name = name
                employee.vid = vid
                employee.manager_email = manager_email
                employee.save()
                return JsonResponse({'message': 'Employee updated successfully'}, status=200)
            else:
                # Create new user if no employee_id is provided
                user = User.objects.create_user(username=name, email=email, password=password)
                role, _ = Role.objects.get_or_create(name=role_name)
                UserRole.objects.create(user=user, role=role, company=company)

                # Create employee record with the selected company
                Employee.objects.create(
                    user=user,
                    company=company,
                    name=name,
                    vid=vid,
                    email=email,
                    manager_email=manager_email,
                )

                # Send invitation email
                send_mail(
                    'Your Employee Invitation',
                    f"""
                    Dear {name},

                    You have been invited to join {company.name}.
                    Your login details:
                    Username: {email}
                    Password: {password}

                    Please log in and change your password immediately.

                    Regards,
                    Admin Team
                    """,
                    'admin@example.com',
                    [email],
                    fail_silently=False,
                )

                return JsonResponse({'message': 'Employee invited successfully'}, status=201)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    elif request.method == 'GET':
        try:
            if employee_id:
                # Get specific employee
                employee = get_object_or_404(Employee, id=employee_id)
                data = {
                    'id': employee.id,
                    'name': employee.name,
                    'vid': employee.vid,
                    'email': employee.email,
                    'manager_email': employee.manager_email,
                    'company': employee.company.name,
                }
                return JsonResponse(data, status=200)
            else:
                # Get all employees for a specific company or all employees
                employees = Employee.objects.filter(company__id=company_id) if company_id else Employee.objects.all()
                employee_list = [
                    {
                        'id': emp.id,
                        'name': emp.name,
                        'vid': emp.vid,
                        'email': emp.email,
                        'manager_email': emp.manager_email,
                        'company': emp.company.name,
                    }
                    for emp in employees
                ]
                return JsonResponse(employee_list, safe=False, status=200)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    elif request.method == 'PUT':
        try:
            if not employee_id:
                return JsonResponse({'error': 'Employee ID is required for updating'}, status=400)

            data = json.loads(request.body)
            name = data.get('name')
            vid = data.get('vid')
            email = data.get('email')
            manager_email = data.get('manager_email')

            # Validate required fields
            if not all([name, vid, email, manager_email]):
                return JsonResponse({'error': 'All fields are required'}, status=400)

            employee = get_object_or_404(Employee, id=employee_id)

            # Update employee details
            employee.name = name
            employee.vid = vid
            employee.email = email
            employee.manager_email = manager_email
            employee.save()

            return JsonResponse({'message': 'Employee updated successfully'}, status=200)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    elif request.method == 'DELETE':
        try:
            if not employee_id:
                return JsonResponse({'error': 'Employee ID is required for deletion'}, status=400)

            employee = Employee.objects.filter(id=employee_id, company_id=company_id).first()
            if not employee:
                return JsonResponse({'error': 'No employee found for the given company and employee ID'}, status=404)

            user = employee.user

            employee.delete()
            user.delete()

            return JsonResponse({'message': 'Employee deleted successfully'}, status=200)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)






@method_decorator([csrf_exempt, login_required, role_required(['user'])], name='dispatch')
class TimeSheetView(View):
    def get(self, request, year=None, month=None):
        try:
            # Fetch user from the request, as it's already attached by the decorator
            user = request.user

            # Fetch the employee object related to the user
            employee = get_object_or_404(Employee, user=user)

            # Try to fetch the manager based on the manager_email
            try:
                manager = User.objects.get(email=employee.manager_email)
                manager_name = manager.username  # Or other manager details like manager.full_name
            except User.DoesNotExist:
                manager_name = "No Manager"  # If manager doesn't exist

            # If year or month is not provided, get the current year and month
            if not year or not month:
                year = datetime.now().year  # Current year
                month = datetime.now().month  # Current month

            # Get the first and last day of the given month
            _, last_day = calendar.monthrange(year, month)
            first_date = f"{year}-{month:02d}-01"  # First day of the month
            last_date = f"{year}-{month:02d}-{last_day:02d}"  # Last day of the month

            # Fetch timesheets for the employee for the entire month
            time_sheets = TimeSheet.objects.filter(
                employee=employee,
                date__gte=first_date,
                date__lte=last_date
            )

            # Map timesheets to their corresponding dates
            timesheet_map = {ts.date: ts for ts in time_sheets}

            # Generate a list of all the days in the month
            all_dates = [f"{year}-{month:02d}-{day:02d}" for day in range(1, last_day + 1)]

            fixed_time_in = "09:30:00"
            fixed_time_out = "06:30:00"

            # Serialize timesheet data
            user_data = {
                'V-ID': employee.vid,
                'Name': employee.name,
                'Reporting Manager': manager_name
            }

            timesheet_data = [
                {
                    # Format the date as per requirement (e.g., Tue, 1/Jan/25)
                    'Date': datetime.strptime(date, '%Y-%m-%d').strftime('%a, %d/%b/%y'),
                    'Day': 'Weekday' if calendar.weekday(year, month, int(date.split('-')[-1])) < 5 else 'Weekend',
                    'Time In': fixed_time_in,
                    'Time Out': fixed_time_out,
                    'Mode of Work': timesheet_map.get(date).mode_of_work if timesheet_map.get(date) else 'Work-from-office',
                    'Sub-Status': timesheet_map.get(date).sub_status if timesheet_map.get(date) else 'Working',
                    'Approval Status': timesheet_map.get(date).approved_status if timesheet_map.get(date) else 'Pending',
                }
                for date in all_dates
            ]

            response_data = {
                "user_data": user_data,
                "timesheet": timesheet_data
            }

            return JsonResponse({'time_sheet': response_data}, status=200)

        except Exception as e:
            return JsonResponse({'error': f'Unexpected error: {str(e)}'}, status=500)



# The JWT token secret, should match the secret in your Django settings
JWT_SECRET = settings.SECRET_KEY

@csrf_exempt
def team_api_view(request):
    if request.method == 'GET':
        
        token = request.headers.get('Authorization')

        if not token:
            return JsonResponse({"error": "Authorization token missing"}, status=400)

        token = token.split(' ')[1]  

        try:
            
            payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            user_email = payload['email']  # Assuming 'email' is part of the payload

            # Fetch the logged-in user
            try:
                user = get_user_model().objects.get(email=user_email)
            except get_user_model().DoesNotExist:
                return JsonResponse({"error": "User not found"}, status=404) 

           
            managed_employees = Employee.objects.filter(manager_email=user.email)

           
            team_data = Team.objects.filter(employee__in=managed_employees)

          
            response_data = []
            for team in team_data:
                response_data.append({
                    "vid": team.employee.vid,
                    "name": team.employee.name,
                    "date": team.date.strftime('%Y-%m-%d'),
                    "sub_status": team.sub_status
                })

            return JsonResponse(response_data, safe=False)

        except jwt.ExpiredSignatureError:
            return JsonResponse({"error": "Token has expired"}, status=401)
        except jwt.InvalidTokenError:
            return JsonResponse({"error": "Invalid token"}, status=401)





@csrf_exempt
@login_required
@role_required(['admin'])
def upload_excel(request):
    try:
        if request.method == 'POST' and request.FILES.get('excel_file'):
            excel_file = request.FILES['excel_file']
            df = pd.read_excel(excel_file, skiprows=2)

            # Set column names
            df.columns = [
                'Employee Number', 'Employee Name', 'Job Title', 'Business Unit', 'Department',
                'Sub Department', 'Location', 'Cost Center', 'Reporting Manager', 'Date', 'Shift',
                'Shift Start', 'Shift End', 'In Time', 'Out Time', 'Late By', 'Early By', 'Status',
                'Effective Hours', 'Total Hours', 'Break Duration', 'Over Time',
                'Total Short Hours (Effective)', 'Total Short Hours (Gross)'
            ]

            def format_timedelta(time_string):
                """
                Converts a time-like string (e.g., "0:00", "09:00") into "HH:MM:SS" format.
                Handles invalid formats and replaces invalid data with "00:00:00".
                """
                try:
                    if not time_string or pd.isna(time_string):
                        return "00:00:00"
                    
                    
                    time_string = time_string.replace(".", ":")
                    
                   
                    parts = time_string.split(":")
                    if len(parts) == 2: 
                        hours, minutes = int(parts[0]), int(parts[1])
                    elif len(parts) == 1:  
                        hours, minutes = 0, int(parts[0])
                    else:
                        raise ValueError(f"Invalid time format: {time_string}")
                    return f"{hours:02}:{minutes:02}:00"
                except Exception as e:
                    print(f"Error formatting time string '{time_string}': {e}")
                    return "00:00:00"

            for _, row in df.iterrows():
                try:
                    
                    date = pd.to_datetime(row['Date'], errors='coerce').date() if not pd.isna(row['Date']) else None
                    
                  
                    shift_start = pd.to_datetime(row['Shift Start'], format='%H:%M', errors='coerce').time() if not pd.isna(row['Shift Start']) else None
                    shift_end = pd.to_datetime(row['Shift End'], format='%H:%M', errors='coerce').time() if not pd.isna(row['Shift End']) else None
                    in_time = pd.to_datetime(row['In Time'], format='%H:%M', errors='coerce').time() if not pd.isna(row['In Time']) else None
                    out_time = pd.to_datetime(row['Out Time'], format='%H:%M', errors='coerce').time() if not pd.isna(row['Out Time']) else None

                    if shift_end is None:
                        shift_end = pd.to_datetime("00:00", format='%H:%M').time() 

                   
                    late_by = pd.to_timedelta(format_timedelta(row['Late By']), errors='coerce') if not pd.isna(row['Late By']) else None
                    early_by = pd.to_timedelta(format_timedelta(row['Early By']), errors='coerce') if not pd.isna(row['Early By']) else None
                    effective_hours = pd.to_timedelta(format_timedelta(row['Effective Hours']), errors='coerce') if not pd.isna(row['Effective Hours']) else None
                    total_hours = pd.to_timedelta(format_timedelta(row['Total Hours']), errors='coerce') if not pd.isna(row['Total Hours']) else None
                    break_duration = pd.to_timedelta(format_timedelta(row['Break Duration']), errors='coerce') if not pd.isna(row['Break Duration']) else None
                    over_time = pd.to_timedelta(format_timedelta(row['Over Time']), errors='coerce') if not pd.isna(row['Over Time']) else None
                    total_short_hours_effective = pd.to_timedelta(format_timedelta(row['Total Short Hours (Effective)']), errors='coerce') if not pd.isna(row['Total Short Hours (Effective)']) else None
                    total_short_hours_gross = pd.to_timedelta(format_timedelta(row['Total Short Hours (Gross)']), errors='coerce') if not pd.isna(row['Total Short Hours (Gross)']) else None

                   
                    print("=== Processed data: ", {
                        "late_by": late_by,
                        "early_by": early_by,
                        "effective_hours": effective_hours,
                        "total_hours": total_hours,
                        "break_duration": break_duration,
                        "over_time": over_time,
                        "total_short_hours_effective": total_short_hours_effective,
                        "total_short_hours_gross": total_short_hours_gross,
                    })

                    
                    EmployeeData.objects.create(
                                    employee_number=row['Employee Number'],
                                    employee_name=row['Employee Name'],
                                    job_title=row['Job Title'],
                                    business_unit=row['Business Unit'],
                                    department=row['Department'],
                                    sub_department=row['Sub Department'] if not pd.isna(row['Sub Department']) else 'Not Assigned', 
                                    location=row['Location'],
                                    cost_center=row['Cost Center'],
                                    reporting_manager=row['Reporting Manager'],
                                    date=date,
                                    shift=row['Shift'],
                                    shift_start=shift_start,
                                    shift_end=shift_end,
                                    in_time=in_time,
                                    out_time=out_time,
                                    late_by=late_by,
                                    early_by=early_by,
                                    status=row['Status'],
                                    effective_hours=effective_hours,
                                    total_hours=total_hours,
                                    break_duration=break_duration,
                                    over_time=over_time,
                                    total_short_hours_effective=total_short_hours_effective,
                                    total_short_hours_gross=total_short_hours_gross,
                                )
                    print(f"Successfully inserted data for Employee {row['Employee Number']}")
                except Exception as e:
                    print(f"Error processing row {row.to_dict()}: {e}")
                    continue

            return JsonResponse({'message': 'Excel data uploaded successfully!'})

        return render(request, 'upload_excel.html')

    except Exception as e:
        print(f"An error occurred: {e}")
        return JsonResponse({'error': f'An error occurred: {e}'}, status=500)





@csrf_exempt
@login_required
@role_required(['admin'])
def status_time_sheet(request, company_id):
    print(f"Authenticated user: {request.user}")

    if request.method == 'GET':
        try:
            # Fetch the company by ID
            company = Company.objects.get(id=company_id)
            print(f"Company found: {company.name}")

            # Fetch employees linked to the company through UserRole
            employees = Employee.objects.filter(user__userrole__company=company)
            print(f"Employees found: {employees.count()}")

            if not employees.exists():
                return JsonResponse({"message": "No employees registered for this company."}, status=200)

            # Prepare the data for the response
            time_sheet_data = []
            for employee in employees:
                # Fetch the latest time sheet entry for each employee
                time_sheets = TimeSheet.objects.filter(employee=employee)
                for sheet in time_sheets:
                    time_sheet_data.append({
                        "vid": employee.vid,
                        "name": employee.name,
                        "date": sheet.date.strftime('%d/%b/%Y'),
                        "sub_status": sheet.approved_status
                    })

            return JsonResponse({"company": company.name, "time_sheets": time_sheet_data}, status=200)

        except Company.DoesNotExist:
            return JsonResponse({"error": "Company not found."}, status=404)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid HTTP method."}, status=400)
