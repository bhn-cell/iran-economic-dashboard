import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------------
# Page configuration
# -----------------------------
st.set_page_config(
    page_title="Iran Economic Dashboard",
    page_icon="🇮🇷",
    layout="wide"
)

# -----------------------------
# Load data
# -----------------------------
try:
    df = pd.read_csv("data.csv")
except FileNotFoundError:
    st.error("فایل data.csv پیدا نشد. لطفاً آن را کنار فایل app.py قرار دهید.")
    st.stop()

# -----------------------------
# Page title
# -----------------------------
st.title("🇮🇷 Iran Economic Dashboard")
st.caption("نمونه اولیه با داده‌های ساختگی — فقط برای نمایش ساختار داشبورد")

# -----------------------------
# Sidebar controls
# -----------------------------
st.sidebar.header("فیلترها")

parameter = st.sidebar.selectbox(
    "پارامتر",
    ["GDP", "Population", "Unemployment"]
)

chart_type = st.sidebar.selectbox(
    "نوع نمودار",
    ["روند زمانی", "مقایسه استان‌ها"]
)

year = st.sidebar.selectbox(
    "سال",
    sorted(df["year"].unique()),
    index=len(df["year"].unique()) - 1
)

province = st.sidebar.selectbox(
    "استان",
    ["همه استان‌ها"] + sorted(df["province"].unique())
)

# -----------------------------
# KPI data
# -----------------------------
year_df = df[df["year"] == year]

if parameter == "GDP":
    total_value = year_df["gdp"].sum()

elif parameter == "Population":
    total_value = year_df["population_m"].sum()

else:
    total_value = year_df["unemployment"].mean()

# -----------------------------
# KPI cards
# -----------------------------
c1, c2, c3 = st.columns(3)

with c1:
    st.metric(
        "پارامتر انتخاب‌شده",
        parameter
    )

with c2:
    st.metric(
        "سال",
        year
    )

with c3:
    if parameter == "Unemployment":
        st.metric(
            "میانگین",
            f"{total_value:.1f}%"
        )
    elif parameter == "Population":
        st.metric(
            "جمعیت کل",
            f"{total_value:,.1f} میلیون نفر"
        )
    else:
        st.metric(
            "GDP کل",
            f"{total_value:,.1f}"
        )

st.divider()

# -----------------------------
# Select metric
# -----------------------------
metric_map = {
    "GDP": ("gdp", "GDP"),
    "Population": ("population_m", "Population"),
    "Unemployment": ("unemployment", "Unemployment")
}

metric_col, metric_label = metric_map[parameter]

# -----------------------------
# Chart
# -----------------------------
if chart_type == "روند زمانی":

    st.subheader(f"{metric_label} — روند زمانی")

    if province == "همه استان‌ها":

        trend = (
            df.groupby("year", as_index=False)[metric_col]
            .mean()
        )

        fig = px.line(
            trend,
            x="year",
            y=metric_col,
            markers=True,
            title=f"میانگین {metric_label} استان‌ها"
        )

    else:

        trend = df[df["province"] == province]

        fig = px.line(
            trend,
            x="year",
            y=metric_col,
            markers=True,
            title=f"{metric_label} — {province}"
        )

    fig.update_layout(
        xaxis_title="سال",
        yaxis_title=metric_label,
        margin=dict(l=20, r=20, t=60, b=20)
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# -----------------------------
# Province comparison
# -----------------------------
else:

    st.subheader(
        f"{metric_label} — مقایسه استان‌ها — {year}"
    )

    comparison = (
        year_df
        .sort_values(metric_col, ascending=False)
    )

    fig = px.bar(
        comparison,
        x="province",
        y=metric_col,
        text_auto=".2f",
        title=f"{metric_label} در سال {year}"
    )

    fig.update_layout(
        xaxis_title="استان",
        yaxis_title=metric_label,
        margin=dict(l=20, r=20, t=60, b=20)
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# -----------------------------
# Data table
# -----------------------------
with st.expander("نمایش داده‌ها"):

    st.dataframe(
        year_df,
        use_container_width=True
    )
