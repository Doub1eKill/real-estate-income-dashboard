import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="Real Estate Income Dashboard",
    page_icon="🏠",
    layout="wide",
)

DATA_PATH = "data/income_real_estate.csv"
SOURCE_URL = "https://data.go.th/dataset/income-2"

# ชื่อประเภทรายได้ต้นฉบับยาวและมีคำสะกดผิด -> ทำชื่อย่อให้อ่านง่ายบนกราฟ
INCOME_TYPE_LABELS = {
    "งานทะเบียน": "ค่าธรรมเนียมงานทะเบียน",
    "งานรังวัด": "ค่าธรรมเนียมงานรังวัด",
    "รายได้เข้ารัฐ": "รายได้เข้ารัฐ",
    "รายได้นำส่งท้องถิ่น": "รายได้นำส่งท้องถิ่น",
    "ภาษีนิติบุคคคล": "ภาษีเงินได้นิติบุคคล",
    "ภาษีบุคคลธรรมดา": "ภาษีเงินได้บุคคลธรรมดา",
    "ธุรกิจเฉพาะเพื่อกรมสรรพากร": "ภาษีธุรกิจเฉพาะ (สรรพากร)",
    "ธุรกิจเฉพาะเพื่อองค์กรปกครองส่วนท้องถิ่น": "ภาษีธุรกิจเฉพาะ (อปท.)",
    "ค่าใช้จ่ายในการจัดเก็บภาษีอากรให้เแก่ราชการส่วนท้องถิ่น": "ค่าใช้จ่ายจัดเก็บภาษีให้ อปท.",
    "อากรแสตมป์": "อากรแสตมป์",
}


@st.cache_data
def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH)
    df["income_type"] = df["income_type"].str.strip().replace(INCOME_TYPE_LABELS)
    df["region"] = df["region"].str.strip()
    df["year"] = df["year"].astype(int)
    df["amount_baht"] = pd.to_numeric(df["amount_baht"], errors="coerce").fillna(0).round(2)
    return df


df = load_data()

# ---------------- Sidebar filters ----------------
st.sidebar.header("🔎 Filter ข้อมูล")

years = sorted(df["year"].unique())
regions = list(df["region"].unique())
income_types = list(df["income_type"].unique())

sel_years = st.sidebar.multiselect("ปีงบประมาณ (พ.ศ.)", years, default=years)
sel_regions = st.sidebar.multiselect("ภาค", regions, default=regions)
sel_types = st.sidebar.multiselect("ประเภทรายได้", income_types, default=income_types)
unit = st.sidebar.radio("หน่วยแสดงผล", ["ล้านบาท", "บาท"], horizontal=True)

divisor = 1_000_000 if unit == "ล้านบาท" else 1

filtered = df[
    df["year"].isin(sel_years)
    & df["region"].isin(sel_regions)
    & df["income_type"].isin(sel_types)
].copy()
filtered["amount"] = filtered["amount_baht"] / divisor

# ---------------- Header ----------------
st.title("🏠 Real Estate Income Dashboard")
st.markdown("**Dashboard รายได้จากการซื้อขายอสังหาริมทรัพย์ (กรมที่ดิน)**")
st.write(
    "ใช้สำหรับวิเคราะห์รายได้ ค่าธรรมเนียม และภาษีที่จัดเก็บจากการซื้อขายอสังหาริมทรัพย์ "
    "แยกตามภาคและประเภทรายได้ ปีงบประมาณ พ.ศ. 2566–2568 "
    "โดยสามารถกรองข้อมูลตามปี ภาค และประเภทรายได้ได้จากแถบด้านซ้าย"
)

if filtered.empty:
    st.warning("ไม่พบข้อมูลตามเงื่อนไขที่เลือก กรุณาเลือกตัวกรองอย่างน้อย 1 รายการในแต่ละหมวด")
    st.stop()


def fmt(value: float) -> str:
    return f"{value:,.2f}" if unit == "ล้านบาท" else f"{value:,.0f}"


# ---------------- KPI ----------------
st.subheader("📊 สรุปข้อมูล")

total = filtered["amount"].sum()
by_year = filtered.groupby("year")["amount"].sum().sort_index()
by_region = filtered.groupby("region")["amount"].sum().sort_values(ascending=False)
by_type = filtered.groupby("income_type")["amount"].sum().sort_values(ascending=False)

delta = None
if len(by_year) >= 2:
    prev, last = by_year.iloc[-2], by_year.iloc[-1]
    if prev:
        delta = f"{(last - prev) / prev * 100:+.1f}% ({by_year.index[-1]} เทียบ {by_year.index[-2]})"

c1, c2, c3, c4 = st.columns(4)
c1.metric(f"รายได้รวม ({unit})", fmt(total), border=True)
c2.metric(
    f"รายได้ปี {by_year.index[-1]} ({unit})",
    fmt(by_year.iloc[-1]),
    delta=delta,
    border=True,
)
c3.metric(f"ภาคที่มีรายได้สูงสุด ({unit})", fmt(by_region.iloc[0]), by_region.index[0],
          delta_color="off", delta_arrow="off", border=True)
c4.metric(f"ประเภทรายได้สูงสุด ({unit})", fmt(by_type.iloc[0]), by_type.index[0],
          delta_color="off", delta_arrow="off", border=True)

st.divider()

# ---------------- Chart 1: trend by year ----------------
st.subheader("📈 แนวโน้มรายได้รายปี")
trend = filtered.groupby(["year", "region"], as_index=False)["amount"].sum()
fig_trend = px.line(
    trend,
    x="year",
    y="amount",
    color="region",
    markers=True,
    labels={"year": "ปีงบประมาณ", "amount": f"รายได้ ({unit})", "region": "ภาค"},
    title="แนวโน้มรายได้รวมแยกตามภาค",
)
fig_trend.update_xaxes(tickmode="array", tickvals=sorted(trend["year"].unique()))
st.plotly_chart(fig_trend, width="stretch")

# ---------------- Chart 2: compare regions ----------------
st.subheader("🗺️ รายได้ตามภาค")
region_year = filtered.groupby(["region", "year"], as_index=False)["amount"].sum()
region_year["year"] = region_year["year"].astype(str)
fig_region = px.bar(
    region_year,
    x="region",
    y="amount",
    color="year",
    barmode="group",
    labels={"region": "ภาค", "amount": f"รายได้ ({unit})", "year": "ปีงบประมาณ"},
    title="เปรียบเทียบรายได้แต่ละภาคในแต่ละปี",
    category_orders={"region": list(by_region.index)},
)
st.plotly_chart(fig_region, width="stretch")

# ---------------- Chart 3 & 4: income type ----------------
st.subheader("💰 โครงสร้างรายได้")
left, right = st.columns(2)

with left:
    fig_pie = px.pie(
        by_type.reset_index(),
        names="income_type",
        values="amount",
        hole=0.4,
        title="สัดส่วนรายได้ตามประเภท",
    )
    fig_pie.update_traces(textposition="inside", textinfo="percent")
    fig_pie.update_layout(legend=dict(orientation="h", y=-0.1))
    st.plotly_chart(fig_pie, width="stretch")

with right:
    top_n = len(by_type)
    if top_n > 1:
        top_n = st.slider("จำนวนประเภทรายได้ที่แสดง (Top N)", 1, top_n, min(5, top_n))
    top = by_type.head(top_n).reset_index().sort_values("amount")
    fig_top = px.bar(
        top,
        x="amount",
        y="income_type",
        orientation="h",
        text_auto=",.2f" if unit == "ล้านบาท" else ",.0f",
        labels={"income_type": "ประเภทรายได้", "amount": f"รายได้ ({unit})"},
        title=f"Top {top_n} ประเภทรายได้สูงสุด",
    )
    st.plotly_chart(fig_top, width="stretch")

# ---------------- Chart 5: heatmap ----------------
st.subheader("🔥 รายได้ตามภาค × ประเภทรายได้")
pivot = filtered.pivot_table(
    index="income_type", columns="region", values="amount", aggfunc="sum", fill_value=0
)
fig_heat = px.imshow(
    pivot,
    aspect="auto",
    color_continuous_scale="Reds",
    labels={"x": "ภาค", "y": "ประเภทรายได้", "color": unit},
    text_auto=",.0f",
)
fig_heat.update_layout(height=520)
st.plotly_chart(fig_heat, width="stretch")

# ---------------- Table & download ----------------
st.subheader("📋 รายละเอียดข้อมูล")
table = filtered.rename(
    columns={
        "year": "ปีงบประมาณ",
        "region": "ภาค",
        "income_type": "ประเภทรายได้",
        "amount_baht": "จำนวนเงิน (บาท)",
    }
)[["ปีงบประมาณ", "ภาค", "ประเภทรายได้", "จำนวนเงิน (บาท)"]]
st.dataframe(
    table,
    width="stretch",
    hide_index=True,
    column_config={
        "ปีงบประมาณ": st.column_config.NumberColumn(format="%d"),
        "จำนวนเงิน (บาท)": st.column_config.NumberColumn(format="%,.2f"),
    },
)

st.subheader("⬇️ Download")
st.download_button(
    "ดาวน์โหลดข้อมูลที่กรองแล้ว (CSV)",
    data=table.to_csv(index=False).encode("utf-8-sig"),
    file_name="real_estate_income_filtered.csv",
    mime="text/csv",
)

st.divider()
st.caption(
    f"ที่มาข้อมูล: กรมที่ดิน ผ่าน [data.go.th]({SOURCE_URL}) | "
    "Real Estate Income Dashboard | Developed with Streamlit + Pandas + Plotly"
)
