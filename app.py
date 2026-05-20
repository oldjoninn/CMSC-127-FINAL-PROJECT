"""
LTO Information Management System – Flask GUI
CMSC 127 Milestone 3
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import mysql.connector
from mysql.connector import Error
from datetime import date
from dotenv import load_dotenv
import os
load_dotenv()

app = Flask(__name__)
app.secret_key = "lto_cmsc127_secret"

# ── Database connection ──────────────────────────────────────────────────────

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": os.getenv("DB_PASSWORD", ""),        
    "database": "lto_db",
}


def get_db():
    """Return a new database connection."""
    return mysql.connector.connect(**DB_CONFIG)


def query(sql, params=None, fetchone=False):
    """Run a SELECT and return rows as list[dict]."""
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute(sql, params or ())
    rows = cur.fetchone() if fetchone else cur.fetchall()
    cur.close()
    conn.close()
    return rows


def execute(sql, params=None):
    """Run INSERT / UPDATE / DELETE."""
    conn = get_db()
    cur = conn.cursor()
    cur.execute(sql, params or ())
    conn.commit()
    last_id = cur.lastrowid
    cur.close()
    conn.close()
    return last_id


# ══════════════════════════════════════════════════════════════════════════════
#  PAGES
# ══════════════════════════════════════════════════════════════════════════════

@app.route("/")
def index():
    return render_template("index.html", page="dashboard")


# ── DRIVERS ──────────────────────────────────────────────────────────────────

@app.route("/drivers")
def drivers():
    rows = query("SELECT *, TIMESTAMPDIFF(YEAR, date_of_birth, CURDATE()) AS age FROM driver ORDER BY last_name, first_name")
    return render_template("index.html", page="drivers", rows=rows)


@app.route("/drivers/add", methods=["POST"])
def drivers_add():
    f = request.form
    execute(
        """INSERT INTO driver
           (license_number, first_name, middle_name, last_name,
            date_of_birth, sex, address, license_type,
            license_status, license_issuance_date, license_expiration_date)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
        (f["license_number"], f["first_name"], f.get("middle_name") or None,
         f["last_name"], f["date_of_birth"], f["sex"], f["address"],
         f["license_type"], f["license_status"],
         f["license_issuance_date"], f["license_expiration_date"]),
    )
    flash("Driver added successfully.", "success")
    return redirect(url_for("drivers"))


@app.route("/drivers/edit", methods=["POST"])
def drivers_edit():
    f = request.form
    execute(
        """UPDATE driver SET
           first_name=%s, middle_name=%s, last_name=%s,
           date_of_birth=%s, sex=%s, address=%s, license_type=%s,
           license_status=%s, license_issuance_date=%s, license_expiration_date=%s
           WHERE license_number=%s""",
        (f["first_name"], f.get("middle_name") or None, f["last_name"],
         f["date_of_birth"], f["sex"], f["address"], f["license_type"],
         f["license_status"], f["license_issuance_date"],
         f["license_expiration_date"], f["license_number"]),
    )
    flash("Driver updated.", "success")
    return redirect(url_for("drivers"))


@app.route("/drivers/delete/<license_number>")
def drivers_delete(license_number):
    try:
        execute("DELETE FROM driver WHERE license_number=%s", (license_number,))
        flash("Driver deleted.", "success")
    except Error as e:
        flash(f"Cannot delete: {e}", "danger")
    return redirect(url_for("drivers"))


# ── VEHICLES ─────────────────────────────────────────────────────────────────

@app.route("/vehicles")
def vehicles():
    rows = query("""
        SELECT v.*, d.first_name AS owner_first_name, d.last_name AS owner_last_name
        FROM vehicle v JOIN driver d ON v.license_number = d.license_number
        ORDER BY v.plate_number
    """)
    drivers_list = query("SELECT license_number, first_name, last_name FROM driver ORDER BY last_name")
    return render_template("index.html", page="vehicles", rows=rows, drivers_list=drivers_list)


@app.route("/vehicles/add", methods=["POST"])
def vehicles_add():
    f = request.form
    execute(
        """INSERT INTO vehicle
           (plate_number, chassis_number, engine_number, vehicle_type,
            ownership_type, make, model, year, color, franchise_number, license_number)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
        (f["plate_number"], f["chassis_number"], f["engine_number"],
         f["vehicle_type"], f["ownership_type"], f["make"], f["model"],
         int(f["year"]), f["color"], f.get("franchise_number") or None,
         f["license_number"]),
    )
    flash("Vehicle added.", "success")
    return redirect(url_for("vehicles"))


@app.route("/vehicles/edit", methods=["POST"])
def vehicles_edit():
    f = request.form
    execute(
        """UPDATE vehicle SET
           engine_number=%s, vehicle_type=%s, ownership_type=%s,
           make=%s, model=%s, year=%s, color=%s, franchise_number=%s, license_number=%s
           WHERE plate_number=%s AND chassis_number=%s""",
        (f["engine_number"], f["vehicle_type"], f["ownership_type"],
         f["make"], f["model"], int(f["year"]), f["color"],
         f.get("franchise_number") or None, f["license_number"],
         f["plate_number"], f["chassis_number"]),
    )
    flash("Vehicle updated.", "success")
    return redirect(url_for("vehicles"))


@app.route("/vehicles/delete/<plate_number>/<chassis_number>")
def vehicles_delete(plate_number, chassis_number):
    try:
        execute("DELETE FROM vehicle WHERE plate_number=%s AND chassis_number=%s",
                (plate_number, chassis_number))
        flash("Vehicle deleted.", "success")
    except Error as e:
        flash(f"Cannot delete: {e}", "danger")
    return redirect(url_for("vehicles"))


# ── REGISTRATIONS ────────────────────────────────────────────────────────────

@app.route("/registrations")
def registrations():
    rows = query("""
        SELECT vr.*, v.make, v.model, v.year AS vehicle_year,
               d.first_name AS owner_first_name, d.last_name AS owner_last_name
        FROM vehicle_registration vr
        JOIN vehicle v ON vr.plate_number = v.plate_number AND vr.chassis_number = v.chassis_number
        JOIN driver d ON v.license_number = d.license_number
        ORDER BY vr.registration_date DESC
    """)
    vehicles_list = query("SELECT plate_number, chassis_number, make, model FROM vehicle ORDER BY plate_number")
    return render_template("index.html", page="registrations", rows=rows, vehicles_list=vehicles_list)


@app.route("/registrations/add", methods=["POST"])
def registrations_add():
    f = request.form
    plate, chassis = f["vehicle_key"].split("|")
    execute(
        """INSERT INTO vehicle_registration
           (registration_number, registration_date, expiration_date,
            registration_status, plate_number, chassis_number)
           VALUES (%s,%s,%s,%s,%s,%s)""",
        (f["registration_number"], f["registration_date"],
         f["expiration_date"], f["registration_status"], plate, chassis),
    )
    flash("Registration added.", "success")
    return redirect(url_for("registrations"))


@app.route("/registrations/edit", methods=["POST"])
def registrations_edit():
    f = request.form
    execute(
        """UPDATE vehicle_registration SET
           registration_date=%s, expiration_date=%s, registration_status=%s
           WHERE registration_number=%s""",
        (f["registration_date"], f["expiration_date"],
         f["registration_status"], f["registration_number"]),
    )
    flash("Registration updated.", "success")
    return redirect(url_for("registrations"))


@app.route("/registrations/delete/<registration_number>")
def registrations_delete(registration_number):
    try:
        execute("DELETE FROM vehicle_registration WHERE registration_number=%s",
                (registration_number,))
        flash("Registration deleted.", "success")
    except Error as e:
        flash(f"Cannot delete: {e}", "danger")
    return redirect(url_for("registrations"))


# ── VIOLATIONS ───────────────────────────────────────────────────────────────

@app.route("/violations")
def violations():
    rows = query("""
        SELECT tv.*, tvt.violation_type,
               d.first_name AS driver_first_name, d.last_name AS driver_last_name
        FROM traffic_violation tv
        LEFT JOIN traffic_violation_type tvt ON tv.traffic_violation_id = tvt.traffic_violation_id
        JOIN driver d ON tv.license_number = d.license_number
        ORDER BY tv.date DESC, tv.time DESC
    """)

    # Convert timedelta to string so Jinja's tojson filter can serialize it
    for r in rows:
        if hasattr(r.get("time"), "total_seconds"):
            r["time"] = str(r["time"])

    drivers_list = query("SELECT license_number, first_name, last_name FROM driver ORDER BY last_name")
    vehicles_list = query("SELECT plate_number, chassis_number, make, model FROM vehicle ORDER BY plate_number")
    return render_template("index.html", page="violations", rows=rows,
                           drivers_list=drivers_list, vehicles_list=vehicles_list)


@app.route("/violations/add", methods=["POST"])
def violations_add():
    f = request.form
    plate, chassis = f["vehicle_key"].split("|")
    vid = execute(
        """INSERT INTO traffic_violation
           (violation_status, apprehending_officer, total_fine_amount,
            location, date, time, license_number, plate_number, chassis_number)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
        (f["violation_status"], f.get("apprehending_officer") or None,
         float(f["total_fine_amount"]), f["location"], f["date"], f["time"],
         f["license_number"], plate, chassis),
    )
    if f.get("violation_type"):
        execute(
            "INSERT INTO traffic_violation_type (traffic_violation_id, violation_type) VALUES (%s,%s)",
            (vid, f["violation_type"]),
        )
    flash("Violation recorded.", "success")
    return redirect(url_for("violations"))


@app.route("/violations/edit", methods=["POST"])
def violations_edit():
    f = request.form
    vid = int(f["traffic_violation_id"])
    execute(
        """UPDATE traffic_violation SET
           violation_status=%s, apprehending_officer=%s,
           total_fine_amount=%s, location=%s, date=%s, time=%s
           WHERE traffic_violation_id=%s""",
        (f["violation_status"], f.get("apprehending_officer") or None,
         float(f["total_fine_amount"]), f["location"], f["date"], f["time"], vid),
    )
    # Update violation type
    existing = query("SELECT * FROM traffic_violation_type WHERE traffic_violation_id=%s", (vid,))
    if f.get("violation_type"):
        if existing:
            execute("UPDATE traffic_violation_type SET violation_type=%s WHERE traffic_violation_id=%s",
                    (f["violation_type"], vid))
        else:
            execute("INSERT INTO traffic_violation_type (traffic_violation_id, violation_type) VALUES (%s,%s)",
                    (vid, f["violation_type"]))
    flash("Violation updated.", "success")
    return redirect(url_for("violations"))


@app.route("/violations/delete/<int:vid>")
def violations_delete(vid):
    try:
        execute("DELETE FROM traffic_violation_type WHERE traffic_violation_id=%s", (vid,))
        execute("DELETE FROM traffic_violation WHERE traffic_violation_id=%s", (vid,))
        flash("Violation deleted.", "success")
    except Error as e:
        flash(f"Cannot delete: {e}", "danger")
    return redirect(url_for("violations"))


# ══════════════════════════════════════════════════════════════════════════════
#  REPORTS
# ══════════════════════════════════════════════════════════════════════════════

@app.route("/reports")
def reports():
    return render_template("index.html", page="reports")


@app.route("/reports/drivers_filtered")
def report_drivers_filtered():
    """Report 1: Drivers filtered by license type, status, age range, sex."""
    lt = request.args.get("license_type", "")
    ls = request.args.get("license_status", "")
    sex = request.args.get("sex", "")
    age_min = request.args.get("age_min", "")
    age_max = request.args.get("age_max", "")

    sql = """SELECT license_number, first_name, middle_name, last_name, sex,
                    TIMESTAMPDIFF(YEAR, date_of_birth, CURDATE()) AS age,
                    address, license_type, license_status, license_expiration_date
             FROM driver WHERE 1=1"""
    params = []
    if lt:
        sql += " AND license_type = %s"; params.append(lt)
    if ls:
        sql += " AND license_status = %s"; params.append(ls)
    if sex:
        sql += " AND sex = %s"; params.append(sex)
    if age_min:
        sql += " AND TIMESTAMPDIFF(YEAR, date_of_birth, CURDATE()) >= %s"; params.append(int(age_min))
    if age_max:
        sql += " AND TIMESTAMPDIFF(YEAR, date_of_birth, CURDATE()) <= %s"; params.append(int(age_max))
    sql += " ORDER BY last_name, first_name"

    rows = query(sql, params)
    return render_template("index.html", page="report_result",
                           report_title="Registered Drivers (Filtered)",
                           report_id=1, rows=rows)


@app.route("/reports/vehicles_by_driver")
def report_vehicles_by_driver():
    """Report 2: Vehicles owned by a given driver."""
    ln = request.args.get("license_number", "")
    rows = []
    if ln:
        rows = query("""
            SELECT v.plate_number, v.chassis_number, v.engine_number,
                   v.vehicle_type, v.ownership_type, v.make, v.model,
                   v.year, v.color, v.franchise_number,
                   d.first_name AS owner_first_name, d.last_name AS owner_last_name
            FROM vehicle v JOIN driver d ON v.license_number = d.license_number
            WHERE d.license_number = %s ORDER BY v.plate_number
        """, (ln,))
    return render_template("index.html", page="report_result",
                           report_title=f"Vehicles Owned by Driver {ln}",
                           report_id=2, rows=rows)


@app.route("/reports/expired_registrations")
def report_expired_registrations():
    """Report 3: Vehicles with expired registrations as of a given date."""
    as_of = request.args.get("as_of_date", str(date.today()))
    rows = query("""
        SELECT v.plate_number, v.chassis_number, v.vehicle_type, v.make, v.model, v.year,
               d.first_name AS owner_first_name, d.last_name AS owner_last_name,
               d.license_number, vr.registration_number,
               vr.expiration_date, vr.registration_status
        FROM vehicle_registration vr
        JOIN vehicle v ON vr.plate_number = v.plate_number AND vr.chassis_number = v.chassis_number
        JOIN driver d ON v.license_number = d.license_number
        WHERE vr.expiration_date < %s
        ORDER BY vr.expiration_date DESC
    """, (as_of,))
    return render_template("index.html", page="report_result",
                           report_title=f"Expired Registrations (as of {as_of})",
                           report_id=3, rows=rows)


@app.route("/reports/invalid_licenses")
def report_invalid_licenses():
    """Report 4: Drivers with expired or suspended licenses."""
    rows = query("""
        SELECT license_number, first_name, middle_name, last_name,
               license_type, license_status, license_expiration_date,
               TIMESTAMPDIFF(YEAR, date_of_birth, CURDATE()) AS age, address
        FROM driver
        WHERE license_status IN ('expired','suspended')
        ORDER BY license_status, last_name
    """)
    return render_template("index.html", page="report_result",
                           report_title="Drivers with Expired / Suspended Licenses",
                           report_id=4, rows=rows)


@app.route("/reports/violations_by_driver")
def report_violations_by_driver():
    """Report 5: Violations by a driver within a date range."""
    ln = request.args.get("license_number", "")
    d1 = request.args.get("date_from", "2020-01-01")
    d2 = request.args.get("date_to", str(date.today()))
    rows = []
    if ln:
        rows = query("""
            SELECT tv.traffic_violation_id, tv.date, tv.time, tv.location,
                   tv.apprehending_officer, tv.violation_status,
                   tv.total_fine_amount, tv.plate_number, tvt.violation_type
            FROM traffic_violation tv
            LEFT JOIN traffic_violation_type tvt ON tv.traffic_violation_id = tvt.traffic_violation_id
            WHERE tv.license_number = %s AND tv.date BETWEEN %s AND %s
            ORDER BY tv.date, tv.time
        """, (ln, d1, d2))
    return render_template("index.html", page="report_result",
                           report_title=f"Violations by {ln} ({d1} to {d2})",
                           report_id=5, rows=rows)


@app.route("/reports/violations_per_type")
def report_violations_per_type():
    """Report 6: Violation count per type for a given year."""
    yr = request.args.get("year", str(date.today().year))
    rows = query("""
        SELECT tvt.violation_type, COUNT(*) AS total_violations
        FROM traffic_violation_type tvt
        JOIN traffic_violation tv ON tvt.traffic_violation_id = tv.traffic_violation_id
        WHERE YEAR(tv.date) = %s
        GROUP BY tvt.violation_type
        ORDER BY total_violations DESC
    """, (int(yr),))
    return render_template("index.html", page="report_result",
                           report_title=f"Violations per Type ({yr})",
                           report_id=6, rows=rows)


@app.route("/reports/vehicles_in_violations")
def report_vehicles_in_violations():
    """Report 7: Vehicles involved in violations in a city/region."""
    loc = request.args.get("location", "")
    rows = []
    if loc:
        rows = query("""
            SELECT DISTINCT v.plate_number, v.chassis_number, v.make, v.model,
                   v.year, v.color, v.vehicle_type,
                   d.first_name AS owner_first_name, d.last_name AS owner_last_name,
                   tv.location
            FROM traffic_violation tv
            JOIN vehicle v ON tv.plate_number = v.plate_number AND tv.chassis_number = v.chassis_number
            JOIN driver d ON v.license_number = d.license_number
            WHERE tv.location LIKE %s
            ORDER BY v.plate_number
        """, (f"%{loc}%",))
    return render_template("index.html", page="report_result",
                           report_title=f"Vehicles in Violations near '{loc}'",
                           report_id=7, rows=rows)


# ── Dashboard stats ──────────────────────────────────────────────────────────

@app.route("/api/stats")
def api_stats():
    total_drivers = query("SELECT COUNT(*) AS c FROM driver", fetchone=True)["c"]
    total_vehicles = query("SELECT COUNT(*) AS c FROM vehicle", fetchone=True)["c"]
    total_violations = query("SELECT COUNT(*) AS c FROM traffic_violation", fetchone=True)["c"]
    unpaid = query("SELECT COUNT(*) AS c FROM traffic_violation WHERE violation_status='unpaid'", fetchone=True)["c"]
    expired_lic = query("SELECT COUNT(*) AS c FROM driver WHERE license_status IN ('expired','suspended')", fetchone=True)["c"]
    expired_reg = query("SELECT COUNT(*) AS c FROM vehicle_registration WHERE expiration_date < CURDATE()", fetchone=True)["c"]
    return jsonify(dict(
        total_drivers=total_drivers, total_vehicles=total_vehicles,
        total_violations=total_violations, unpaid_violations=unpaid,
        expired_licenses=expired_lic, expired_registrations=expired_reg,
    ))


# ──────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(debug=True, port=5000)
