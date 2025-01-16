from rest_framework import serializers
from .models import Employee, TimeSheet

class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = '__all__'

class TimeSheetSerializer(serializers.ModelSerializer):
    employee = EmployeeSerializer()  # Nest employee data in the response

    class Meta:
        model = TimeSheet
        fields = '__all__'
