from django.contrib import admin
from .models import Department, Doctor, Patient, Appointment, Medicine, Prescription, PrescriptionMedicine, Bill


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['name']


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'department', 'specialization', 'experience', 'is_available']
    list_filter = ['department', 'is_available']
    search_fields = ['user__first_name', 'user__last_name', 'specialization']


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'age', 'gender', 'blood_group']
    list_filter = ['gender', 'blood_group']
    search_fields = ['user__first_name', 'user__last_name']


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['id', 'patient', 'doctor', 'appointment_date', 'status', 'created_at']
    list_filter = ['status', 'appointment_date']
    search_fields = ['patient__user__first_name', 'doctor__user__first_name']


@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'unit']
    search_fields = ['name']


class PrescriptionMedicineInline(admin.TabularInline):
    model = PrescriptionMedicine
    extra = 1


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ['id', 'appointment', 'created_at']
    inlines = [PrescriptionMedicineInline]


@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    list_display = ['id', 'patient', 'amount', 'paid', 'created_at']
    list_filter = ['paid']
    search_fields = ['patient__user__first_name']
