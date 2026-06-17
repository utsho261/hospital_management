from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DepartmentViewSet, DoctorViewSet, PatientViewSet,
    AppointmentViewSet, MedicineViewSet, PrescriptionViewSet, BillViewSet
)

router = DefaultRouter()
router.register('departments', DepartmentViewSet, basename='department')
router.register('doctors', DoctorViewSet, basename='doctor')
router.register('patients', PatientViewSet, basename='patient')
router.register('appointments', AppointmentViewSet, basename='appointment')
router.register('medicines', MedicineViewSet, basename='medicine')
router.register('prescriptions', PrescriptionViewSet, basename='prescription')
router.register('bills', BillViewSet, basename='bill')

urlpatterns = [
    path('', include(router.urls)),
]
