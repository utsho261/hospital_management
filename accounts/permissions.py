from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    """Only admin users can access."""
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'admin')


class IsDoctor(BasePermission):
    """Only doctors can access."""
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'doctor')


class IsPatient(BasePermission):
    """Only patients can access."""
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'patient')


class IsReceptionist(BasePermission):
    """Only receptionists can access."""
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'receptionist')


class IsAdminOrDoctor(BasePermission):
    """Admin or Doctor can access."""
    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated and
            request.user.role in ['admin', 'doctor']
        )


class IsAdminOrReceptionist(BasePermission):
    """Admin or Receptionist can access."""
    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated and
            request.user.role in ['admin', 'receptionist']
        )


class IsOwnerOrAdmin(BasePermission):
    """Object owner or admin can access."""
    def has_object_permission(self, request, view, obj):
        if request.user.role == 'admin':
            return True
        if hasattr(obj, 'user'):
            return obj.user == request.user
        if hasattr(obj, 'patient'):
            return obj.patient.user == request.user
        return False


class IsAdminOrReceptionistOrReadOnly(BasePermission):
    """
    Anyone authenticated can read (GET/list/retrieve).
    Only admin or receptionist can create/update/delete.
    Used for: Department, Medicine (master/reference data).
    """
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return True
        return request.user.role in ['admin', 'receptionist']


class IsAdminOrDoctorOrReadOnly(BasePermission):
    """
    Anyone authenticated can read.
    Only admin or doctor can create/update/delete.
    Used for: Doctor profile management.
    """
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return True
        return request.user.role in ['admin', 'doctor']


class IsAdminOrReceptionistOrPatientReadOnly(BasePermission):
    """
    Used for: Patient profile management.
    - Admin/receptionist: full access.
    - Patient: can read but cannot create/update/delete patient records.
    """
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if request.user.role in ['admin', 'receptionist']:
            return True
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return True
        return False


class IsAdminOrDoctorForPrescription(BasePermission):
    """
    Anyone authenticated can read prescriptions (e.g. patient viewing their own).
    Only admin or doctor can create/update/delete prescriptions.
    """
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return True
        return request.user.role in ['admin', 'doctor']


class IsAdminOrReceptionistForBilling(BasePermission):
    """
    Anyone authenticated can read bills (e.g. patient viewing their own).
    Only admin or receptionist can create/update/delete/mark-paid.
    """
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return True
        return request.user.role in ['admin', 'receptionist']
