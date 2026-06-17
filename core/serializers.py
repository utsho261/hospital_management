from rest_framework import serializers
from .models import (
    Department, Doctor, Patient, Appointment,
    Medicine, Prescription, PrescriptionMedicine, Bill,
)
from accounts.models import User
from accounts.serializers import UserSerializer


# ────── Department ──────
class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'


# ────── Doctor ──────
class DoctorSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='user', write_only=True
    )
    department_name = serializers.CharField(source='department.name', read_only=True)

    class Meta:
        model = Doctor
        fields = ['id', 'user', 'user_id', 'department', 'department_name',
                  'specialization', 'phone', 'experience', 'is_available']


# ────── Patient ──────
class PatientSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='user', write_only=True
    )

    class Meta:
        model = Patient
        fields = ['id', 'user', 'user_id', 'age', 'gender',
                  'blood_group', 'address', 'phone']


# ────── Appointment ──────
class AppointmentSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.user.get_full_name', read_only=True)
    doctor_name = serializers.CharField(source='doctor.user.get_full_name', read_only=True)

    class Meta:
        model = Appointment
        fields = ['id', 'patient', 'patient_name', 'doctor', 'doctor_name',
                  'appointment_date', 'status', 'created_at']
        read_only_fields = ['created_at']

    def validate(self, data):
        doctor = data.get('doctor') or getattr(self.instance, 'doctor', None)
        if doctor and not doctor.is_available:
            raise serializers.ValidationError("Selected doctor is not available.")
        return data


# ────── Medicine ──────
class MedicineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medicine
        fields = '__all__'


# ────── PrescriptionMedicine ──────
class PrescriptionMedicineSerializer(serializers.ModelSerializer):
    medicine_name = serializers.CharField(source='medicine.name', read_only=True)

    class Meta:
        model = PrescriptionMedicine
        fields = ['id', 'medicine', 'medicine_name', 'dosage', 'duration']


# ────── Prescription ──────
class PrescriptionSerializer(serializers.ModelSerializer):
    prescription_medicines = PrescriptionMedicineSerializer(many=True)

    class Meta:
        model = Prescription
        fields = ['id', 'appointment', 'diagnosis', 'notes',
                  'created_at', 'prescription_medicines']
        read_only_fields = ['created_at']

    def create(self, validated_data):
        medicines_data = validated_data.pop('prescription_medicines', [])
        prescription = Prescription.objects.create(**validated_data)
        for med_data in medicines_data:
            PrescriptionMedicine.objects.create(prescription=prescription, **med_data)
        return prescription

    def update(self, instance, validated_data):
        medicines_data = validated_data.pop('prescription_medicines', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if medicines_data is not None:
            # replace all medicines for simplicity
            instance.prescription_medicines.all().delete()
            for med_data in medicines_data:
                PrescriptionMedicine.objects.create(prescription=instance, **med_data)
        return instance


# ────── Bill ──────
class BillSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.user.get_full_name', read_only=True)

    class Meta:
        model = Bill
        fields = ['id', 'patient', 'patient_name', 'amount', 'paid', 'created_at']
        read_only_fields = ['created_at']
