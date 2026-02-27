# clinic_appointment_system

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
python manage.py migrate
```

8. Start the development server:

```bash
python manage.py runserver
```