
--  LTO Information Management System
--  CMSC 127 – Milestone 3 


DROP DATABASE IF EXISTS lto_db;
CREATE DATABASE IF NOT EXISTS lto_db;
USE lto_db;


--  TABLE DEFINITIONS


CREATE TABLE driver (
    license_number          VARCHAR(20)  NOT NULL,
    first_name              VARCHAR(50)  NOT NULL,
    middle_name             VARCHAR(50),
    last_name               VARCHAR(50)  NOT NULL,
    date_of_birth           DATE         NOT NULL,
    sex                     VARCHAR(10)  NOT NULL,
    address                 VARCHAR(255) NOT NULL,
    license_type            VARCHAR(50)  NOT NULL,
    license_status          VARCHAR(20)  NOT NULL,
    license_issuance_date   DATE         NOT NULL,
    license_expiration_date DATE         NOT NULL,
    PRIMARY KEY (license_number)
);

CREATE TABLE vehicle (
    plate_number     VARCHAR(15)  NOT NULL,
    chassis_number   VARCHAR(50)  NOT NULL,
    engine_number    VARCHAR(50)  NOT NULL,
    vehicle_type     VARCHAR(50)  NOT NULL,
    ownership_type   VARCHAR(50)  NOT NULL,
    make             VARCHAR(50)  NOT NULL,
    model            VARCHAR(50)  NOT NULL,
    year             INT          NOT NULL,
    color            VARCHAR(20)  NOT NULL,
    franchise_number VARCHAR(50),
    license_number   VARCHAR(20)  NOT NULL,
    PRIMARY KEY (plate_number, chassis_number),
    CONSTRAINT fk_vehicle_driver
        FOREIGN KEY (license_number)
        REFERENCES driver (license_number)
);

CREATE TABLE vehicle_registration (
    registration_number VARCHAR(50)  NOT NULL,
    registration_date   DATE         NOT NULL,
    expiration_date     DATE         NOT NULL,
    registration_status VARCHAR(20)  NOT NULL,
    plate_number        VARCHAR(15)  NOT NULL,
    chassis_number      VARCHAR(50)  NOT NULL,
    PRIMARY KEY (registration_number),
    CONSTRAINT fk_registration_vehicle
        FOREIGN KEY (plate_number, chassis_number)
        REFERENCES vehicle (plate_number, chassis_number)
);

CREATE TABLE traffic_violation (
    traffic_violation_id  INT          NOT NULL AUTO_INCREMENT,
    violation_status      VARCHAR(20)  NOT NULL,
    apprehending_officer  VARCHAR(100),
    total_fine_amount     DECIMAL(10, 2) NOT NULL,
    location              VARCHAR(255) NOT NULL,
    date                  DATE         NOT NULL,
    time                  TIME         NOT NULL,
    license_number        VARCHAR(20)  NOT NULL,
    plate_number          VARCHAR(15)  NOT NULL,
    chassis_number        VARCHAR(50)  NOT NULL,
    PRIMARY KEY (traffic_violation_id),
    CONSTRAINT fk_violation_driver
        FOREIGN KEY (license_number)
        REFERENCES driver (license_number),
    CONSTRAINT fk_violation_vehicle
        FOREIGN KEY (plate_number, chassis_number)
        REFERENCES vehicle (plate_number, chassis_number)
);

CREATE TABLE traffic_violation_type (
    traffic_violation_id INT          NOT NULL,   
    violation_type       VARCHAR(100) NOT NULL,
    PRIMARY KEY (traffic_violation_id, violation_type),
    CONSTRAINT fk_violation_type
        FOREIGN KEY (traffic_violation_id)
        REFERENCES traffic_violation (traffic_violation_id)
);


--  DUMMY DATA


INSERT INTO driver (license_number, first_name, middle_name, last_name, date_of_birth, sex, address, license_type, license_status, license_issuance_date, license_expiration_date) VALUES
    ('N01-90-123456', 'Juan',  'Santos',   'Dela Cruz',  '1990-05-15', 'M', '123 Rizal St., Manila',        'Non-Professional', 'valid',     '2023-01-10', '2028-01-10'),
    ('P02-85-654321', 'Maria', 'Lopez',    'Reyes',      '1985-08-22', 'F', '456 Mabini Ave., Quezon City', 'Professional',     'valid',     '2022-06-01', '2027-06-01'),
    ('N03-78-111222', 'Pedro', 'Garcia',   'Santos',     '1978-03-10', 'M', '789 Bonifacio Rd., Cebu',      'Non-Professional', 'expired',   '2018-04-01', '2023-04-01'),
    ('S04-02-333444', 'Ana',   'Cruz',     'Garcia',     '2002-11-30', 'F', '321 Luna St., Davao',          'Student Permit',   'valid',     '2024-01-15', '2025-01-15'),
    ('P05-95-555666', 'Marco', 'Bautista', 'Villanueva', '1995-07-04', 'M', '654 Aguinaldo Blvd., Cavite',  'Professional',     'suspended', '2020-09-01', '2025-09-01');

INSERT INTO vehicle (plate_number, chassis_number, engine_number, vehicle_type, ownership_type, make, model, year, color, franchise_number, license_number) VALUES
    ('ABC 1234', 'CHS-001', 'ENG-001', 'private car',            'private', 'Toyota',     'Vios',      2022, 'White',  NULL,       'N01-90-123456'),
    ('XYZ 5678', 'CHS-002', 'ENG-002', 'motorcycle',             'private', 'Honda',      'Click 125', 2021, 'Red',    NULL,       'P02-85-654321'),
    ('DEF 9012', 'CHS-003', 'ENG-003', 'public utility vehicle', 'public',  'Mitsubishi', 'L300',      2019, 'Yellow', 'FR-00123', 'P02-85-654321'),
    ('GHI 3456', 'CHS-004', 'ENG-004', 'private car',            'private', 'Ford',       'Ranger',    2020, 'Black',  NULL,       'P05-95-555666'),
    ('JKL 7890', 'CHS-005', 'ENG-005', 'motorcycle',             'private', 'Yamaha',     'Mio',       2023, 'Blue',   NULL,       'N01-90-123456');

INSERT INTO vehicle_registration (registration_number, registration_date, expiration_date, registration_status, plate_number, chassis_number) VALUES
    ('REG-2025-00001', '2025-01-15', '2026-01-15', 'active',  'ABC 1234', 'CHS-001'),
    ('REG-2024-00002', '2024-03-10', '2025-03-10', 'expired', 'XYZ 5678', 'CHS-002'),
    ('REG-2025-00003', '2025-02-20', '2026-02-20', 'active',  'DEF 9012', 'CHS-003'),
    ('REG-2023-00004', '2023-06-01', '2024-06-01', 'expired', 'GHI 3456', 'CHS-004'),
    ('REG-2025-00005', '2025-04-01', '2026-04-01', 'active',  'JKL 7890', 'CHS-005');

INSERT INTO traffic_violation (violation_status, apprehending_officer, total_fine_amount, location, date, time, license_number, plate_number, chassis_number) VALUES
    ('paid',      'Officer Reyes',    2000.00, 'EDSA, Quezon City',      '2024-03-01', '08:30:00', 'N01-90-123456', 'ABC 1234', 'CHS-001'),
    ('unpaid',    'Officer Santos',   5000.00, 'C5 Road, Taguig',        '2024-06-15', '14:15:00', 'N01-90-123456', 'ABC 1234', 'CHS-001'),
    ('unpaid',    NULL,                500.00, 'Ayala Ave., Makati',     '2024-09-20', '11:00:00', 'P02-85-654321', 'XYZ 5678', 'CHS-002'),
    ('unpaid',    'Officer Cruz',     2000.00, 'NLEX, Bulacan',          '2025-01-10', '07:45:00', 'P05-95-555666', 'GHI 3456', 'CHS-004'),
    ('contested', 'Officer Lim',      1500.00, 'Katipunan Ave., QC',     '2025-02-14', '09:20:00', 'N01-90-123456', 'JKL 7890', 'CHS-005'),
    ('unpaid',    'Officer Bautista', 2000.00, 'SLEX, Laguna',           '2025-03-05', '16:00:00', 'P05-95-555666', 'GHI 3456', 'CHS-004'),
    ('unpaid',    'Officer Torres',   5000.00, 'MacArthur Hwy., Manila', '2025-03-20', '13:30:00', 'P05-95-555666', 'GHI 3456', 'CHS-004');

INSERT INTO traffic_violation_type (traffic_violation_id, violation_type) VALUES
    (1, 'Overspeeding'),
    (2, 'Reckless Driving'),
    (3, 'Illegal Parking'),
    (4, 'Overspeeding'),
    (5, 'No Helmet'),
    (6, 'Overspeeding'),
    (7, 'Reckless Driving');


--  VIEWS


--  VIEW 1: All drivers with their age 

CREATE OR REPLACE VIEW view_drivers AS
SELECT
    license_number,
    first_name,
    middle_name,
    last_name,
    sex,
    TIMESTAMPDIFF(YEAR, date_of_birth, CURDATE()) AS age,
    address,
    license_type,
    license_status,
    license_issuance_date,
    license_expiration_date
FROM driver;

--  VIEW 2: All vehicles with their owner's info

CREATE OR REPLACE VIEW view_vehicles_with_owner AS
SELECT
    v.plate_number,
    v.chassis_number,
    v.engine_number,
    v.vehicle_type,
    v.ownership_type,
    v.make,
    v.model,
    v.year,
    v.color,
    v.franchise_number,
    d.license_number    AS owner_license_number,
    d.first_name        AS owner_first_name,
    d.last_name         AS owner_last_name
FROM vehicle v
JOIN driver d ON v.license_number = d.license_number;
 
--  VIEW 3: Vehicles with expired registrations

CREATE OR REPLACE VIEW view_expired_registrations AS
SELECT
    v.plate_number,
    v.chassis_number,
    v.vehicle_type,
    v.make,
    v.model,
    v.year,
    d.first_name        AS owner_first_name,
    d.last_name         AS owner_last_name,
    d.license_number,
    vr.registration_number,
    vr.registration_date,
    vr.expiration_date,
    vr.registration_status
FROM vehicle_registration vr
JOIN vehicle v ON vr.plate_number   = v.plate_number
              AND vr.chassis_number = v.chassis_number
JOIN driver  d ON v.license_number  = d.license_number
WHERE vr.expiration_date < CURDATE();
 
--  VIEW 4: Drivers with expired or suspended licenses

CREATE OR REPLACE VIEW view_invalid_licenses AS
SELECT
    license_number,
    first_name,
    middle_name,
    last_name,
    license_type,
    license_status,
    license_expiration_date,
    TIMESTAMPDIFF(YEAR, date_of_birth, CURDATE()) AS age,
    address
FROM driver
WHERE license_status IN ('expired', 'suspended');

--  VIEW 5: All traffic violations with violation type and driver info

CREATE OR REPLACE VIEW view_traffic_violations AS
SELECT
    tv.traffic_violation_id,
    tv.date,
    tv.time,
    tv.location,
    tv.apprehending_officer,
    tv.violation_status,
    tv.total_fine_amount,
    tv.license_number,
    d.first_name        AS driver_first_name,
    d.last_name         AS driver_last_name,
    tv.plate_number,
    tv.chassis_number,
    tvt.violation_type
FROM traffic_violation tv
LEFT JOIN traffic_violation_type tvt
       ON tv.traffic_violation_id = tvt.traffic_violation_id
JOIN driver d
       ON tv.license_number = d.license_number;

--  VIEW 6: Violation count per type per year
CREATE OR REPLACE VIEW view_violations_per_type_per_year AS
SELECT
    YEAR(tv.date)       AS violation_year,
    tvt.violation_type,
    COUNT(*)            AS total_violations
FROM traffic_violation_type tvt
JOIN traffic_violation tv
  ON tvt.traffic_violation_id = tv.traffic_violation_id
GROUP BY YEAR(tv.date), tvt.violation_type
ORDER BY violation_year DESC, total_violations DESC;
  
--  VIEW 7: Vehicles involved in violations with location info

CREATE OR REPLACE VIEW view_vehicles_in_violations AS
SELECT DISTINCT
    v.plate_number,
    v.chassis_number,
    v.make,
    v.model,
    v.year,
    v.color,
    v.vehicle_type,
    d.first_name        AS owner_first_name,
    d.last_name         AS owner_last_name,
    tv.location
FROM traffic_violation tv
JOIN vehicle v
  ON tv.plate_number   = v.plate_number
 AND tv.chassis_number = v.chassis_number
JOIN driver d
  ON v.license_number = d.license_number;

-- VIEW 8: Unpaid violations with driver and vehicle info
CREATE OR REPLACE VIEW view_unpaid_violations AS
SELECT 
    d.license_number,
    CONCAT(d.first_name, ' ', d.last_name) AS driver_name,
    tv.traffic_violation_id,
    tv.plate_number,
    tv.date AS violation_date,
    tv.total_fine_amount,
    tv.location
FROM driver d
JOIN traffic_violation tv ON d.license_number = tv.license_number
WHERE tv.violation_status = 'unpaid';

--  REPORTS


-- 1. View all registered drivers filtered by license type, license status, age range, sex

SELECT
    license_number,
    first_name,
    middle_name,
    last_name,
    sex,
    TIMESTAMPDIFF(YEAR, date_of_birth, CURDATE()) AS age,
    address,
    license_type,
    license_status,
    license_expiration_date
FROM driver
WHERE license_type   = 'Professional'
  AND license_status = 'valid'
  AND sex            = 'F'
  AND TIMESTAMPDIFF(YEAR, date_of_birth, CURDATE()) BETWEEN 18 AND 50
ORDER BY last_name, first_name;

-- 2. View all vehicles owned by a given driver

SELECT
    v.plate_number,
    v.chassis_number,
    v.engine_number,
    v.vehicle_type,
    v.ownership_type,
    v.make,
    v.model,
    v.year,
    v.color,
    v.franchise_number,
    d.first_name  AS owner_first_name,
    d.last_name   AS owner_last_name,
    d.license_number
FROM vehicle v
JOIN driver d ON v.license_number = d.license_number
WHERE d.license_number = 'P02-85-654321'
ORDER BY v.plate_number;

-- 3. View all vehicles with expired registrations as of a given date

SELECT
    v.plate_number,
    v.chassis_number,
    v.vehicle_type,
    v.make,
    v.model,
    v.year,
    d.first_name  AS owner_first_name,
    d.last_name   AS owner_last_name,
    d.license_number,
    vr.registration_number,
    vr.expiration_date,
    vr.registration_status
FROM vehicle_registration vr
JOIN vehicle v ON vr.plate_number   = v.plate_number
              AND vr.chassis_number = v.chassis_number
JOIN driver  d ON v.license_number  = d.license_number
WHERE vr.expiration_date < '2025-04-12'
ORDER BY vr.expiration_date DESC;

-- 4. View all drivers with expired or suspended licenses

SELECT
    license_number,
    first_name,
    middle_name,
    last_name,
    license_type,
    license_status,
    license_expiration_date,
    TIMESTAMPDIFF(YEAR, date_of_birth, CURDATE()) AS age,
    address
FROM driver
WHERE license_status IN ('expired', 'suspended')
ORDER BY license_status, last_name;

-- 5. View all traffic violations committed by a given driver within a specified date range

SELECT
    tv.traffic_violation_id,
    tv.date,
    tv.time,
    tv.location,
    tv.apprehending_officer,
    tv.violation_status,
    tv.total_fine_amount,
    tv.plate_number,
    tvt.violation_type
FROM traffic_violation tv
LEFT JOIN traffic_violation_type tvt
       ON tv.traffic_violation_id = tvt.traffic_violation_id
WHERE tv.license_number = 'N01-90-123456'
  AND tv.date BETWEEN '2024-01-01' AND '2024-12-31'
ORDER BY tv.date, tv.time;

-- 6. Total number of violations per violation type for a given year

SELECT
    tvt.violation_type,
    COUNT(*) AS total_violations
FROM traffic_violation_type tvt
JOIN traffic_violation tv
  ON tvt.traffic_violation_id = tv.traffic_violation_id
WHERE YEAR(tv.date) = 2025
GROUP BY tvt.violation_type
ORDER BY total_violations DESC;

-- 7. All vehicles involved in violations within a given city or region

SELECT DISTINCT
    v.plate_number,
    v.chassis_number,
    v.make,
    v.model,
    v.year,
    v.color,
    v.vehicle_type,
    d.first_name AS owner_first_name,
    d.last_name  AS owner_last_name,
    tv.location
FROM traffic_violation tv
JOIN vehicle v
  ON tv.plate_number   = v.plate_number
 AND tv.chassis_number = v.chassis_number
JOIN driver d
  ON v.license_number = d.license_number
WHERE tv.location LIKE '%Quezon City%'
ORDER BY v.plate_number;