# Hospital Management System API

A RESTful API for a Hospital Management System, built with **Django** and **Django REST Framework (DRF)**. The system supports role-based access for **Admins**, **Doctors**, **Patients**, and **Receptionists**, and covers the full workflow of a hospital: user registration, doctor/patient management, appointment booking, prescriptions with multiple medicines, and billing.

This project was built as an assignment based on a provided Entity-Relationship Diagram (ERD), implementing all required models, relationships, and API features.

## Features

- **Authentication** — JWT-based register/login/logout/token-refresh, with four roles: `admin`, `doctor`, `patient`, `receptionist`.
- **Role-based permissions** — write access to sensitive resources (departments, medicines, doctor/patient profiles, prescriptions, bills) is restricted by role, while read access is open to any authenticated user.
- **Doctor & Patient management** — full CRUD, doctor availability toggle, and search by name/specialization/blood group.
- **Appointments** — book, view, update, cancel; filter by doctor, patient, status, or date; custom actions to approve/complete/cancel.
- **Prescriptions** — create a prescription with multiple medicines in a single request (nested write), view prescriptions filtered by appointment.
- **Medicines** — list and search by name/description.
- **Billing** — generate bills per patient, mark as paid, filter by patient or paid status.
- **Filtering & search** — powered by `django-filter` and DRF's `SearchFilter`/`OrderingFilter` across most endpoints.

## Tech Stack

- **Backend:** Django 6, Django REST Framework
- **Auth:** `djangorestframework-simplejwt` (JWT access/refresh tokens, with blacklisting on logout)
- **Database:** SQLite (default, zero-config) — PostgreSQL-ready via `psycopg2-binary`
- **Filtering:** `django-filter`

## Entity Models (per ERD)

`User` · `Doctor` · `Patient` · `Department` · `Appointment` · `Prescription` · `PrescriptionMedicine` · `Medicine` · `Bill`

`User` is a custom user model (`AUTH_USER_MODEL`) with a `role` field. `Doctor` and `Patient` each have a one-to-one link to a `User`. `Appointment` links a `Patient` and a `Doctor`. `Prescription` is one-to-one with an `Appointment` and holds many `PrescriptionMedicine` entries (the join table between `Prescription` and `Medicine`). `Bill` belongs to a `Patient`.

## Project Structure

```
hospital_management/
├── accounts/              # User model, auth views, role-based permission classes
│   ├── models.py          # Custom User model with role field
│   ├── serializers.py     # Register / Login / User serializers
│   ├── views.py           # Register, Login, Logout, Profile views
│   ├── permissions.py     # Role-based permission classes (IsAdmin, IsDoctor, etc.)
│   └── urls.py
├── core/                   # Hospital domain models and APIs
│   ├── models.py          # Department, Doctor, Patient, Appointment, Medicine,
│   │                       # Prescription, PrescriptionMedicine, Bill
│   ├── serializers.py     # ModelSerializers, incl. nested Prescription write
│   ├── views.py           # ViewSets with filtering, search, and custom actions
│   └── urls.py            # Router registration
├── hospital_management/   # Project settings, root urls, WSGI/ASGI
├── manage.py
└── requirements.txt
```

## Setup & Installation

**1. Clone the repository**
```bash
git clone https://github.com/<your-username>/hospital-management-system.git
cd hospital-management-system
```

**2. Create and activate a virtual environment**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Apply migrations**
```bash
python manage.py migrate
```

**5. (Optional) Create a superuser for Django admin access**
```bash
python manage.py createsuperuser
```

**6. Run the development server**
```bash
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/`.

> **Note on database:** the project uses SQLite by default for zero-config local development. To switch to PostgreSQL, update the `DATABASES` setting in `hospital_management/settings.py` (the `psycopg2-binary` driver is already included in `requirements.txt`).

## Authentication

All endpoints except `register` and `login` require a JWT access token in the request header:

```
Authorization: Bearer <access_token>
```

| Endpoint | Method | Description |
|---|---|---|
| `/api/auth/register/` | POST | Register a new user (specify `role`: admin/doctor/patient/receptionist) |
| `/api/auth/login/` | POST | Log in, returns access & refresh tokens |
| `/api/auth/logout/` | POST | Blacklist the refresh token |
| `/api/auth/token/refresh/` | POST | Get a new access token using a refresh token |
| `/api/auth/profile/` | GET/PUT | View or update the logged-in user's profile |

## API Endpoints

### Authentication (`/api/auth/`)
| Endpoint | Method | Description |
|---|---|---|
| `/register/` | POST | Register user with role (admin/doctor/patient/receptionist) |
| `/login/` | POST | Login, returns JWT access + refresh tokens |
| `/logout/` | POST | Blacklist refresh token |
| `/token/refresh/` | POST | Refresh access token |
| `/profile/` | GET / PUT | Get / update current user profile |

### Core Resources (`/api/`)
| Resource | Endpoint | Filters / Actions |
|---|---|---|
| Departments | `/departments/` | `?search=` |
| Doctors | `/doctors/` | `?department=&is_available=&search=` |
| Doctor availability | `/doctors/{id}/toggle-availability/` (PATCH) | — |
| Patients | `/patients/` | `?search=` |
| Appointments | `/appointments/` | `?doctor=&patient=&status=&date=&date_from=&date_to=&ordering=` |
| Appointment actions | `/appointments/{id}/{approve\|complete\|cancel}/` (PATCH) | — |
| Medicines | `/medicines/` | `?search=` |
| Prescriptions | `/prescriptions/` | `?appointment=` — supports nested medicines on create/update |
| Bills | `/bills/` | `?patient=&paid=` |
| Mark bill paid | `/bills/{id}/mark-paid/` (PATCH) | — |

All endpoints (except register/login) require:
`Authorization: Bearer <access_token>`

## Role-Based Permissions

| Resource | Read | Write (Create/Update/Delete) |
|---|---|---|
| Department | Any authenticated user | Admin, Receptionist |
| Doctor | Any authenticated user | Admin, Doctor |
| Patient | Any authenticated user | Admin, Receptionist |
| Appointment | Any authenticated user | Any authenticated user |
| Medicine | Any authenticated user | Admin, Receptionist |
| Prescription | Any authenticated user | Admin, Doctor |
| Bill | Any authenticated user | Admin, Receptionist |

## Testing the API

A ready-to-import **Postman collection** is included (`hospital_management_postman_collection.json` if shared alongside this repo, or see the project's submission notes), pre-configured to run the full flow end-to-end: register → login → create department/doctor/patient → book appointment → create prescription with multiple medicines → generate and pay a bill, including permission checks for restricted roles.

You can also explore and test endpoints interactively using the DRF browsable API by visiting any endpoint URL directly in a browser while logged in via Django admin/session, or using `curl`:

```bash
curl -X POST http://127.0.0.1:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin1","email":"admin1@test.com","password":"pass1234","password2":"pass1234","first_name":"Admin","last_name":"One","role":"admin"}'
```
## Sample Requests

**Create Prescription with multiple medicines**
```json
POST /api/prescriptions/
{
  "appointment": 1,
  "diagnosis": "Fever and headache",
  "notes": "Rest for 3 days",
  "prescription_medicines": [
    {"medicine": 1, "dosage": "1+0+1", "duration": "5 days"},
    {"medicine": 2, "dosage": "0+0+1", "duration": "3 days"}
  ]
}
```
## License

This project was developed for educational purposes as part of a Python/Django assignment.
