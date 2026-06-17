import django_filters
from .models import Appointment, Doctor, Patient


class AppointmentFilter(django_filters.FilterSet):
    date = django_filters.DateFilter(field_name='appointment_date', lookup_expr='date')
    date_from = django_filters.DateFilter(field_name='appointment_date', lookup_expr='date__gte')
    date_to = django_filters.DateFilter(field_name='appointment_date', lookup_expr='date__lte')

    class Meta:
        model = Appointment
        fields = ['doctor', 'patient', 'status', 'date', 'date_from', 'date_to']


class DoctorFilter(django_filters.FilterSet):
    class Meta:
        model = Doctor
        fields = ['department', 'is_available']
