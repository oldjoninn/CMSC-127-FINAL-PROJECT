# LTO Information Management System — GUI
### CMSC 127 Milestone 3

A Flask-based web GUI for the LTO database system.

---

## Prerequisites

- **Python 3.8+**
- **MariaDB** (running locally)
- **pip** packages: `flask`, `mysql-connector-python`

## Setup

### 1. Install Python dependencies

```bash
pip install flask mysql-connector-python
```

### 2. Initialize the database

Make sure MariaDB is running, then load the SQL schema:

```bash
mysql -u root < crisostomo_shi_malco_milestone.sql
```

> This creates the `lto_db` database with all tables, views, and dummy data.

### 3. Configure database credentials

Create a `.env` file in the project root:
```
DB_PASSWORD=your_mariadb_password_here
```
Leave it blank if your MariaDB has no password:
```
DB_PASSWORD=
```

> `.env` is listed in `.gitignore` and will not be pushed to GitHub.

### 4. Run the application
```
python app.py
```
> Then open **http://localhost:5000** in your browser.

---

## Features

| Module           | Capabilities                           |
| ---------------- | -------------------------------------- |
| **Dashboard**    | Overview stats (drivers, vehicles, violations, etc.) |
| **Drivers**      | Add / Edit / Delete driver records     |
| **Vehicles**     | Add / Edit / Delete vehicle records    |
| **Registrations**| Add / Edit / Delete registration records |
| **Violations**   | Record / Edit / Delete traffic violations |
| **Reports**      | 7 parameterized SQL reports            |

### Reports

1. Drivers filtered by license type, status, age range, sex
2. Vehicles owned by a given driver
3. Vehicles with expired registrations (as of a date)
4. Drivers with expired / suspended licenses
5. Violations by a driver within a date range
6. Violation count per type for a given year
7. Vehicles involved in violations in a city/region

---

## Tech Stack

- **Backend:** Python + Flask
- **Database:** MariaDB (mysql-connector-python)
- **Frontend:** HTML/CSS/JS (Jinja2 templates, no external frameworks)

## Project Structure

```
lto-gui/
├── app.py                          # Flask application (all routes)
├── templates/
│   └── index.html                  # Single-page template (all views)
├── crisostomo_shi_malco_milestone.sql  # Database schema + data
└── README.md
```
