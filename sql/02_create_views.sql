-- Նախ, եթե արդեն կան view-երը, ջնջենք, որ ազատ ստեղծենք
DROP VIEW IF EXISTS credit_conveyor.vw_kpi_violated_loans;
DROP VIEW IF EXISTS credit_conveyor.vw_phase_duration;

-- ===============================
-- View 1: Փուլերի տևողություն օրերով
-- ===============================

CREATE VIEW credit_conveyor.vw_phase_duration AS
SELECT
    lph.loan_phase_id,
    lph.loan_id,
    lph.phase_id,
    p.phase_name,
    lph.start_date::date AS start_date,
    lph.end_date::date   AS end_date,
    COALESCE(
        EXTRACT(DAY FROM age(lph.end_date::date, lph.start_date::date)),
        0
    )::int AS duration_days
FROM credit_conveyor.loan_phase_history lph
JOIN credit_conveyor.phase p
  ON p.phase_id = lph.phase_id;

-- ===============================
-- View 2: KPI-ին չհամապատասխանող վարկեր
-- ===============================

CREATE VIEW credit_conveyor.vw_kpi_violated_loans AS
SELECT DISTINCT
    l.loan_id,
    l.application_id,
    l.client_id,
    l.status,
    l.application_date,
    l.final_decision_date,
    b.branch_name,
    pr.product_name
FROM credit_conveyor.loan_phase_kpi       lpk
JOIN credit_conveyor.kpi_definition       kd
  ON kd.kpi_id = lpk.kpi_id
JOIN credit_conveyor.loan_phase_history   lph
  ON lph.loan_phase_id = lpk.loan_phase_id
JOIN credit_conveyor.loan                 l
  ON l.loan_id = lph.loan_id
JOIN credit_conveyor.branch               b
  ON b.branch_id = l.branch_id
JOIN credit_conveyor.product              pr
  ON pr.product_id = l.product_id
WHERE lpk.value_numeric > kd.threshold_value;

-- View: credit_conveyor.v_loans_not_meeting_kpi

-- DROP VIEW credit_conveyor.v_loans_not_meeting_kpi;

CREATE OR REPLACE VIEW credit_conveyor.v_loans_not_meeting_kpi
 AS
 SELECT la.application_id,
    c.client_id,
    b.branch_name,
    p.product_name,
    lp.phase_code,
    lpk.value_numeric AS duration_days,
    tgt.max_days
   FROM credit_conveyor.loan_application la
     JOIN credit_conveyor.client c ON la.client_id::text = c.client_id::text
     JOIN credit_conveyor.branch b ON la.branch_id = b.branch_id
     JOIN credit_conveyor.product p ON la.product_id = p.product_id
     JOIN credit_conveyor.loan_phase_history lph ON la.loan_id = lph.loan_id
     JOIN credit_conveyor.loan_phase lp ON lp.phase_id = lph.phase_id
     JOIN credit_conveyor.loan_phase_kpi lpk ON lpk.loan_phase_id = lph.loan_phase_id
     JOIN credit_conveyor.phase_kpi_target tgt ON tgt.phase_id = lp.phase_id
  WHERE lpk.value_numeric > tgt.max_days::numeric;

ALTER TABLE credit_conveyor.v_loans_not_meeting_kpi
    OWNER TO postgres;

-- View: credit_conveyor.v_avg_phase_duration_by_branch

-- DROP VIEW credit_conveyor.v_avg_phase_duration_by_branch;

CREATE OR REPLACE VIEW credit_conveyor.v_avg_phase_duration_by_branch
 AS
 SELECT b.branch_name,
    lp.phase_code,
    avg(lpk.value_numeric) AS avg_duration_days
   FROM credit_conveyor.loan_phase_kpi lpk
     JOIN credit_conveyor.loan_phase_history lph ON lpk.loan_phase_id = lph.loan_phase_id
     JOIN credit_conveyor.loan_phase lp ON lp.phase_id = lph.phase_id
     JOIN credit_conveyor.loan_application la ON la.loan_id = lph.loan_id
     JOIN credit_conveyor.branch b ON b.branch_id = la.branch_id
  GROUP BY b.branch_name, lp.phase_code
  ORDER BY b.branch_name, lp.phase_code;

ALTER TABLE credit_conveyor.v_avg_phase_duration_by_branch
    OWNER TO postgres;

-- View: credit_conveyor.v_loan_count_by_product

-- DROP VIEW credit_conveyor.v_loan_count_by_product;

CREATE OR REPLACE VIEW credit_conveyor.v_loan_count_by_product
 AS
 SELECT p.product_name,
    count(*) AS loan_count
   FROM credit_conveyor.loan_application la
     JOIN credit_conveyor.product p ON la.product_id = p.product_id
  GROUP BY p.product_name
  ORDER BY (count(*)) DESC;

ALTER TABLE credit_conveyor.v_loan_count_by_product
    OWNER TO postgres;

-- View: credit_conveyor.v_loan_count_by_branch

-- DROP VIEW credit_conveyor.v_loan_count_by_branch;

CREATE OR REPLACE VIEW credit_conveyor.v_loan_count_by_branch
 AS
 SELECT b.branch_name,
    count(*) AS loan_count
   FROM credit_conveyor.loan_application la
     JOIN credit_conveyor.branch b ON la.branch_id = b.branch_id
  GROUP BY b.branch_name
  ORDER BY (count(*)) DESC;

ALTER TABLE credit_conveyor.v_loan_count_by_branch
    OWNER TO postgres;

-- View: credit_conveyor.v_loan_overview

-- DROP VIEW credit_conveyor.v_loan_overview;

CREATE OR REPLACE VIEW credit_conveyor.v_loan_overview
 AS
 SELECT la.loan_id,
    la.application_id,
    la.status,
    la.application_date,
    la.final_decision_date,
    c.client_id,
    b.branch_name,
    p.product_name
   FROM credit_conveyor.loan_application la
     JOIN credit_conveyor.client c ON la.client_id::text = c.client_id::text
     JOIN credit_conveyor.branch b ON la.branch_id = b.branch_id
     JOIN credit_conveyor.product p ON la.product_id = p.product_id;

ALTER TABLE credit_conveyor.v_loan_overview
    OWNER TO postgres;

-- View: credit_conveyor.vw_kpi_violations

-- DROP VIEW credit_conveyor.vw_kpi_violations;

CREATE OR REPLACE VIEW credit_conveyor.vw_kpi_violations
 AS
 SELECT loan_phase_id,
    loan_id,
    phase_id,
    phase_name,
    start_date,
    end_date,
    duration_days,
        CASE
            WHEN duration_days > 1::numeric THEN true
            ELSE false
        END AS is_violation
   FROM credit_conveyor.vw_phase_duration d;

ALTER TABLE credit_conveyor.vw_kpi_violations
    OWNER TO postgres;

-- View: credit_conveyor.vw_kpi_violated_phases

-- DROP VIEW credit_conveyor.vw_kpi_violated_phases;

CREATE OR REPLACE VIEW credit_conveyor.vw_kpi_violated_phases
 AS
 SELECT loan_phase_id,
    loan_id,
    phase_id,
    phase_name,
    start_date,
    end_date,
    duration_days,
    is_violation
   FROM credit_conveyor.vw_kpi_violations
  WHERE is_violation = true;

ALTER TABLE credit_conveyor.vw_kpi_violated_phases
    OWNER TO postgres;

-- View: credit_conveyor.vw_kpi_violated_loans

-- DROP VIEW credit_conveyor.vw_kpi_violated_loans;

CREATE OR REPLACE VIEW credit_conveyor.vw_kpi_violated_loans
 AS
 SELECT v.loan_id,
    la.application_id,
    la.client_id,
    la.status,
    la.application_date,
    b.branch_name,
    p.product_name,
    v.phase_id,
    v.phase_name,
    v.start_date,
    v.end_date,
    v.duration_days
   FROM credit_conveyor.vw_kpi_violations v
     JOIN credit_conveyor.loan_application la ON la.loan_id = v.loan_id
     JOIN credit_conveyor.branch b ON b.branch_id = la.branch_id
     JOIN credit_conveyor.product p ON p.product_id = la.product_id
  WHERE v.is_violation = true;

ALTER TABLE credit_conveyor.vw_kpi_violated_loans
    OWNER TO postgres;

-- View: credit_conveyor.vw_phase_duration

-- DROP VIEW credit_conveyor.vw_phase_duration;

CREATE OR REPLACE VIEW credit_conveyor.vw_phase_duration
 AS
 SELECT lph.loan_phase_id,
    lph.loan_id,
    lph.phase_id,
    p.phase_name,
    lph.start_date,
    lph.end_date,
    EXTRACT(day FROM age(lph.end_date::timestamp with time zone, lph.start_date::timestamp with time zone)) AS duration_days
   FROM credit_conveyor.loan_phase_history lph
     JOIN credit_conveyor.phase p ON p.phase_id = lph.phase_id;

ALTER TABLE credit_conveyor.vw_phase_duration
    OWNER TO postgres;


