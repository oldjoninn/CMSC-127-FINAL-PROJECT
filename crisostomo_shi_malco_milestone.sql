
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

-- 20 Drivers (Mix of valid, expired, suspended, and student permits. 8 drivers have no vehicles.)
INSERT INTO driver (license_number, first_name, middle_name, last_name, date_of_birth, sex, address, license_type, license_status, license_issuance_date, license_expiration_date) VALUES
    ('N01-20-000001', 'Juan',      'Santos',     'Dela Cruz',  '1990-05-15', 'M', '123 Rizal St., Manila',             'Non-Professional', 'valid',     '2023-01-10', '2028-01-10'),
    ('P02-15-000002', 'Maria',     'Lopez',      'Reyes',      '1985-08-22', 'F', '456 Mabini Ave., Quezon City',      'Professional',     'valid',     '2022-06-01', '2027-06-01'),
    ('N03-18-000003', 'Pedro',     'Garcia',     'Santos',     '1978-03-10', 'M', '789 Bonifacio Rd., Cebu',           'Non-Professional', 'expired',   '2018-04-01', '2023-04-01'),
    ('S04-26-000004', 'Ana',       'Cruz',       'Garcia',     '2005-11-30', 'F', '321 Luna St., Davao',               'Student Permit',   'valid',     '2026-01-15', '2027-01-15'),
    ('P05-19-000005', 'Marco',     'Bautista',   'Villanueva', '1995-07-04', 'M', '654 Aguinaldo Blvd., Cavite',       'Professional',     'suspended', '2024-09-01', '2029-09-01'),
    ('N06-22-000006', 'Luis',      'Fernandez',  'Mendoza',    '1992-12-12', 'M', 'Pansol, Calamba, Laguna',           'Non-Professional', 'valid',     '2024-02-20', '2029-02-20'),
    ('N07-21-000007', 'Elena',     'Ramos',      'Castillo',   '1988-09-05', 'F', 'Batong Malake, Los Baños, Laguna',  'Non-Professional', 'valid',     '2025-05-10', '2030-05-10'),
    ('P08-10-000008', 'Ricardo',   'Gomez',      'Navarro',    '1975-11-20', 'M', 'San Antonio, Los Baños, Laguna',    'Professional',     'valid',     '2023-11-15', '2028-11-15'),
    ('S09-26-000009', 'Sofia',     'Alvarez',    'Tolentino',  '2007-04-18', 'F', 'Makiling, Calamba, Laguna',         'Student Permit',   'valid',     '2026-03-01', '2027-03-01'),
    ('N10-14-000010', 'Miguel',    'Torres',     'Pascual',    '1998-02-28', 'M', 'Timog Ave., Quezon City',           'Non-Professional', 'valid',     '2022-08-12', '2027-08-12'),
    ('P11-11-000011', 'Teresa',    'Velasco',    'Aquino',     '1980-06-14', 'F', 'Ayala Alabang, Muntinlupa',         'Professional',     'valid',     '2021-07-22', '2026-07-22'),
    ('N12-23-000012', 'Jose',      'Soriano',    'Valdez',     '2000-01-30', 'M', 'BGC, Taguig City',                  'Non-Professional', 'valid',     '2023-12-05', '2028-12-05'),
    ('N13-16-000013', 'Carmen',    'Rivera',     'Salazar',    '1994-10-09', 'F', 'Ortigas Center, Pasig',             'Non-Professional', 'expired',   '2020-03-15', '2025-03-15'),
    ('P14-09-000014', 'Antonio',   'Luna',       'Heneral',    '1982-10-29', 'M', 'Intramuros, Manila',                'Professional',     'revoked',   '2019-11-30', '2024-11-30'),
    ('S15-25-000015', 'Beatriz',   'Reyes',      'Magno',      '2006-08-15', 'F', 'Taft Ave., Manila',                 'Student Permit',   'valid',     '2025-10-10', '2026-10-10'),
    ('N16-24-000016', 'Fernando',  'Poe',        'Junior',     '1970-08-20', 'M', 'Greenhills, San Juan',              'Non-Professional', 'valid',     '2024-04-18', '2029-04-18'),
    ('N17-21-000017', 'Lucia',     'Zaragoza',   'Gutierez',   '1999-05-25', 'F', 'Eastwood, Quezon City',             'Non-Professional', 'valid',     '2025-01-20', '2030-01-20'),
    ('P18-12-000018', 'Gregorio',  'Del Pilar',  'Tirad',      '1985-11-14', 'M', 'Bulacan, Bulacan',                  'Professional',     'valid',     '2022-09-09', '2027-09-09'),
    ('N19-20-000019', 'Rosario',   'Macapagal',  'Arroyo',     '1965-04-05', 'F', 'Lubao, Pampanga',                   'Non-Professional', 'valid',     '2023-06-12', '2028-06-12'),
    ('S20-26-000020', 'Emilio',    'Aguinaldo',  'Kawit',      '2008-03-22', 'M', 'Kawit, Cavite',                     'Student Permit',   'valid',     '2026-04-05', '2027-04-05');

-- 15 Vehicles (Linked to the first 12 drivers)
INSERT INTO vehicle (plate_number, chassis_number, engine_number, vehicle_type, ownership_type, make, model, year, color, franchise_number, license_number) VALUES
    ('ABC 1234', 'CHS-00001', 'ENG-00001', 'private car',            'private', 'Toyota',     'Vios',      2022, 'White',  NULL,       'N01-20-000001'),
    ('XYZ 5678', 'CHS-00002', 'ENG-00002', 'motorcycle',             'private', 'Honda',      'Click 125', 2021, 'Red',    NULL,       'P02-15-000002'),
    ('DEF 9012', 'CHS-00003', 'ENG-00003', 'public utility vehicle', 'public',  'Mitsubishi', 'L300',      2019, 'Yellow', 'FR-00123', 'P02-15-000002'),
    ('GHI 3456', 'CHS-00004', 'ENG-00004', 'private car',            'private', 'Ford',       'Ranger',    2020, 'Black',  NULL,       'P05-19-000005'),
    ('JKL 7890', 'CHS-00005', 'ENG-00005', 'motorcycle',             'private', 'Yamaha',     'Mio',       2023, 'Blue',   NULL,       'N01-20-000001'),
    ('MNO 1111', 'CHS-00006', 'ENG-00006', 'private car',            'private', 'Honda',      'Civic',     2024, 'Silver', NULL,       'N06-22-000006'),
    ('PQR 2222', 'CHS-00007', 'ENG-00007', 'private car',            'private', 'Suzuki',     'Swift',     2018, 'Red',    NULL,       'N07-21-000007'),
    ('STU 3333', 'CHS-00008', 'ENG-00008', 'public utility vehicle', 'public',  'Toyota',     'Hiace',     2021, 'White',  'FR-00456', 'P08-10-000008'),
    ('VWX 4444', 'CHS-00009', 'ENG-00009', 'motorcycle',             'private', 'Kawasaki',   'Rouser',    2020, 'Black',  NULL,       'N10-14-000010'),
    ('YZA 5555', 'CHS-00010', 'ENG-00010', 'private car',            'private', 'Mazda',      '3',         2025, 'Gray',   NULL,       'P11-11-000011'),
    ('BCD 6666', 'CHS-00011', 'ENG-00011', 'private car',            'private', 'Nissan',     'Navara',    2022, 'Orange', NULL,       'N12-23-000012'),
    ('EFG 7777', 'CHS-00012', 'ENG-00012', 'private car',            'private', 'Toyota',     'Fortuner',  2019, 'Black',  NULL,       'N13-16-000013'),
    ('HIJ 8888', 'CHS-00013', 'ENG-00013', 'motorcycle',             'private', 'Vespa',      'Primavera', 2023, 'Green',  NULL,       'N06-22-000006'),
    ('KLM 9999', 'CHS-00014', 'ENG-00014', 'public utility vehicle', 'public',  'Isuzu',      'Crosswind', 2017, 'White',  'FR-00789', 'P08-10-000008'),
    ('NOP 0000', 'CHS-00015', 'ENG-00015', 'private car',            'private', 'Ford',       'Everest',   2026, 'White',  NULL,       'N12-23-000012');

-- 28 Registrations (Includes historical records for multiple vehicles to demonstrate tracking)
INSERT INTO vehicle_registration (registration_number, registration_date, expiration_date, registration_status, plate_number, chassis_number) VALUES
    ('REG-2023-00001', '2023-06-15', '2024-06-15', 'expired', 'ABC 1234', 'CHS-00001'),
    ('REG-2024-00001', '2024-06-15', '2025-06-15', 'expired', 'ABC 1234', 'CHS-00001'),
    ('REG-2025-00001', '2025-06-15', '2026-06-15', 'active',  'ABC 1234', 'CHS-00001'),
    ('REG-2024-00002', '2024-03-10', '2025-03-10', 'expired', 'XYZ 5678', 'CHS-00002'),
    ('REG-2025-00002', '2025-03-10', '2026-03-10', 'active',  'XYZ 5678', 'CHS-00002'),
    ('REG-2026-00003', '2026-02-20', '2027-02-20', 'active',  'DEF 9012', 'CHS-00003'),
    ('REG-2023-00004', '2023-06-01', '2024-06-01', 'expired', 'GHI 3456', 'CHS-00004'),
    ('REG-2024-00005', '2024-08-01', '2025-08-01', 'expired', 'JKL 7890', 'CHS-00005'),
    ('REG-2025-00005', '2025-08-01', '2026-08-01', 'active',  'JKL 7890', 'CHS-00005'),
    ('REG-2026-00006', '2026-01-10', '2027-01-10', 'active',  'MNO 1111', 'CHS-00006'),
    ('REG-2023-00007', '2023-07-22', '2024-07-22', 'expired', 'PQR 2222', 'CHS-00007'),
    ('REG-2024-00007', '2024-07-22', '2025-07-22', 'expired', 'PQR 2222', 'CHS-00007'),
    ('REG-2025-00007', '2025-07-22', '2026-07-22', 'active',  'PQR 2222', 'CHS-00007'),
    ('REG-2026-00008', '2026-04-15', '2027-04-15', 'active',  'STU 3333', 'CHS-00008'),
    ('REG-2025-00009', '2025-11-05', '2026-11-05', 'active',  'VWX 4444', 'CHS-00009'),
    ('REG-2026-00010', '2026-05-01', '2027-05-01', 'active',  'YZA 5555', 'CHS-00010'),
    ('REG-2024-00011', '2024-10-12', '2025-10-12', 'expired', 'BCD 6666', 'CHS-00011'),
    ('REG-2025-00011', '2025-10-12', '2026-10-12', 'active',  'BCD 6666', 'CHS-00011'),
    ('REG-2023-00012', '2023-09-18', '2024-09-18', 'expired', 'EFG 7777', 'CHS-00012'),
    ('REG-2024-00012', '2024-09-18', '2025-09-18', 'expired', 'EFG 7777', 'CHS-00012'),
    ('REG-2025-00013', '2025-12-01', '2026-12-01', 'active',  'HIJ 8888', 'CHS-00013'),
    ('REG-2025-00014', '2025-03-30', '2026-03-30', 'expired', 'KLM 9999', 'CHS-00014'),
    ('REG-2026-00014', '2026-03-30', '2027-03-30', 'active',  'KLM 9999', 'CHS-00014'),
    ('REG-2026-00015', '2026-05-15', '2027-05-15', 'active',  'NOP 0000', 'CHS-00015');

-- 10 Traffic Violations 
INSERT INTO traffic_violation (violation_status, apprehending_officer, total_fine_amount, location, date, time, license_number, plate_number, chassis_number) VALUES
    ('paid',      'Officer Reyes',    2000.00, 'EDSA, Quezon City',      '2025-11-01', '08:30:00', 'N01-20-000001', 'ABC 1234', 'CHS-00001'),
    ('unpaid',    'Officer Santos',   5000.00, 'C5 Road, Taguig',        '2026-04-15', '14:15:00', 'N01-20-000001', 'ABC 1234', 'CHS-00001'),
    ('unpaid',    NULL,                500.00, 'Ayala Ave., Makati',     '2026-01-20', '11:00:00', 'P02-15-000002', 'XYZ 5678', 'CHS-00002'),
    ('unpaid',    'Officer Cruz',     2000.00, 'NLEX, Bulacan',          '2026-02-10', '07:45:00', 'P05-19-000005', 'GHI 3456', 'CHS-00004'),
    ('contested', 'Officer Lim',      1500.00, 'Katipunan Ave., QC',     '2026-03-14', '09:20:00', 'N06-22-000006', 'MNO 1111', 'CHS-00006'),
    ('paid',      'Officer Bautista', 1000.00, 'SLEX, Laguna',           '2025-12-05', '16:00:00', 'N07-21-000007', 'PQR 2222', 'CHS-00007'),
    ('unpaid',    'Officer Torres',   5000.00, 'MacArthur Hwy., Manila', '2026-05-10', '13:30:00', 'P08-10-000008', 'STU 3333', 'CHS-00008'),
    ('paid',      'Officer Garcia',   2500.00, 'Commonwealth Ave., QC',  '2026-04-22', '10:15:00', 'N12-23-000012', 'BCD 6666', 'CHS-00011'),
    ('unpaid',    'Officer Mendoza',  1500.00, 'BGC, Taguig',            '2026-05-18', '21:45:00', 'N10-14-000010', 'VWX 4444', 'CHS-00009'),
    ('contested', 'Officer Villanueva', 3000.00, 'Roxas Blvd., Manila',  '2026-05-02', '17:30:00', 'P11-11-000011', 'YZA 5555', 'CHS-00010');

INSERT INTO traffic_violation_type (traffic_violation_id, violation_type) VALUES
    (1, 'Overspeeding'),
    (2, 'Reckless Driving'),
    (3, 'Illegal Parking'),
    (4, 'Overspeeding'),
    (5, 'No Helmet'),
    (6, 'Disregarding Traffic Signs'),
    (7, 'Reckless Driving'),
    (8, 'Driving Under the Influence'),
    (9, 'No Helmet'),
    (10, 'Obstruction');


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