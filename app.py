"""
LTO Information Management System – Flask GUI
CMSC 127 Project Presentation
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import mysql.connector
from mysql.connector import Error, IntegrityError
from datetime import date, datetime
import os
import re

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

app = Flask(__name__)
app.secret_key = "lto_cmsc127_secret"


# ── Database connection ──────────────────────────────────────────────────────

DB_CONFIG = {
    "host":     os.getenv("DB_HOST", "localhost"),
    "user":     os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "lto_db"),
}


def get_db():
    return mysql.connector.connect(**DB_CONFIG)


def query(sql, params=None, fetchone=False):
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute(sql, params or ())
    rows = cur.fetchone() if fetchone else cur.fetchall()
    cur.close()
    conn.close()
    return rows


def execute(sql, params=None):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(sql, params or ())
    conn.commit()
    last_id = cur.lastrowid
    cur.close()
    conn.close()
    return last_id


# ── Validation helpers ───────────────────────────────────────────────────────

VALID_SEX            = {"M", "F"}
VALID_LICENSE_TYPES  = {"Non-Professional", "Professional", "Student Permit"}
VALID_LICENSE_STATUS = {"valid", "expired", "suspended", "revoked"}
VALID_OWNERSHIP      = {"private", "public"}
VALID_REG_STATUS     = {"active", "expired", "suspended", "revoked"}
VALID_VIOL_STATUS    = {"unpaid", "paid", "contested", "dismissed"}

# Identifier format patterns. 
LICENSE_RE      = re.compile(r"^[A-Z][0-9]{2}-[0-9]{2}-[0-9]{6}$")
PLATE_RE        = re.compile(r"^[A-Z]{3} [0-9]{3,4}$")
CHASSIS_RE      = re.compile(r"^[A-Z]{2,5}-[0-9]{3,8}$")
REGISTRATION_RE = re.compile(r"^REG-[0-9]{4}-[0-9]{5}$")


class ValidationError(Exception):
    """Raised on form validation failure."""


def clean(value, *, lower=False):
    """Trim a form value and optionally lowercase it. Empty string becomes None."""
    if value is None:
        return None
    v = str(value).strip()
    if not v:
        return None
    return v.lower() if lower else v


def require(value, field):
    v = clean(value)
    if v is None:
        raise ValidationError(f"{field} is required.")
    return v


def parse_date(s, field):
    s = clean(s)
    if s is None:
        raise ValidationError(f"{field} is required.")
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except ValueError:
        raise ValidationError(f"{field} must be a valid date (YYYY-MM-DD).")


def parse_time(s, field):
    s = clean(s)
    if s is None:
        raise ValidationError(f"{field} is required.")
    for fmt in ("%H:%M", "%H:%M:%S"):
        try:
            return datetime.strptime(s, fmt).time()
        except ValueError:
            continue
    raise ValidationError(f"{field} must be a valid time (HH:MM).")


def parse_int(s, field, *, min_v=None, max_v=None):
    s = clean(s)
    if s is None:
        raise ValidationError(f"{field} is required.")
    try:
        n = int(s)
    except ValueError:
        raise ValidationError(f"{field} must be a whole number.")
    if min_v is not None and n < min_v:
        raise ValidationError(f"{field} must be ≥ {min_v}.")
    if max_v is not None and n > max_v:
        raise ValidationError(f"{field} must be ≤ {max_v}.")
    return n


def parse_decimal(s, field, *, min_v=None):
    s = clean(s)
    if s is None:
        raise ValidationError(f"{field} is required.")
    try:
        n = float(s)
    except ValueError:
        raise ValidationError(f"{field} must be a number.")
    if min_v is not None and n < min_v:
        raise ValidationError(f"{field} must be ≥ {min_v}.")
    return n


def must_be_in(value, allowed, field):
    if value not in allowed:
        raise ValidationError(
            f"{field} must be one of: {', '.join(sorted(allowed))}."
        )
    return value


def db_error_message(e):
    """Translate common MySQL errors into user-friendly text."""
    msg = str(e)
    if isinstance(e, IntegrityError):
        if "Duplicate entry" in msg:
            return "Duplicate record — that identifier is already in use."
        if "foreign key constraint fails" in msg.lower():
            if "REFERENCES `driver`" in msg or "fk_violation_driver" in msg or "fk_vehicle_driver" in msg:
                return "Referenced driver does not exist or is still in use by other records."
            if "fk_registration_vehicle" in msg or "fk_violation_vehicle" in msg:
                return "Referenced vehicle does not exist or is still in use by other records."
            return "Cannot complete operation: related records still exist or referenced row missing."
        if "chk_" in msg or "CHECK constraint" in msg:
            return f"Value violates a database constraint: {msg}"
    return f"Database error: {msg}"


# ══════════════════════════════════════════════════════════════════════════════
#  PAGES
# ══════════════════════════════════════════════════════════════════════════════

@app.route("/")
def index():
    return render_template("dashboard.html")


# ── DRIVERS ──────────────────────────────────────────────────────────────────

@app.route("/drivers")
def drivers():
    q = clean(request.args.get("q"))
    sql = """SELECT *, TIMESTAMPDIFF(YEAR, date_of_birth, CURDATE()) AS age
             FROM driver"""
    params = []
    if q:
        sql += """ WHERE license_number LIKE %s
                      OR first_name LIKE %s
                      OR last_name LIKE %s
                      OR address LIKE %s"""
        like = f"%{q}%"
        params = [like, like, like, like]
    sql += " ORDER BY last_name, first_name"
    rows = query(sql, params)
    return render_template("drivers.html", rows=rows, search=q or "")


def _validate_driver(f, *, is_edit=False):
    # Uppercase before validating so lowercase user input (e.g. "n01-90-...")
    # still matches the canonical format without rejecting it.
    license_number = require(f.get("license_number"), "License number").upper()
    if not LICENSE_RE.match(license_number):
        raise ValidationError(
            "License number must follow the format L##-##-###### "
            "(e.g. N01-90-123456)."
        )
    first_name = require(f.get("first_name"), "First name")
    last_name  = require(f.get("last_name"),  "Last name")
    middle_name = clean(f.get("middle_name"))
    dob = parse_date(f.get("date_of_birth"), "Date of birth")
    sex = must_be_in(require(f.get("sex"), "Sex").upper()[:1], VALID_SEX, "Sex")
    address = require(f.get("address"), "Address")
    license_type   = must_be_in(require(f.get("license_type"),   "License type"),   VALID_LICENSE_TYPES,  "License type")
    license_status = must_be_in(require(f.get("license_status"), "License status").lower(), VALID_LICENSE_STATUS, "License status")
    issued  = parse_date(f.get("license_issuance_date"),   "Issuance date")
    expires = parse_date(f.get("license_expiration_date"), "Expiration date")

    if dob > date.today():
        raise ValidationError("Date of birth cannot be in the future.")
    
    # Calculate exact age on the date the license was issued
    age_at_issuance = issued.year - dob.year - ((issued.month, issued.day) < (dob.month, dob.day))
    
    if license_type == "Student Permit" and age_at_issuance < 16:
        raise ValidationError("Driver must be at least 16 years old at issuance for a Student Permit.")
    elif license_type == "Non-Professional" and age_at_issuance < 17:
        raise ValidationError("Driver must be at least 17 years old at issuance for a Non-Professional license.")
    elif license_type == "Professional" and age_at_issuance < 18:
        raise ValidationError("Driver must be at least 18 years old at issuance for a Professional license.")
        
    if age_at_issuance > 120:
        raise ValidationError("Date of birth is unrealistic.")
    
    current_age = date.today().year - dob.year - ((date.today().month, date.today().day) < (dob.month, dob.day))

    if current_age > 120:
        raise ValidationError("Date of birth is unrealistic.")
    
    if expires < issued:
        raise ValidationError("Expiration date must be on or after issuance date.")
    if issued < dob:
        raise ValidationError("Issuance date cannot precede date of birth.")

    return dict(
        license_number=license_number, first_name=first_name, middle_name=middle_name,
        last_name=last_name, date_of_birth=dob, sex=sex, address=address,
        license_type=license_type, license_status=license_status,
        license_issuance_date=issued, license_expiration_date=expires,
    )


@app.route("/drivers/add", methods=["POST"])
def drivers_add():
    try:
        d = _validate_driver(request.form)
        execute(
            """INSERT INTO driver
               (license_number, first_name, middle_name, last_name,
                date_of_birth, sex, address, license_type,
                license_status, license_issuance_date, license_expiration_date)
               VALUES (%(license_number)s,%(first_name)s,%(middle_name)s,%(last_name)s,
                       %(date_of_birth)s,%(sex)s,%(address)s,%(license_type)s,
                       %(license_status)s,%(license_issuance_date)s,%(license_expiration_date)s)""",
            d,
        )
        flash("Driver added successfully.", "success")
    except ValidationError as e:
        flash(str(e), "danger")
    except Error as e:
        flash(db_error_message(e), "danger")
    return redirect(url_for("drivers"))


@app.route("/drivers/edit", methods=["POST"])
def drivers_edit():
    try:
        d = _validate_driver(request.form, is_edit=True)
        existing = query("SELECT 1 FROM driver WHERE license_number=%s",
                         (d["license_number"],), fetchone=True)
        if not existing:
            raise ValidationError("Driver not found.")
        execute(
            """UPDATE driver SET
               first_name=%(first_name)s, middle_name=%(middle_name)s, last_name=%(last_name)s,
               date_of_birth=%(date_of_birth)s, sex=%(sex)s, address=%(address)s,
               license_type=%(license_type)s, license_status=%(license_status)s,
               license_issuance_date=%(license_issuance_date)s,
               license_expiration_date=%(license_expiration_date)s
               WHERE license_number=%(license_number)s""",
            d,
        )
        flash("Driver updated.", "success")
    except ValidationError as e:
        flash(str(e), "danger")
    except Error as e:
        flash(db_error_message(e), "danger")
    return redirect(url_for("drivers"))


@app.route("/drivers/delete/<license_number>")
def drivers_delete(license_number):
    try:
        existing = query("SELECT 1 FROM driver WHERE license_number=%s",
                         (license_number,), fetchone=True)
        if not existing:
            flash("Driver not found.", "danger")
            return redirect(url_for("drivers"))
        execute("DELETE FROM driver WHERE license_number=%s", (license_number,))
        flash("Driver deleted.", "success")
    except Error as e:
        flash(db_error_message(e), "danger")
    return redirect(url_for("drivers"))


# ── VEHICLES ─────────────────────────────────────────────────────────────────

@app.route("/vehicles")
def vehicles():
    q = clean(request.args.get("q"))
    sql = """SELECT v.*, d.first_name AS owner_first_name, d.last_name AS owner_last_name
             FROM vehicle v JOIN driver d ON v.license_number = d.license_number"""
    params = []
    if q:
        sql += """ WHERE v.plate_number LIKE %s
                      OR v.chassis_number LIKE %s
                      OR v.make LIKE %s
                      OR v.model LIKE %s
                      OR d.last_name LIKE %s"""
        like = f"%{q}%"
        params = [like, like, like, like, like]
    sql += " ORDER BY v.plate_number"
    rows = query(sql, params)
    drivers_list = query("SELECT license_number, first_name, last_name FROM driver ORDER BY last_name")
    return render_template("vehicles.html",
                           rows=rows, drivers_list=drivers_list, search=q or "")


def _validate_vehicle(f, *, is_edit=False):
    # Normalize before validation: uppercase letters, collapse extra whitespace.
    # This lets the same regex accept "abc 1234" and "ABC  1234".
    plate   = re.sub(r"\s+", " ", require(f.get("plate_number"),  "Plate number").upper()).strip()
    chassis = require(f.get("chassis_number"), "Chassis number").upper()
    engine  = require(f.get("engine_number"),  "Engine number")
    if not PLATE_RE.match(plate):
        raise ValidationError(
            "Plate number must follow the format AAA NNNN "
            "(e.g. ABC 1234 — three letters, a space, then 3 or 4 digits)."
        )
    if not CHASSIS_RE.match(chassis):
        raise ValidationError(
            "Chassis number must follow the format AAA-NNN "
            "(e.g. CHS-001 — 2 to 5 uppercase letters, dash, then 3 to 8 digits)."
        )
    vehicle_type   = require(f.get("vehicle_type"), "Vehicle type")
    ownership_type = must_be_in(require(f.get("ownership_type"), "Ownership").lower(),
                                VALID_OWNERSHIP, "Ownership")
    make  = require(f.get("make"),  "Make")
    model = require(f.get("model"), "Model")
    year  = parse_int(f.get("year"), "Year", min_v=1900, max_v=date.today().year + 1)
    color = require(f.get("color"), "Color")
    franchise = clean(f.get("franchise_number"))
    license_number = require(f.get("license_number"), "Owner license number")

    if ownership_type == "public" and not franchise:
        raise ValidationError("Public vehicles must have a franchise number.")
    if ownership_type == "private" and franchise:
        raise ValidationError("Private vehicles must not have a franchise number.")

    if not query("SELECT 1 FROM driver WHERE license_number=%s",
                 (license_number,), fetchone=True):
        raise ValidationError("Owner license number does not exist.")

    return dict(
        plate_number=plate, chassis_number=chassis, engine_number=engine,
        vehicle_type=vehicle_type, ownership_type=ownership_type,
        make=make, model=model, year=year, color=color,
        franchise_number=franchise, license_number=license_number,
    )


@app.route("/vehicles/add", methods=["POST"])
def vehicles_add():
    try:
        v = _validate_vehicle(request.form)
        execute(
            """INSERT INTO vehicle
               (plate_number, chassis_number, engine_number, vehicle_type,
                ownership_type, make, model, year, color, franchise_number, license_number)
               VALUES (%(plate_number)s,%(chassis_number)s,%(engine_number)s,%(vehicle_type)s,
                       %(ownership_type)s,%(make)s,%(model)s,%(year)s,%(color)s,
                       %(franchise_number)s,%(license_number)s)""",
            v,
        )
        flash("Vehicle added.", "success")
    except ValidationError as e:
        flash(str(e), "danger")
    except Error as e:
        flash(db_error_message(e), "danger")
    return redirect(url_for("vehicles"))


@app.route("/vehicles/edit", methods=["POST"])
def vehicles_edit():
    try:
        v = _validate_vehicle(request.form, is_edit=True)
        
        # Fetch the current state of the vehicle before making changes
        current_vehicle = query(
            "SELECT license_number FROM vehicle WHERE plate_number=%s AND chassis_number=%s",
            (v["plate_number"], v["chassis_number"]), fetchone=True
        )
        
        if not current_vehicle:
            raise ValidationError("Vehicle not found.")
            
        # If the ownership (license_number) is being changed, enforce the rules
        if current_vehicle["license_number"] != v["license_number"]:
            
            # Check for active registrations
            active_reg = query(
                """SELECT 1 FROM vehicle_registration 
                   WHERE plate_number=%s AND chassis_number=%s AND registration_status = 'active' LIMIT 1""",
                (v["plate_number"], v["chassis_number"]), fetchone=True
            )
            if active_reg:
                raise ValidationError("Cannot change ownership: Vehicle has an active registration. It must be unregistered first.")
                
            # Check for unpaid violations
            unpaid_viol = query(
                """SELECT 1 FROM traffic_violation 
                   WHERE plate_number=%s AND chassis_number=%s AND violation_status = 'unpaid' LIMIT 1""",
                (v["plate_number"], v["chassis_number"]), fetchone=True
            )
            if unpaid_viol:
                raise ValidationError("Cannot change ownership: Vehicle has unpaid violations.")
            
        # If all checks pass, execute the update
        execute(
            """UPDATE vehicle SET
               engine_number=%(engine_number)s, vehicle_type=%(vehicle_type)s,
               ownership_type=%(ownership_type)s, make=%(make)s, model=%(model)s,
               year=%(year)s, color=%(color)s, franchise_number=%(franchise_number)s,
               license_number=%(license_number)s
               WHERE plate_number=%(plate_number)s AND chassis_number=%(chassis_number)s""",
            v,
        )
        flash("Vehicle updated.", "success")
        
    except ValidationError as e:
        flash(str(e), "danger")
    except Error as e:
        flash(db_error_message(e), "danger")
    return redirect(url_for("vehicles"))


@app.route("/vehicles/delete/<plate_number>/<chassis_number>")
def vehicles_delete(plate_number, chassis_number):
    try:
        if not query(
            "SELECT 1 FROM vehicle WHERE plate_number=%s AND chassis_number=%s",
            (plate_number, chassis_number), fetchone=True
        ):
            flash("Vehicle not found.", "danger")
            return redirect(url_for("vehicles"))
        execute("DELETE FROM vehicle WHERE plate_number=%s AND chassis_number=%s",
                (plate_number, chassis_number))
        flash("Vehicle deleted.", "success")
    except Error as e:
        flash(db_error_message(e), "danger")
    return redirect(url_for("vehicles"))


# ── REGISTRATIONS ────────────────────────────────────────────────────────────

@app.route("/registrations")
def registrations():
    q = clean(request.args.get("q"))
    sql = """SELECT vr.*, v.make, v.model, v.year AS vehicle_year,
                    d.first_name AS owner_first_name, d.last_name AS owner_last_name
             FROM vehicle_registration vr
             JOIN vehicle v ON vr.plate_number = v.plate_number
                           AND vr.chassis_number = v.chassis_number
             JOIN driver d ON v.license_number = d.license_number"""
    params = []
    if q:
        sql += """ WHERE vr.registration_number LIKE %s
                      OR vr.plate_number LIKE %s
                      OR d.last_name LIKE %s"""
        like = f"%{q}%"
        params = [like, like, like]
    sql += " ORDER BY vr.registration_date DESC"
    rows = query(sql, params)
    vehicles_list = query("""
        SELECT plate_number, chassis_number, make, model
        FROM vehicle ORDER BY plate_number
    """)
    return render_template("registrations.html",
                           rows=rows, vehicles_list=vehicles_list, search=q or "")


def _validate_registration(f, *, is_edit=False):
    reg_num = require(f.get("registration_number"), "Registration number").upper()
    if not REGISTRATION_RE.match(reg_num):
        raise ValidationError(
            "Registration number must follow the format REG-YYYY-NNNNN "
            "(e.g. REG-2025-00001)."
        )
    reg_date = parse_date(f.get("registration_date"), "Registration date")
    exp_date = parse_date(f.get("expiration_date"),   "Expiration date")
    status   = must_be_in(require(f.get("registration_status"), "Status").lower(),
                          VALID_REG_STATUS, "Status")
    if exp_date < reg_date:
        raise ValidationError("Expiration date must be on or after registration date.")

    out = dict(registration_number=reg_num, registration_date=reg_date,
               expiration_date=exp_date, registration_status=status)

    if not is_edit:
        vk = require(f.get("vehicle_key"), "Vehicle")
        if "|" not in vk:
            raise ValidationError("Invalid vehicle selection.")
        plate, chassis = vk.split("|", 1)
        plate, chassis = plate.strip(), chassis.strip()
        if not query(
            "SELECT 1 FROM vehicle WHERE plate_number=%s AND chassis_number=%s",
            (plate, chassis), fetchone=True
        ):
            raise ValidationError("Selected vehicle does not exist.")
        out["plate_number"] = plate
        out["chassis_number"] = chassis
    return out


@app.route("/registrations/add", methods=["POST"])
def registrations_add():
    try:
        r = _validate_registration(request.form)
        execute(
            """INSERT INTO vehicle_registration
               (registration_number, registration_date, expiration_date,
                registration_status, plate_number, chassis_number)
               VALUES (%(registration_number)s,%(registration_date)s,%(expiration_date)s,
                       %(registration_status)s,%(plate_number)s,%(chassis_number)s)""",
            r,
        )
        flash("Registration added.", "success")
    except ValidationError as e:
        flash(str(e), "danger")
    except Error as e:
        flash(db_error_message(e), "danger")
    return redirect(url_for("registrations"))


@app.route("/registrations/edit", methods=["POST"])
def registrations_edit():
    try:
        r = _validate_registration(request.form, is_edit=True)
        if not query("SELECT 1 FROM vehicle_registration WHERE registration_number=%s",
                     (r["registration_number"],), fetchone=True):
            raise ValidationError("Registration not found.")
        execute(
            """UPDATE vehicle_registration SET
               registration_date=%(registration_date)s,
               expiration_date=%(expiration_date)s,
               registration_status=%(registration_status)s
               WHERE registration_number=%(registration_number)s""",
            r,
        )
        flash("Registration updated.", "success")
    except ValidationError as e:
        flash(str(e), "danger")
    except Error as e:
        flash(db_error_message(e), "danger")
    return redirect(url_for("registrations"))


@app.route("/registrations/delete/<registration_number>")
def registrations_delete(registration_number):
    try:
        if not query("SELECT 1 FROM vehicle_registration WHERE registration_number=%s",
                     (registration_number,), fetchone=True):
            flash("Registration not found.", "danger")
            return redirect(url_for("registrations"))
        execute("DELETE FROM vehicle_registration WHERE registration_number=%s",
                (registration_number,))
        flash("Registration deleted.", "success")
    except Error as e:
        flash(db_error_message(e), "danger")
    return redirect(url_for("registrations"))


# ── VIOLATIONS ───────────────────────────────────────────────────────────────

@app.route("/violations")
def violations():
    q = clean(request.args.get("q"))
    sql = """SELECT tv.*, tvt.violation_type,
                    d.first_name AS driver_first_name, d.last_name AS driver_last_name
             FROM traffic_violation tv
             LEFT JOIN traffic_violation_type tvt
                    ON tv.traffic_violation_id = tvt.traffic_violation_id
             JOIN driver d ON tv.license_number = d.license_number"""
    params = []
    if q:
        sql += """ WHERE tv.plate_number LIKE %s
                      OR tv.location LIKE %s
                      OR d.last_name LIKE %s
                      OR tvt.violation_type LIKE %s"""
        like = f"%{q}%"
        params = [like, like, like, like]
    sql += " ORDER BY tv.date DESC, tv.time DESC"
    rows = query(sql, params)

    for r in rows:
        if hasattr(r.get("time"), "total_seconds"):
            r["time"] = str(r["time"])

    drivers_list  = query("SELECT license_number, first_name, last_name FROM driver ORDER BY last_name")
    vehicles_list = query("SELECT plate_number, chassis_number, make, model FROM vehicle ORDER BY plate_number")
    return render_template("violations.html", rows=rows,
                           drivers_list=drivers_list, vehicles_list=vehicles_list,
                           search=q or "")


def _validate_violation(f, *, is_edit=False):
    status = must_be_in(require(f.get("violation_status"), "Violation status").lower(),
                        VALID_VIOL_STATUS, "Violation status")
    fine     = parse_decimal(f.get("total_fine_amount"), "Fine amount", min_v=0)
    location = require(f.get("location"), "Location")
    d        = parse_date(f.get("date"), "Date")
    t        = parse_time(f.get("time"), "Time")

    if d > date.today():
        raise ValidationError("Violation date cannot be in the future.")

    out = dict(
        violation_status=status,
        apprehending_officer=clean(f.get("apprehending_officer")),
        total_fine_amount=fine, location=location, date=d, time=t,
        violation_type=clean(f.get("violation_type")),
    )

    if not is_edit:
        license_number = require(f.get("license_number"), "Driver")
        if not query("SELECT 1 FROM driver WHERE license_number=%s",
                     (license_number,), fetchone=True):
            raise ValidationError("Driver does not exist.")
        vk = require(f.get("vehicle_key"), "Vehicle")
        if "|" not in vk:
            raise ValidationError("Invalid vehicle selection.")
        plate, chassis = vk.split("|", 1)
        plate, chassis = plate.strip(), chassis.strip()
        if not query("SELECT 1 FROM vehicle WHERE plate_number=%s AND chassis_number=%s",
                     (plate, chassis), fetchone=True):
            raise ValidationError("Selected vehicle does not exist.")
        out["license_number"] = license_number
        out["plate_number"]   = plate
        out["chassis_number"] = chassis
    return out


@app.route("/violations/add", methods=["POST"])
def violations_add():
    try:
        v = _validate_violation(request.form)
        vt = v.pop("violation_type")
        vid = execute(
            """INSERT INTO traffic_violation
               (violation_status, apprehending_officer, total_fine_amount,
                location, date, time, license_number, plate_number, chassis_number)
               VALUES (%(violation_status)s,%(apprehending_officer)s,%(total_fine_amount)s,
                       %(location)s,%(date)s,%(time)s,%(license_number)s,
                       %(plate_number)s,%(chassis_number)s)""",
            v,
        )
        if vt:
            execute(
                "INSERT INTO traffic_violation_type (traffic_violation_id, violation_type) VALUES (%s,%s)",
                (vid, vt),
            )
        flash("Violation recorded.", "success")
    except ValidationError as e:
        flash(str(e), "danger")
    except Error as e:
        flash(db_error_message(e), "danger")
    return redirect(url_for("violations"))


@app.route("/violations/edit", methods=["POST"])
def violations_edit():
    try:
        vid = parse_int(request.form.get("traffic_violation_id"), "Violation ID")
        if not query("SELECT 1 FROM traffic_violation WHERE traffic_violation_id=%s",
                     (vid,), fetchone=True):
            raise ValidationError("Violation not found.")
        v = _validate_violation(request.form, is_edit=True)
        vt = v.pop("violation_type")
        v["traffic_violation_id"] = vid
        execute(
            """UPDATE traffic_violation SET
               violation_status=%(violation_status)s,
               apprehending_officer=%(apprehending_officer)s,
               total_fine_amount=%(total_fine_amount)s,
               location=%(location)s, date=%(date)s, time=%(time)s
               WHERE traffic_violation_id=%(traffic_violation_id)s""",
            v,
        )
        existing = query(
            "SELECT violation_type FROM traffic_violation_type WHERE traffic_violation_id=%s",
            (vid,), fetchone=True
        )
        if vt:
            if existing:
                execute(
                    "UPDATE traffic_violation_type SET violation_type=%s WHERE traffic_violation_id=%s",
                    (vt, vid),
                )
            else:
                execute(
                    "INSERT INTO traffic_violation_type (traffic_violation_id, violation_type) VALUES (%s,%s)",
                    (vid, vt),
                )
        else:
            execute("DELETE FROM traffic_violation_type WHERE traffic_violation_id=%s", (vid,))
        flash("Violation updated.", "success")
    except ValidationError as e:
        flash(str(e), "danger")
    except Error as e:
        flash(db_error_message(e), "danger")
    return redirect(url_for("violations"))


@app.route("/violations/delete/<int:vid>")
def violations_delete(vid):
    try:
        if not query("SELECT 1 FROM traffic_violation WHERE traffic_violation_id=%s",
                     (vid,), fetchone=True):
            flash("Violation not found.", "danger")
            return redirect(url_for("violations"))
        execute("DELETE FROM traffic_violation_type WHERE traffic_violation_id=%s", (vid,))
        execute("DELETE FROM traffic_violation WHERE traffic_violation_id=%s", (vid,))
        flash("Violation deleted.", "success")
    except Error as e:
        flash(db_error_message(e), "danger")
    return redirect(url_for("violations"))


# ══════════════════════════════════════════════════════════════════════════════
#  REPORTS
# ══════════════════════════════════════════════════════════════════════════════

@app.route("/reports")
def reports():
    drivers_list  = query("SELECT license_number, first_name, last_name FROM driver ORDER BY last_name")
    return render_template("reports.html", drivers_list=drivers_list)


def _render_report(title, report_id, rows, params_used=None, message=None):
    return render_template(
        "report_result.html",
        report_title=title, report_id=report_id, rows=rows,
        params_used=params_used or {}, message=message,
    )


@app.route("/reports/drivers_filtered")
def report_drivers_filtered():
    """Report 1: Drivers filtered by license type, status, age range, sex."""
    lt      = clean(request.args.get("license_type"))
    ls      = clean(request.args.get("license_status"))
    sex_raw = clean(request.args.get("sex"))
    sex     = sex_raw.upper()[:1] if sex_raw else None
    age_min = clean(request.args.get("age_min"))
    age_max = clean(request.args.get("age_max"))

    try:
        if lt:  must_be_in(lt, VALID_LICENSE_TYPES,  "License type")
        if ls:  must_be_in(ls.lower(), VALID_LICENSE_STATUS, "License status")
        if sex: must_be_in(sex, VALID_SEX, "Sex")
        age_min_v = parse_int(age_min, "Min age", min_v=0, max_v=150) if age_min else None
        age_max_v = parse_int(age_max, "Max age", min_v=0, max_v=150) if age_max else None
        if age_min_v is not None and age_max_v is not None and age_min_v > age_max_v:
            raise ValidationError("Min age must be ≤ Max age.")
    except ValidationError as e:
        return _render_report("Registered Drivers (Filtered)", 1, [], message=str(e))

    sql = """SELECT license_number, first_name, middle_name, last_name, sex,
                    TIMESTAMPDIFF(YEAR, date_of_birth, CURDATE()) AS age,
                    address, license_type, license_status, license_expiration_date
             FROM driver WHERE 1=1"""
    params = []
    if lt:
        sql += " AND license_type = %s"; params.append(lt)
    if ls:
        sql += " AND license_status = %s"; params.append(ls.lower())
    if sex:
        sql += " AND sex = %s"; params.append(sex)
    if age_min:
        sql += " AND TIMESTAMPDIFF(YEAR, date_of_birth, CURDATE()) >= %s"; params.append(int(age_min))
    if age_max:
        sql += " AND TIMESTAMPDIFF(YEAR, date_of_birth, CURDATE()) <= %s"; params.append(int(age_max))
    sql += " ORDER BY last_name, first_name"

    rows = query(sql, params)
    params_used = {k: v for k, v in {
        "License Type": lt, "Status": ls, "Sex": sex,
        "Min Age": age_min, "Max Age": age_max
    }.items() if v}
    return _render_report("Registered Drivers (Filtered)", 1, rows, params_used)


@app.route("/reports/vehicles_by_driver")
def report_vehicles_by_driver():
    """Report 2: Vehicles owned by a given driver."""
    ln = clean(request.args.get("license_number"))
    if not ln:
        return _render_report("Vehicles Owned by Driver", 2, [],
                              message="Please provide a license number.")
    drv = query("SELECT first_name, last_name FROM driver WHERE license_number=%s",
                (ln,), fetchone=True)
    if not drv:
        return _render_report(f"Vehicles Owned by Driver {ln}", 2, [],
                              message=f"No driver found with license number '{ln}'.")
    rows = query("""
        SELECT v.plate_number, v.chassis_number, v.engine_number,
               v.vehicle_type, v.ownership_type, v.make, v.model,
               v.year, v.color, v.franchise_number,
               d.first_name AS owner_first_name, d.last_name AS owner_last_name
        FROM vehicle v JOIN driver d ON v.license_number = d.license_number
        WHERE d.license_number = %s ORDER BY v.plate_number
    """, (ln,))
    title = f"Vehicles Owned by {drv['first_name']} {drv['last_name']} ({ln})"
    return _render_report(title, 2, rows, {"License Number": ln})


@app.route("/reports/expired_registrations")
def report_expired_registrations():
    """Report 3: Vehicles with expired registrations as of a given date."""
    as_of_raw = clean(request.args.get("as_of_date"))
    if not as_of_raw:
        as_of = date.today()
    else:
        try:
            as_of = parse_date(as_of_raw, "As-of date")
        except ValidationError as e:
            return _render_report("Expired Registrations", 3, [], message=str(e))

    rows = query("""
        SELECT v.plate_number, v.chassis_number, v.vehicle_type, v.make, v.model, v.year,
               d.first_name AS owner_first_name, d.last_name AS owner_last_name,
               d.license_number, vr.registration_number,
               vr.expiration_date, vr.registration_status
        FROM vehicle_registration vr
        JOIN vehicle v ON vr.plate_number = v.plate_number
                       AND vr.chassis_number = v.chassis_number
        JOIN driver d ON v.license_number = d.license_number
        WHERE vr.expiration_date < %s
        ORDER BY vr.expiration_date DESC
    """, (as_of,))
    return _render_report(f"Expired Registrations (as of {as_of})", 3,
                          rows, {"As of Date": str(as_of)})


@app.route("/reports/invalid_licenses")
def report_invalid_licenses():
    """Report 4: Drivers with expired or suspended licenses."""
    status = clean(request.args.get("license_status"))
    sql = """SELECT license_number, first_name, middle_name, last_name,
                    license_type, license_status, license_expiration_date,
                    TIMESTAMPDIFF(YEAR, date_of_birth, CURDATE()) AS age, address
             FROM driver
             WHERE license_status IN ('expired','suspended')"""
    params = []
    if status:
        s = status.lower()
        if s not in {"expired", "suspended"}:
            return _render_report("Drivers with Expired / Suspended Licenses", 4, [],
                                  message="Filter must be 'expired' or 'suspended'.")
        sql += " AND license_status=%s"
        params.append(s)
    sql += " ORDER BY license_status, last_name"
    rows = query(sql, params)
    used = {"Status filter": status} if status else {"Status filter": "expired or suspended"}
    return _render_report("Drivers with Expired / Suspended Licenses", 4, rows, used)


@app.route("/reports/violations_by_driver")
def report_violations_by_driver():
    """Report 5: Violations by a driver within a date range."""
    ln = clean(request.args.get("license_number"))
    d1 = clean(request.args.get("date_from")) or "2000-01-01"
    d2 = clean(request.args.get("date_to"))   or str(date.today())

    if not ln:
        return _render_report("Violations by Driver", 5, [],
                              message="Please provide a license number.")
    try:
        d1d = parse_date(d1, "Date from")
        d2d = parse_date(d2, "Date to")
    except ValidationError as e:
        return _render_report("Violations by Driver", 5, [], message=str(e))
    if d1d > d2d:
        return _render_report("Violations by Driver", 5, [],
                              message="'From' date must be on or before 'To' date.")

    drv = query("SELECT first_name, last_name FROM driver WHERE license_number=%s",
                (ln,), fetchone=True)
    if not drv:
        return _render_report(f"Violations by Driver {ln}", 5, [],
                              message=f"No driver found with license number '{ln}'.")

    rows = query("""
        SELECT tv.traffic_violation_id, tv.date, tv.time, tv.location,
               tv.apprehending_officer, tv.violation_status,
               tv.total_fine_amount, tv.plate_number, tvt.violation_type
        FROM traffic_violation tv
        LEFT JOIN traffic_violation_type tvt
               ON tv.traffic_violation_id = tvt.traffic_violation_id
        WHERE tv.license_number = %s AND tv.date BETWEEN %s AND %s
        ORDER BY tv.date, tv.time
    """, (ln, d1d, d2d))
    for r in rows:
        if hasattr(r.get("time"), "total_seconds"):
            r["time"] = str(r["time"])
    title = f"Violations by {drv['first_name']} {drv['last_name']} ({d1d} → {d2d})"
    return _render_report(title, 5, rows,
                          {"License Number": ln, "From": str(d1d), "To": str(d2d)})


@app.route("/reports/violations_per_type")
def report_violations_per_type():
    """Report 6: Violation count per type for a given year."""
    yr_raw = clean(request.args.get("year"))
    if not yr_raw:
        return _render_report("Violations per Type", 6, [],
                              message="Please provide a year.")
    try:
        yr = parse_int(yr_raw, "Year", min_v=1900, max_v=2100)
    except ValidationError as e:
        return _render_report("Violations per Type", 6, [], message=str(e))

    rows = query("""
        SELECT tvt.violation_type, COUNT(*) AS total_violations
        FROM traffic_violation_type tvt
        JOIN traffic_violation tv ON tvt.traffic_violation_id = tv.traffic_violation_id
        WHERE YEAR(tv.date) = %s
        GROUP BY tvt.violation_type
        ORDER BY total_violations DESC, tvt.violation_type
    """, (yr,))
    return _render_report(f"Violations per Type ({yr})", 6, rows, {"Year": yr})


@app.route("/reports/vehicles_in_violations")
def report_vehicles_in_violations():
    """Report 7: Vehicles involved in violations in a city/region."""
    loc = clean(request.args.get("location"))
    if not loc:
        return _render_report("Vehicles in Violations", 7, [],
                              message="Please provide a city or region.")
    rows = query("""
        SELECT DISTINCT v.plate_number, v.chassis_number, v.make, v.model,
               v.year, v.color, v.vehicle_type,
               d.first_name AS owner_first_name, d.last_name AS owner_last_name,
               tv.location
        FROM traffic_violation tv
        JOIN vehicle v ON tv.plate_number = v.plate_number
                      AND tv.chassis_number = v.chassis_number
        JOIN driver d ON v.license_number = d.license_number
        WHERE tv.location LIKE %s
        ORDER BY v.plate_number
    """, (f"%{loc}%",))
    return _render_report(f"Vehicles in Violations near '{loc}'", 7,
                          rows, {"Location": loc})


# ── Dashboard stats ──────────────────────────────────────────────────────────

@app.route("/api/stats")
def api_stats():
    stats = query("""
        SELECT
          (SELECT COUNT(*) FROM driver)                                                 AS total_drivers,
          (SELECT COUNT(*) FROM vehicle)                                                AS total_vehicles,
          (SELECT COUNT(*) FROM vehicle_registration)                                   AS total_registrations,
          (SELECT COUNT(*) FROM traffic_violation)                                      AS total_violations,
          (SELECT COUNT(*) FROM traffic_violation WHERE violation_status='unpaid')      AS unpaid_violations,
          (SELECT COUNT(*) FROM driver WHERE license_status IN ('expired','suspended','revoked'))
                                                                                        AS expired_licenses,
          (SELECT COUNT(*) FROM vehicle_registration WHERE expiration_date < CURDATE()) AS expired_registrations
    """, fetchone=True)
    return jsonify(stats)


# ── Recent activity feed ─────────────────────────────────────────────────────

@app.route("/api/recent")
def api_recent():
    """Latest 5 violations for the dashboard activity feed."""
    rows = query("""
        SELECT tv.traffic_violation_id, tv.date, tv.time,
               tv.violation_status, tv.total_fine_amount, tv.location,
               tv.plate_number, tvt.violation_type,
               CONCAT(d.first_name,' ',d.last_name) AS driver_name
        FROM traffic_violation tv
        LEFT JOIN traffic_violation_type tvt
               ON tv.traffic_violation_id = tvt.traffic_violation_id
        JOIN driver d ON tv.license_number = d.license_number
        ORDER BY tv.date DESC, tv.time DESC
        LIMIT 5
    """)
    for r in rows:
        # serialize date/time so jsonify can handle them
        if r.get("date"):   r["date"] = str(r["date"])
        if r.get("time") is not None:
            r["time"] = str(r["time"])
    return jsonify(rows)


# ── Error handlers ───────────────────────────────────────────────────────────

@app.errorhandler(404)
def not_found(e):
    return render_template("error.html",
                           error_title="Page not found",
                           error_message="The page you requested does not exist."), 404


@app.errorhandler(500)
def server_error(e):
    return render_template("error.html",
                           error_title="Server error",
                           error_message=str(e)), 500


# ──────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(debug=True, port=5000)