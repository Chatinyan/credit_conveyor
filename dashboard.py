import streamlit as st
import psycopg2
import pandas as pd
import plotly.express as px

# -------- PAGE CONFIG --------
st.set_page_config(
    page_title="Loan Credit Conveyor",
    page_icon="🏦",
    layout="wide"
)

# -------- DB CONNECTION --------
def get_connection():
    return psycopg2.connect(
        host="localhost",
        dbname="credit_db",
        user="postgres",
        password="admin"
    )
# -------- FASTBANK STYLE --------
FAST_PRIMARY = "#FF00FF"      # հիմնական մանուշակագույն
FAST_DARK = "#CC00CC"
FAST_BG_LIGHT = "#F7F2FF"
FAST_TEXT_DARK = "#1B102F"

st.markdown(
    f"""
    <style>
    /* Ընդհանուր ֆոն և ֆոնտեր */
    [data-testid="stAppViewContainer"] {{
        background: radial-gradient(circle at top left, #faf5ff 0, #f3ecff 35%, #ffffff 100%);
        color: {FAST_TEXT_DARK};
        font-family: "Segoe UI", system-ui, -apple-system, BlinkMacSystemFont, "Roboto", sans-serif;
    }}

    /* Հիմնական կոնտեյներ՝ մի քիչ ավելի նեղ ու կենտրոնացված */
    .main .block-container {{
        padding-top: 0.5rem;
        padding-bottom: 1.2rem;
        max-width: 1300px;
    }}

    /* Sidebar–ը FastBank gradient–ով */
    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, #5A22B5 0%, {FAST_PRIMARY} 45%, #3B1A78 100%) !important;
        color: #ffffff !important;
    }}

    /* Միայն վերնագրերն ու label-ներն ենք անում սպիտակ,
       input–ների value–ները թողնում ենք մուգ */
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] p {{
        color: #ffffff !important;
    }}

    /* Selectbox–ի value–ն և Date input–ի value–ն մուգ գույնով */
    [data-testid="stSidebar"] [data-baseweb="select"] span {{
        color: #222222 !important;
    }}

    [data-testid="stSidebar"] .stDateInput input {{
        color: #222222 !important;
    }}

    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {{
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-size: 0.8rem;
        opacity: 0.9;
    }}

    /* Վերնագրեր (հիմնական մասում) */
    h1 {{
        font-size: 2rem;
        font-weight: 800;
        letter-spacing: 0.03em;
        color: {FAST_TEXT_DARK};
    }}
    h2, h3 {{
        color: {FAST_DARK};
        font-weight: 700;
    }}

    /* KPI քարտեր (st.metric)՝ ստվերով */
    [data-testid="stMetric"] {{
        background: linear-gradient(140deg, #ffffff 0%, {FAST_BG_LIGHT} 100%);
        padding: 18px 20px;
        border-radius: 20px;
        box-shadow: 0 14px 34px rgba(65, 36, 120, 0.18);
        border: 1px solid #e4d7ff;
    }}
    [data-testid="stMetricLabel"] {{
        color: {FAST_PRIMARY} !important;
        font-weight: 600;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.09em;
    }}
    [data-testid="stMetricValue"] {{
        color: {FAST_TEXT_DARK} !important;
        font-weight: 800;
        font-size: 1.5rem;
    }}

    /* Սեկցիայի քարտեր (աղյուսակներ / KPI թաբլիցաներ / բաժիններ) */
    .section-card {{
        background-color: #ffffff;
        border-radius: 22px;
        padding: 14px 18px 18px 18px;
        margin-bottom: 1.2rem;
        box-shadow: 0 18px 38px rgba(15, 23, 42, 0.10);
        border: 1px solid #ece3ff;
    }}
    .section-title {{
        font-size: 1rem;
        font-weight: 700;
        color: {FAST_DARK};
        margin-bottom: 0.4rem;
        display: flex;
        align-items: center;
        gap: 0.4rem;
    }}
    .section-title span.icon {{
        width: 22px;
        height: 22px;
        border-radius: 999px;
        background: rgba(127, 44, 225, 0.12);
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-size: 0.8rem;
    }}

    /* DataFrame wrapper–ը թող լինի թափանցիկ,
       քանի որ section-card–ով ենք հարթում */
    [data-testid="stDataFrame"] {{
        background-color: transparent;
        box-shadow: none;
        border-radius: 0;
        border: none;
    }}

    /* HR գծեր՝ նուրբ */
    hr {{
        border: none;
        border-top: 1px solid #e6ddff;
        margin: 1rem 0 1.2rem;
    }}

    /* Plotly chart–երի կոնտեյներ՝ նույնպես որպես քարտիկ */
    .element-container:has(.js-plotly-plot) > div {{
        border-radius: 22px;
        padding: 10px 12px 6px 12px;
        background-color: #ffffff;
        box-shadow: 0 18px 38px rgba(15, 23, 42, 0.10);
        border: 1px solid #ece3ff;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# -------- DATA LOADERS --------
@st.cache_data
def load_loans():
    conn = get_connection()
    query = """
        SELECT 
            la.loan_id,
            la.application_id,
            la.client_id,
            la.status,
            la.application_date,
            la.final_decision_date,
            b.branch_name,
            p.product_name
        FROM credit_conveyor.loan_application la
        JOIN credit_conveyor.branch  b ON la.branch_id  = b.branch_id
        JOIN credit_conveyor.product p ON la.product_id = p.product_id;
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df


@st.cache_data
def load_phase_duration():
    conn = get_connection()
    query = "SELECT * FROM credit_conveyor.vw_phase_duration;"
    df = pd.read_sql(query, conn)
    conn.close()
    return df


@st.cache_data
def load_kpi_violated_loans():
    conn = get_connection()
    query = "SELECT * FROM credit_conveyor.vw_kpi_violated_loans;"
    df = pd.read_sql(query, conn)
    conn.close()
    return df


# -------- LOAD DATA --------
loans_df = load_loans()
phase_df = load_phase_duration()
kpi_violated_df = load_kpi_violated_loans()

# -------- TITLE --------
st.title("🏦 Վարկային Հոսքագծի Վերլուծական Վահանակ")
st.caption("Վարկային հոսքագծի վիզուալ վերլուծություն՝ ըստ վարկատեսակի, մասնաճյուղի և KPI կատարողականի։")

# -------- SIDEBAR FILTERS --------
# -------- SIDEBAR FILTERS --------
with st.sidebar:
    # gradient + inner card
    st.markdown("<div class='sidebar-gradient'><div class='sidebar-inner'>", unsafe_allow_html=True)

    st.markdown(
        "<div class='sidebar-title'><span class='dot'></span>ՖԻԼՏՐԵՐ</div>",
        unsafe_allow_html=True,
    )

    client_opt = ["All"] + sorted(loans_df["client_id"].unique().tolist())
    branch_opt = ["All"] + sorted(loans_df["branch_name"].unique().tolist())
    status_opt = ["All"] + sorted(loans_df["status"].unique().tolist())

    client_filter = st.selectbox("Հաճախորդ", client_opt)
    branch_filter = st.selectbox("Մասնաճյուղ", branch_opt)
    status_filter = st.selectbox("Վարկի կարգավիճակ", status_opt)
    date_range = st.date_input("Դիմումի ամսաթիվ", [])

    # փակում ենք div-երը
    st.markdown("</div></div>", unsafe_allow_html=True)


# -------- APPLY FILTERS TO LOANS --------
filtered = loans_df.copy()

if client_filter != "All":
    filtered = filtered[filtered["client_id"] == client_filter]

if branch_filter != "All":
    filtered = filtered[filtered["branch_name"] == branch_filter]

if status_filter != "All":
    filtered = filtered[filtered["status"] == status_filter]

if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
    start_date = pd.to_datetime(date_range[0])
    end_date = pd.to_datetime(date_range[1])
    filtered = filtered[
        (filtered["application_date"] >= start_date) &
        (filtered["application_date"] <= end_date)
    ]

# -------- KPI CARDS --------
total_loans_all = len(loans_df)
total_loans_filtered = len(filtered)

avg_duration_all = phase_df["duration_days"].mean()

# KPI loans (UNIQUE loan_id-ի քանակը)
violations_total = kpi_violated_df["loan_id"].nunique()

if not filtered.empty:
    violated_filtered_for_metric = kpi_violated_df[
        kpi_violated_df["loan_id"].isin(filtered["loan_id"])
    ]
    violations_filtered = violated_filtered_for_metric["loan_id"].nunique()
else:
    violations_filtered = violations_total

col_kpi1, col_kpi2, col_kpi3 = st.columns(3)

with col_kpi1:
    st.metric("Ֆիլտրված վարկերի քանակ", total_loans_filtered, f"ընդհանուրը՝ {total_loans_all}")

with col_kpi2:
    st.metric("Միջին փուլային տևողություն (օր)", round(avg_duration_all or 0, 2))

with col_kpi3:
    st.metric(
        "KPI խախտում ունեցող վարկեր (ֆիլտրով)",
        violations_filtered,
        f"ընդհանուրը՝ {violations_total}"
    )

    # Ինչ սյունակներ ենք ցույց տալիս աղյուսակներում
    LOAN_COLUMNS = [
        "N",
        "loan_id",
        "application_id",
        "client_id",
        "status",
        "application_date",
        "final_decision_date",
        "branch_name",
        "product_name",
    ]

# -------- MAIN TABLE + KPI TABLE --------
col1, col2 = st.columns([1.3, 1])

with col1:
    st.markdown(
        "<div class='section-title'><span class='icon'>📄</span>Ֆիլտրված վարկերի ցանկ</div>",
        unsafe_allow_html=True,
    )

    total_filtered = len(filtered)
    st.caption(f"Ֆիլտրված է {total_filtered} վարկ (ընտրած ֆիլտրերով)")

    # Հերթական համար ֆիլտրված վարկերի համար (օպցիոնալ, բայց գեղեցիկ է)
    filtered_show = filtered.reset_index(drop=True).copy()
    filtered_show.insert(0, "N", filtered_show.index + 1)

    st.dataframe(
        filtered_show[LOAN_COLUMNS],
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("</div>", unsafe_allow_html=True)


with col2:
    # գեղեցիկ քարթ KPI վարկերի համար
    st.markdown(
        "<div class='section-title'><span class='icon'>⚠️</span>KPI-ին չհամապատասխանող վարկեր</div>",
        unsafe_allow_html=True,
    )

    # 1․ KPI FAIL loan_id-ները ըստ ֆիլտրերի
    if not filtered.empty:
        violated_ids = kpi_violated_df[
            kpi_violated_df["loan_id"].isin(filtered["loan_id"])
        ]["loan_id"].unique()

        violated = loans_df[loans_df["loan_id"].isin(violated_ids)]
    else:
        violated_ids = kpi_violated_df["loan_id"].unique()
        violated = loans_df[loans_df["loan_id"].isin(violated_ids)]

    # 2․ Թողնում ենք loan_id-ով միայն UNIQUE վարկերը, սորտավորում ենք
    violated_unique = (
        violated
        .drop_duplicates(subset=["loan_id"])
        .sort_values("loan_id")
        .reset_index(drop=True)
    )

    if violated_unique.empty:
        st.info("Այս պահին ընտրված ֆիլտրերով KPI խախտում ունեցող վարկ չկա։")
    else:
        # Ավելացնում ենք հերթական համար՝ որ loan_id=500–ից չշփոթվես :)
        violated_unique.insert(0, "N", violated_unique.index + 1)

        st.caption(f"Ցուցադրվում է {len(violated_unique)} վարկ KPI խախտումով")

        st.dataframe(
            violated_unique[LOAN_COLUMNS],
            use_container_width=True,
            hide_index=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)

st.subheader("🏢 Վարկերի քանակ ըստ մասնաճյուղի")
branch_counts = filtered.groupby("branch_name").size().reset_index(name="count")

if not branch_counts.empty:
    fig2 = px.bar(
        branch_counts,
        x="branch_name",
        y="count",
        labels={"branch_name": "Մասնաճյուղ", "count": "Քանակ"},
        color_discrete_sequence=[FAST_PRIMARY],  # 👈 FAST մանուշակագույն
    )
    fig2.update_layout(
        template="simple_white",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        title_font=dict(color=FAST_DARK, size=18),
        font=dict(color=FAST_DARK),
    )
    st.plotly_chart(fig2, use_container_width=True)
else:
    st.info("Ֆիլտրի արդյունքում մասնաճյուղերի տվյալ չկա։")


merged = loans_df.merge(phase_df, on="loan_id", how="left")
avg_duration_by_product = merged.groupby("product_name")["duration_days"].mean().reset_index()

st.subheader("⏱ Միջին փուլային տևողություն ըստ վարկատեսակի")

merged = loans_df.merge(phase_df, on="loan_id", how="left")
avg_duration_by_product = merged.groupby("product_name")["duration_days"].mean().reset_index()

if not avg_duration_by_product.empty:
    fig3 = px.line(
        avg_duration_by_product,
        x="product_name",
        y="duration_days",
        markers=True,
        labels={
            "product_name": "Վարկատեսակ",
            "duration_days": "Միջին տևողություն (օր)"
        },
    )
    # գիծն ու marker–ները – FastBank գույնով
    fig3.update_traces(line_color=FAST_PRIMARY, marker=dict(color=FAST_PRIMARY, size=8))
    fig3.update_layout(
        template="simple_white",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        title_font=dict(color=FAST_DARK, size=18),
        font=dict(color=FAST_DARK),
    )
    st.plotly_chart(fig3, use_container_width=True)
else:
    st.info("Միջին փուլային տևողության համար տվյալներ չկան։")

