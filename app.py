import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Iran Economic Dashboard",
    page_icon="🇮🇷",
    layout="wide"
)

# -----------------------------
# Load data
# -----------------------------
df = pd.read_csv("data.csv")

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
    ["نقشه استانی", "روند زمانی", "مقایسه استان‌ها"]
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
# KPI cards
# -----------------------------
year_df = df[df["year"] == year]

if parameter == "GDP":
    total_value = year_df["gdp"].sum()
    unit = "میلیارد دلار (ساختگی)"
elif parameter == "Population":
    total_value = year_df["population_m"].sum()
    unit = "میلیون نفر (ساختگی)"
else:
    total_value = year_df["unemployment"].mean()
    unit = "درصد"

c1, c2, c3 = st.columns(3)

with c1:
    st.metric("پارامتر انتخاب‌شده", parameter)

with c2:
    st.metric("سال", year)

with c3:
    if parameter == "Unemployment":
        st.metric("میانگین", f"{total_value:.1f}%")
    else:
        st.metric("مقدار کل", f"{total_value:,.1f}")

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
if chart_type == "نقشه استانی":
    st.subheader(f"{metric_label} — نقشه استانی — {year}")

    # برای اینکه پروتوتایپ بدون فایل GIS خارجی اجرا شود،
    # اینجا یک نقشه نقطه‌ای ساده با مختصات تقریبی استفاده شده است.
    coords = {
        "تهران": (51.39, 35.69),
        "اصفهان": (51.67, 32.65),
        "فارس": (52.53, 29.59),
        "خراسان رضوی": (59.60, 36.30),
        "آذربایجان شرقی": (46.29, 38.08),
    }

    map_df = year_df.copy()
    map_df["lon"] = map_df["province"].map(lambda x: coords[x][0])
    map_df["lat"] = map_df["province"].map(lambda x: coords[x][1])

    fig = px.scatter_map(
        map_df,
        lat="lat",
        lon="lon",
        size=metric_col,
        color=metric_col,
        hover_name="province",
        hover_data={metric_col: True, "lat": False, "lon": False},
        zoom=3.7,
        height=550,
        size_max=35,
        color_continuous_scale="Viridis"
    )

    fig.update_layout(
        mapbox_style="open-street-map",
        margin=dict(l=0, r=0, t=0, b=0)
    )

    st.plotly_chart(fig, use_container_width=True)

elif chart_type == "روند زمانی":
    st.subheader(f"{metric_label} — روند زمانی")

    if province == "همه استان‌ها":
        trend = df.groupby("year", as_index=False)[metric_col].mean()
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

    st.plotly_chart(fig, use_container_width=True)

else:
    st.subheader(f"{metric_label} — مقایسه استان‌ها — {year}")

    comparison = year_df.sort_values(metric_col, ascending=False)

    fig = px.bar(
        comparison,
        x="province",
        y=metric_col,
        text_auto=".2f",
        title=f"{metric_label} در سال {year}"
    )

    st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# Data table
# -----------------------------
with st.expander("نمایش داده‌ها"):
    st.dataframe(year_df, use_container_width=True)
