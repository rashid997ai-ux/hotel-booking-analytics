import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

import logic as L

# ---------- Page setup ----------
st.set_page_config(page_title="Hotel Booking Analytics", page_icon="🏨", layout="wide")

NAVY, CARD, EDGE = "#071226", "#0E1E3A", "#1E4A7A"
CYAN, BLUE, VIOLET, AMBER = "#22D3EE", "#2563EB", "#8B5CF6", "#F59E0B"
TXT, MUTE, GRID = "#E6F1FF", "#8FB3D9", "#143055"
PALETTE = [CYAN, BLUE, VIOLET, AMBER, "#94A3B8"]

st.markdown(
    """
<style>
.stApp {background:#071226; color:#E6F1FF;}
.block-container {max-width:1300px; padding-top:1.6rem; padding-bottom:2rem;}
[data-testid="stSidebar"] {background:#0A1930; border-right:1px solid #143055;}
[data-testid="stHeader"] {background:transparent;}
h1,h2,h3,h4,p,label,span,li {color:#E6F1FF;}
.hero {background:linear-gradient(110deg,#0E1E3A,#123A7A,#0E7490); border:1px solid #1E4A7A;
       border-radius:18px; padding:clamp(16px,3vw,26px); margin-bottom:18px;}
.hero h1 {font-size:clamp(1.4rem,4vw,2.3rem); line-height:1.2; margin:0 0 6px 0; color:#FFFFFF;}
.hero p {margin:0; color:#CFE6FA; font-size:clamp(.8rem,1.8vw,.95rem);}
.kpi-grid {display:grid; grid-template-columns:repeat(auto-fit,minmax(190px,1fr)); gap:14px; margin-bottom:18px;}
.kpi {background:#0E1E3A; border:1px solid #1E4A7A; border-radius:14px; padding:16px 18px;
      box-shadow:0 6px 20px rgba(0,0,0,.35);}
.kpi-label {color:#8FB3D9; font-size:.72rem; font-weight:700; letter-spacing:.06em; text-transform:uppercase;}
.kpi-value {color:#22D3EE; font-size:clamp(1.5rem,3vw,2rem); font-weight:700; margin-top:6px; line-height:1.1;}
.kpi-note {color:#6B8DB5; font-size:.72rem; margin-top:4px;}
[data-testid="stPlotlyChart"] {border:1px solid #1E4A7A; border-radius:14px; overflow:hidden; background:#0E1E3A;}
.insight-box {background:#0E1E3A; border:1px solid #1E4A7A; border-left:4px solid #22D3EE;
border-radius:12px; padding:14px 18px; margin:6px 0 18px 0;}
.insight-box li {margin:4px 0; font-size:.92rem;}
.foot {text-align:center; color:#6B8DB5; font-size:.78rem; margin-top:26px;}
section[data-testid="stSidebar"] [data-baseweb="tag"] {background-color:#1B3A66 !important; border:1px solid #2F5C96 !important;}
section[data-testid="stSidebar"] [data-baseweb="tag"] * {color:#CFE6FA !important; fill:#CFE6FA !important;}
@media (max-width: 640px) {.block-container {padding-left:.8rem; padding-right:.8rem;}}
</style>
""",
    unsafe_allow_html=True,
)


# ---------- Data ----------
@st.cache_data(show_spinner="Loading data...")
def get_data():
    return L.load_data()


df = get_data()


# ---------- Helpers ----------
def style(fig, title, height=340, legend=False):
    fig.update_layout(
        title=dict(text=title, x=0.02, y=0.95, font=dict(size=15, color=TXT)),
        height=height,
        margin=dict(l=12, r=12, t=58, b=12),
        paper_bgcolor=CARD,
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=TXT, size=12),
        showlegend=legend,
        dragmode=False,
        hoverlabel=dict(bgcolor=NAVY, font_color=TXT),
        legend=dict(orientation="h", y=-0.15, font=dict(color=TXT)),
    )
    # fixedrange stops touch-drag and zoom, so charts do not shake on phones
    fig.update_xaxes(fixedrange=True, gridcolor=GRID, zeroline=False, linecolor=EDGE)
    fig.update_yaxes(fixedrange=True, gridcolor=GRID, zeroline=False, linecolor=EDGE)
    return fig


def show(fig):
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False, "scrollZoom": False})


def kpi_card(label, value, note=""):
    return (
        f'<div class="kpi"><div class="kpi-label">{label}</div>'
        f'<div class="kpi-value">{value}</div><div class="kpi-note">{note}</div></div>'
    )


# ---------- Sidebar filters ----------
st.sidebar.markdown("## Filters")
all_hotels = sorted(df["Hotel"].unique())
all_years = sorted(df["Arrival Date Year"].unique())
all_segments = sorted(df["Market Segment"].unique())
all_customers = sorted(df["Customer Type"].unique())

hotels = st.sidebar.multiselect("Hotel", all_hotels, default=all_hotels)
years = st.sidebar.multiselect("Arrival year", all_years, default=all_years)
segments = st.sidebar.multiselect("Market segment", all_segments, default=all_segments)
customers = st.sidebar.multiselect("Customer type", all_customers, default=all_customers)
st.sidebar.caption("Every number and chart on the page follows these filters.")

fdf = L.apply_filters(df, hotels, years, segments, customers)

# ---------- Header ----------
st.markdown(
    """
<div class="hero">
  <h1>Hotel Booking Analytics</h1>
  <p>Interactive dashboard of 119,209 cleaned bookings (2015 to 2017) | City Hotel and Resort Hotel</p>
</div>
""",
    unsafe_allow_html=True,
)

if fdf.empty:
    st.warning("No bookings match the selected filters. Please select at least one option in every filter.")
    st.stop()

# ---------- KPI cards ----------
k = L.kpis(fdf)
cards = [
    kpi_card("Total bookings", f"{k['bookings']:,}", f"{k['bookings'] / len(df):.0%} of all bookings"),
    kpi_card("Cancellation rate", f"{k['cancel_rate']:.1%}", "Share of bookings canceled"),
    kpi_card("Average daily rate", f"${k['adr']:,.2f}", "Average price per night"),
    kpi_card("Average stay", f"{k['nights']:.1f} nights", "Weekend plus weekday nights"),
    kpi_card("Revenue (stays kept)", L.fmt_money(k["revenue"]), "ADR x nights, canceled excluded"),
]
st.markdown('<div class="kpi-grid">' + "".join(cards) + "</div>", unsafe_allow_html=True)

# ---------- Key insights ----------
notes = L.insights(fdf)
if notes:
    items = "".join(f"<li>{n}</li>" for n in notes)
    st.markdown(f'<div class="insight-box"><b>Key insights</b><ul>{items}</ul></div>', unsafe_allow_html=True)

# ---------- Trend ----------
trend = L.monthly_trend(fdf)
fig = make_subplots(specs=[[{"secondary_y": True}]])
fig.add_trace(go.Bar(x=trend["Arrival Year Month"], y=trend["Bookings"], name="Bookings", marker_color=CYAN), secondary_y=False)
fig.add_trace(
    go.Scatter(x=trend["Arrival Year Month"], y=trend["CancelRate"], name="Cancellation rate",
               mode="lines+markers", line=dict(color=AMBER, width=3)),
    secondary_y=True,
)
style(fig, "Bookings and cancellation rate by month", height=380, legend=True)
fig.update_yaxes(tickformat=",", secondary_y=False)
fig.update_yaxes(tickformat=".0%", rangemode="tozero", showgrid=False, secondary_y=True)
fig.update_xaxes(tickangle=-45)
show(fig)

# ---------- Row 1 ----------
c1, c2 = st.columns(2)
with c1:
    h = L.by_hotel(fdf)
    fig = px.bar(h, x="Hotel", y="CancelRate", color_discrete_sequence=[BLUE])
    fig.update_traces(texttemplate="%{y:.1%}", textposition="outside", cliponaxis=False)
    style(fig, "Cancellation rate by hotel")
    fig.update_yaxes(tickformat=".0%", range=[0, max(0.1, float(h["CancelRate"].max()) * 1.3)], title=None)
    fig.update_xaxes(title=None)
    show(fig)
with c2:
    seg = L.by_segment(fdf)
    fig = px.bar(seg, x="Bookings", y="Market Segment", orientation="h", color_discrete_sequence=[CYAN])
    fig.update_traces(texttemplate="%{x:,}", textposition="outside", cliponaxis=False)
    style(fig, "Bookings by market segment")
    fig.update_xaxes(title=None, tickformat=",")
    fig.update_yaxes(title=None)
    show(fig)

# ---------- Row 2 ----------
c3, c4 = st.columns(2)
with c3:
    ct = L.by_customer(fdf)
    fig = px.pie(ct, names="Customer Type", values="Bookings", hole=0.6, color_discrete_sequence=PALETTE)
    fig.update_traces(textinfo="percent", marker=dict(line=dict(color=CARD, width=2)))
    style(fig, "Bookings by customer type", legend=True)
    show(fig)
with c4:
    tc = L.top_countries(fdf)
    fig = px.bar(tc, x="Bookings", y="Country", orientation="h", color_discrete_sequence=[VIOLET])
    fig.update_traces(texttemplate="%{x:,}", textposition="outside", cliponaxis=False)
    style(fig, "Top 10 guest countries")
    fig.update_xaxes(title=None, tickformat=",")
    fig.update_yaxes(title=None)
    show(fig)

# ---------- Row 3 ----------
c5, c6 = st.columns(2)
with c5:
    a = L.adr_by_month(fdf)
    fig = px.line(a, x="Month", y="ADR", markers=True, color_discrete_sequence=[CYAN])
    fig.update_traces(line=dict(width=3))
    style(fig, "Average daily rate by month")
    fig.update_yaxes(tickprefix="$", title=None, rangemode="tozero")
    fig.update_xaxes(title=None)
    show(fig)
with c6:
    lt = L.lead_time_cancel(fdf)
    fig = px.bar(lt, x="Lead Bucket", y="CancelRate", color_discrete_sequence=[AMBER])
    fig.update_traces(texttemplate="%{y:.0%}", textposition="outside", cliponaxis=False)
    style(fig, "Cancellation rate by booking lead time")
    fig.update_yaxes(tickformat=".0%", range=[0, max(0.1, float(lt["CancelRate"].max()) * 1.3)], title=None)
    fig.update_xaxes(title=None)
    show(fig)

# ---------- Data table ----------
st.markdown("### Booking data")
show_cols = ["Hotel", "Arrival Year Month", "Market Segment", "Customer Type", "Country",
             "Lead Time", "Total Nights", "Total Guests", "ADR", "Is Canceled"]
st.caption(f"Showing the first 500 of {len(fdf):,} filtered bookings.")
st.dataframe(fdf[show_cols].head(500), hide_index=True, width="stretch")
if st.checkbox("Prepare CSV download of the filtered data"):
    st.download_button(
        "Download filtered data (CSV)",
        data=fdf[show_cols].to_csv(index=False).encode("utf-8"),
        file_name="hotel_bookings_filtered.csv",
        mime="text/csv",
    )

st.markdown(
    '<div class="foot">Self-practice portfolio project by Rashid Data Works | '
    "Data: public Hotel Booking Demand dataset (Kaggle), cleaned with Python and Pandas | "
    "Names, emails, phone numbers and card details were removed.</div>",
    unsafe_allow_html=True,
)
