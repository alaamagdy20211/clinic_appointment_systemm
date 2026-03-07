# HealthNest - Clinic Appointment System

<p align="center">
  <img src="static/images/logo.png" alt="HealthNest Logo" width="180">
</p>


HealthNest is a clinic appointment system built using Django and PostgreSQL. It allows patients to book appointments with doctors, manage their profiles, and view their appointment history. Doctors can manage their schedules, view patient information, and update appointment statuses.

## How to set up the project

1. Clone the repository:

```bash
git clone https://github.com/ahmedbakry024/clinic_appointment_system.git
```

2. Navigate to the project directory:

```bash
cd clinic_appointment_system
```

3. Create a virtual environment:

```bash
python -m venv venv
```

4. Activate the virtual environment:

- On Windows:

```bash
venv\Scripts\activate
```

- On macOS/Linux:

```bash
source venv/bin/activate
```

5. Install the required dependencies:
```bash
pip install django psycopg2-binary dotenv
```

6. Set up the PostgreSQL database:

- Create a new database named `clinic_db` (or use the name specified in your `.env` file).
- Update the `.env` file with your database credentials.

7. Run database migrations:

```bash
python manage.py makemigrations
python manage.py migrate
```

8. Start the development server:

```bash
python manage.py runserver
```

9. Access the application in your web browser at `http://localhost:8000`

## Adding a superuser
To access the Django admin interface, you need to create a superuser account. Run the following command and follow the prompts:

```bash
python manage.py createsuperuser
```

## Accessing the admin interface
Once you have created a superuser, you can access the admin interface by navigating to `http://localhost:8000/admin` in your web browser. Log in with the superuser credentials you created, and you will be able to manage the application's data through the admin dashboard.

## Adding initial data samples
To add initial data samples for testing purposes, you can use the samples provided in the `sample.sql` file. Run the following command to load the data into your PostgreSQL database:

```bash
psql -U your_username -d clinic_db -f sample.sql
```

All the users passwords are set to `Test1234!` for testing purposes. Make sure to replace `your_username` with your actual PostgreSQL username and `clinic_db` with the name of your database.

## How to test the project

1. Run the development server:

```bash
python manage.py runserver
```
2. Open your web browser and navigate to `http://localhost:8000`.
3. You can register as a new patient or log in with existing credentials (use the sample data for testing).
4. Patients can book appointments, view their profiles, and check their appointment history.
5. Doctors can log in to manage their schedules, view patient information, and update appointment statuses.
6. Receptionists can log in to manage appointments and schedule queues.
7. Admins can log in to manage users, doctors, and appointments through the admin interface.
8. Test the functionality of the application by performing various actions such as booking appointments, updating profiles, and managing schedules.

