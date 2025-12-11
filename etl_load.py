import pandas as pd
import psycopg2
import os
print(os.listdir())

# 1. Կարդում ենք Excel-ը
df = pd.read_excel("CreditConveyor Data.xlsx", sheet_name="CreditConveyorTest")

# 2. Կապ PostgreSQL-ին (փոխիր password-ը եթե այլ է)
conn = psycopg2.connect(
    host="localhost",
    dbname="credit_db",
    user="postgres",
    password="admin"
)
cur = conn.cursor()

# --- Branch, Product և Client աղյուսակների լիցքավորում ---

# Branch
branches = df["Branch"].dropna().unique()
for b in branches:
    cur.execute(
        "INSERT INTO credit_conveyor.branch (branch_name) VALUES (%s) ON CONFLICT (branch_name) DO NOTHING;",
        (b,)
    )

# Product
products = df["Product"].dropna().unique()
for p in products:
    cur.execute(
        "INSERT INTO credit_conveyor.product (product_name) VALUES (%s) ON CONFLICT (product_name) DO NOTHING;",
        (p,)
    )

# Client
clients = df["ClientID"].dropna().unique()
for c in clients:
    cur.execute(
        "INSERT INTO credit_conveyor.client (client_id) VALUES (%s) ON CONFLICT (client_id) DO NOTHING;",
        (c,)
    )

conn.commit()
print("Basic data inserted successfully!")

# --- Helper functions to get FK IDs ---

def get_branch_id(branch_name):
    cur.execute("SELECT branch_id FROM credit_conveyor.branch WHERE branch_name = %s;", (branch_name,))
    return cur.fetchone()[0]

def get_product_id(product_name):
    cur.execute("SELECT product_id FROM credit_conveyor.product WHERE product_name = %s;", (product_name,))
    return cur.fetchone()[0]

def get_client_id(client_id):
    # client_id itself is PK so no need to convert
    return client_id

# --- Insert Loan Applications ---

for index, row in df.iterrows():
    application_id = row["ApplicationID"]
    client_id = row["ClientID"]
    product_name = row["Product"]
    branch_name = row["Branch"]
    status = row["Status"]
    app_date = row["ApplicationDate"]
    final_decision = row["FinalDecisionDate"]

    # foreign keys
    fk_client = get_client_id(client_id)
    fk_product = get_product_id(product_name)
    fk_branch = get_branch_id(branch_name)

    cur.execute("""
        INSERT INTO credit_conveyor.loan_application
        (application_id, client_id, product_id, branch_id, status, application_date, final_decision_date)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (application_id) DO NOTHING;
    """, (application_id, fk_client, fk_product, fk_branch, status, app_date, final_decision))

conn.commit()
print("Loan applications inserted successfully!")

# --- Insert Loan Phase History ---

# Phase IDs
cur.execute("SELECT phase_id, phase_code FROM credit_conveyor.loan_phase;")
phase_map = {row[1]: row[0] for row in cur.fetchall()}

for index, row in df.iterrows():
    # Loan ID
    cur.execute("SELECT loan_id FROM credit_conveyor.loan_application WHERE application_id = %s;",
                (row["ApplicationID"],))
    loan_id = cur.fetchone()[0]

    # Phase1
    if not pd.isna(row["Phase1_Start"]):
        cur.execute("""
            INSERT INTO credit_conveyor.loan_phase_history
            (loan_id, phase_id, start_date, end_date)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT DO NOTHING;
        """, (loan_id, phase_map["PHASE1"], row["Phase1_Start"], row["Phase1_End"]))

    # Phase2
    if not pd.isna(row["Phase2_Start"]):
        cur.execute("""
            INSERT INTO credit_conveyor.loan_phase_history
            (loan_id, phase_id, start_date, end_date)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT DO NOTHING;
        """, (loan_id, phase_map["PHASE2"], row["Phase2_Start"], row["Phase2_End"]))

    # Phase3
    if not pd.isna(row["Phase3_Start"]):
        cur.execute("""
            INSERT INTO credit_conveyor.loan_phase_history
            (loan_id, phase_id, start_date, end_date)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT DO NOTHING;
        """, (loan_id, phase_map["PHASE3"], row["Phase3_Start"], row["Phase3_End"]))

conn.commit()
print("Loan phase history inserted successfully!")

# --- Calculate KPI: Phase Duration in Days ---

# 1. Get KPI ID for PHASE_DURATION_DAYS
cur.execute("SELECT kpi_id FROM credit_conveyor.kpi_definition WHERE kpi_code = 'PHASE_DURATION_DAYS';")
kpi_id = cur.fetchone()[0]

# 2. Select all phase history rows
cur.execute("SELECT loan_phase_id, start_date, end_date FROM credit_conveyor.loan_phase_history;")
rows = cur.fetchall()

for loan_phase_id, start, end in rows:
    if start and end:
        duration_days = (end - start).days  # timedelta to days

        cur.execute("""
            INSERT INTO credit_conveyor.loan_phase_kpi
            (loan_phase_id, kpi_id, value_numeric)
            VALUES (%s, %s, %s)
            ON CONFLICT DO NOTHING;
        """, (loan_phase_id, kpi_id, duration_days))

conn.commit()
print("KPI calculation completed successfully!")


cur.close()
conn.close()

