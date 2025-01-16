from django.urls import path
from . import views
from .views import TimeSheetView

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('signin/', views.signin, name='signin'),
    path('companies/', views.company_list, name='company_list'),
    # path('invite-employee/', views.invite_employee, name='invite_employee'),
    path('time-sheet/', TimeSheetView.as_view(), name='time-sheet'),
    path('teams/', views.team_api_view, name='team_api'),
    path('upload_excel/', views.upload_excel, name=' upload_excel'),
    path('status-time-sheet/<int:company_id>/', views.status_time_sheet, name='status_time_sheet'),

    path('invite-employee/<int:company_id>/', views.invite_employee, name='invite_employee'),
    path('invite-employee/<int:company_id>/employee/<int:employee_id>/', views.invite_employee, name='get_employee'),
    path('invite-employee/<int:company_id>/employees/', views.invite_employee, name='get_all_employees'),
    path('invite-employee/<int:company_id>/employee/<int:employee_id>/', views.invite_employee, name='update_employee'),
    path('invite-employee/<int:company_id>/employee/<int:employee_id>/', views.invite_employee, name='delete_employee')


]
