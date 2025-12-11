CREATE SCHEMA IF NOT EXISTS credit_conveyor;
-- Table: credit_conveyor.client

-- DROP TABLE IF EXISTS credit_conveyor.client;

CREATE TABLE IF NOT EXISTS credit_conveyor.client
(
    client_id character varying(20) COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT client_pkey PRIMARY KEY (client_id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS credit_conveyor.client
    OWNER to postgres;
-- Table: credit_conveyor.branch

-- DROP TABLE IF EXISTS credit_conveyor.branch;

CREATE TABLE IF NOT EXISTS credit_conveyor.branch
(
    branch_id integer NOT NULL DEFAULT nextval('credit_conveyor.branch_branch_id_seq'::regclass),
    branch_name character varying(100) COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT branch_pkey PRIMARY KEY (branch_id),
    CONSTRAINT branch_branch_name_key UNIQUE (branch_name)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS credit_conveyor.branch
    OWNER to postgres;
-- Table: credit_conveyor.product

-- DROP TABLE IF EXISTS credit_conveyor.product;

CREATE TABLE IF NOT EXISTS credit_conveyor.product
(
    product_id integer NOT NULL DEFAULT nextval('credit_conveyor.product_product_id_seq'::regclass),
    product_name character varying(100) COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT product_pkey PRIMARY KEY (product_id),
    CONSTRAINT product_product_name_key UNIQUE (product_name)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS credit_conveyor.product
    OWNER to postgres;
-- Table: credit_conveyor.phase

-- DROP TABLE IF EXISTS credit_conveyor.phase;

CREATE TABLE IF NOT EXISTS credit_conveyor.phase
(
    phase_id integer NOT NULL DEFAULT nextval('credit_conveyor.phase_phase_id_seq'::regclass),
    phase_name character varying(100) COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT phase_pkey PRIMARY KEY (phase_id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS credit_conveyor.phase
    OWNER to postgres;
-- Table: credit_conveyor.loan

-- DROP TABLE IF EXISTS credit_conveyor.loan;

CREATE TABLE IF NOT EXISTS credit_conveyor.loan
(
    loan_id integer NOT NULL DEFAULT nextval('credit_conveyor.loan_loan_id_seq'::regclass),
    application_id character varying(20) COLLATE pg_catalog."default" NOT NULL,
    client_id character varying(20) COLLATE pg_catalog."default" NOT NULL,
    branch_id integer NOT NULL,
    product_id integer NOT NULL,
    status character varying(30) COLLATE pg_catalog."default" NOT NULL,
    application_date date NOT NULL,
    final_decision_date date,
    CONSTRAINT loan_pkey PRIMARY KEY (loan_id),
    CONSTRAINT loan_application_id_key UNIQUE (application_id),
    CONSTRAINT loan_branch_id_fkey FOREIGN KEY (branch_id)
        REFERENCES credit_conveyor.branch (branch_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT loan_client_id_fkey FOREIGN KEY (client_id)
        REFERENCES credit_conveyor.client (client_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT loan_product_id_fkey FOREIGN KEY (product_id)
        REFERENCES credit_conveyor.product (product_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS credit_conveyor.loan
    OWNER to postgres;
-- Table: credit_conveyor.loan_phase_history

-- DROP TABLE IF EXISTS credit_conveyor.loan_phase_history;

CREATE TABLE IF NOT EXISTS credit_conveyor.loan_phase_history
(
    loan_phase_id integer NOT NULL DEFAULT nextval('credit_conveyor.loan_phase_history_loan_phase_id_seq'::regclass),
    loan_id integer NOT NULL,
    phase_id integer NOT NULL,
    start_date date NOT NULL,
    end_date date,
    CONSTRAINT loan_phase_history_pkey PRIMARY KEY (loan_phase_id),
    CONSTRAINT uq_loan_phase UNIQUE (loan_id, phase_id),
    CONSTRAINT loan_phase_history_loan_id_fkey FOREIGN KEY (loan_id)
        REFERENCES credit_conveyor.loan_application (loan_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT loan_phase_history_phase_id_fkey FOREIGN KEY (phase_id)
        REFERENCES credit_conveyor.loan_phase (phase_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS credit_conveyor.loan_phase_history
    OWNER to postgres;
-- Table: credit_conveyor.kpi_definition

-- DROP TABLE IF EXISTS credit_conveyor.kpi_definition;

CREATE TABLE IF NOT EXISTS credit_conveyor.kpi_definition
(
    kpi_id integer NOT NULL DEFAULT nextval('credit_conveyor.kpi_definition_kpi_id_seq'::regclass),
    kpi_code character varying(50) COLLATE pg_catalog."default" NOT NULL,
    kpi_name character varying(255) COLLATE pg_catalog."default" NOT NULL,
    description text COLLATE pg_catalog."default",
    CONSTRAINT kpi_definition_pkey PRIMARY KEY (kpi_id),
    CONSTRAINT kpi_definition_kpi_code_key UNIQUE (kpi_code)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS credit_conveyor.kpi_definition
    OWNER to postgres;
-- Table: credit_conveyor.loan_phase_kpi

-- DROP TABLE IF EXISTS credit_conveyor.loan_phase_kpi;

CREATE TABLE IF NOT EXISTS credit_conveyor.loan_phase_kpi
(
    loan_phase_id integer NOT NULL,
    kpi_id integer NOT NULL,
    value_numeric numeric(18,4),
    value_text character varying(255) COLLATE pg_catalog."default",
    measured_at timestamp without time zone DEFAULT now(),
    CONSTRAINT loan_phase_kpi_pkey PRIMARY KEY (loan_phase_id, kpi_id),
    CONSTRAINT loan_phase_kpi_kpi_id_fkey FOREIGN KEY (kpi_id)
        REFERENCES credit_conveyor.kpi_definition (kpi_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT loan_phase_kpi_loan_phase_id_fkey FOREIGN KEY (loan_phase_id)
        REFERENCES credit_conveyor.loan_phase_history (loan_phase_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS credit_conveyor.loan_phase_kpi
    OWNER to postgres;