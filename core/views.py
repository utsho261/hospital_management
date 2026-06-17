from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Department, Doctor, Patient, Appointment, Medicine, Prescription, Bill
from .serializers import (
    DepartmentSerializer, DoctorSerializer, PatientSerializer,
    AppointmentSerializer, MedicineSerializer, PrescriptionSerializer, BillSerializer
)
from accounts.permissions import (
    IsAdminOrReceptionistOrReadOnly,
    IsAdminOrDoctorOrReadOnly,
    IsAdminOrReceptionistOrPatientReadOnly,
    IsAdminOrDoctorForPrescription,
    IsAdminOrReceptionistForBilling,
)


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAdminOrReceptionistOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']


class DoctorViewSet(viewsets.ModelViewSet):
    queryset = Doctor.objects.select_related('user', 'department').all()
    serializer_class = DoctorSerializer
    permission_classes = [IsAdminOrDoctorOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['department', 'is_available']
    search_fields = ['user__first_name', 'user__last_name', 'specialization']

    @action(detail=True, methods=['patch'], url_path='toggle-availability')
    def toggle_availability(self, request, pk=None):
        doctor = self.get_object()
        doctor.is_available = not doctor.is_available
        doctor.save()
        return Response({
            'message': f"Doctor availability set to {doctor.is_available}",
            'is_available': doctor.is_available
        })


class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.select_related('user').all()
    serializer_class = PatientSerializer
    permission_classes = [IsAdminOrReceptionistOrPatientReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['user__first_name', 'user__last_name', 'blood_group']


class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.select_related('patient__user', 'doctor__user').all()
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['doctor', 'patient', 'status']
    ordering_fields = ['appointment_date', 'created_at']

    def get_queryset(self):
        qs = super().get_queryset()
        date = self.request.query_params.get('date')
        if date:
            qs = qs.filter(appointment_date__date=date)
        return qs

    @action(detail=True, methods=['patch'], url_path='cancel')
    def cancel(self, request, pk=None):
        appointment = self.get_object()
        if appointment.status == 'cancelled':
            return Response({'error': 'Already cancelled.'}, status=status.HTTP_400_BAD_REQUEST)
        appointment.status = 'cancelled'
        appointment.save()
        return Response({'message': 'Appointment cancelled.', 'status': appointment.status})

    @action(detail=True, methods=['patch'], url_path='approve')
    def approve(self, request, pk=None):
        appointment = self.get_object()
        appointment.status = 'approved'
        appointment.save()
        return Response({'message': 'Appointment approved.', 'status': appointment.status})

    @action(detail=True, methods=['patch'], url_path='complete')
    def complete(self, request, pk=None):
        appointment = self.get_object()
        appointment.status = 'completed'
        appointment.save()
        return Response({'message': 'Appointment completed.', 'status': appointment.status})


class MedicineViewSet(viewsets.ModelViewSet):
    queryset = Medicine.objects.all()
    serializer_class = MedicineSerializer
    permission_classes = [IsAdminOrReceptionistOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']


class PrescriptionViewSet(viewsets.ModelViewSet):
    queryset = Prescription.objects.select_related('appointment').prefetch_related('prescription_medicines__medicine').all()
    serializer_class = PrescriptionSerializer
    permission_classes = [IsAdminOrDoctorForPrescription]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['appointment']


class BillViewSet(viewsets.ModelViewSet):
    queryset = Bill.objects.select_related('patient__user').all()
    serializer_class = BillSerializer
    permission_classes = [IsAdminOrReceptionistForBilling]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['patient', 'paid']

    @action(detail=True, methods=['patch'], url_path='mark-paid')
    def mark_paid(self, request, pk=None):
        bill = self.get_object()
        bill.paid = True
        bill.save()
        return Response({'message': 'Bill marked as paid.', 'paid': bill.paid})
