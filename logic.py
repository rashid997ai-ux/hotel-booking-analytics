"""Data logic for the Hotel Booking Analytics dashboard (pandas only, no UI code)."""
from pathlib import Path
import numpy as np
import pandas as pd

DATA_PATH = Path(__file__).parent / "data" / "hotel_bookings_clean.csv"
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
LEAD_BINS = [-1, 7, 30, 90, 180, 365, 100000]
LEAD_LABELS = ["0-7 days", "8-30 days", "31-90 days", "91-180 days", "181-365 days", "Over 365 days"]


def load_data(path=DATA_PATH):
    df = pd.read_csv(path)
    # Revenue is counted only for stays that were NOT canceled.
    df["Revenue"] = np.where(df["Is Canceled"] == 0, df["ADR"] * df["Total Nights"], 0.0)
    df["Lead Bucket"] = pd.cut(df["Lead Time"], bins=LEAD_BINS, labels=LEAD_LABELS)
    return df


def apply_filters(df, hotels, years, segments, customers):
    mask = (
        df["Hotel"].isin(hotels)
        & df["Arrival Date Year"].isin(years)
        & df["Market Segment"].isin(segments)
        & df["Customer Type"].isin(customers)
    )
    return df[mask]


def kpis(df):
    n = len(df)
    if n == 0:
        return dict(bookings=0, cancel_rate=0.0, adr=0.0, nights=0.0, revenue=0.0)
    return dict(
        bookings=n,
        cancel_rate=float(df["Is Canceled"].mean()),
        adr=float(df["ADR"].mean()),
        nights=float(df["Total Nights"].mean()),
        revenue=float(df["Revenue"].sum()),
    )


def monthly_trend(df):
    g = df.groupby("Arrival Year Month").agg(
        Bookings=("Hotel", "size"), CancelRate=("Is Canceled", "mean")
    )
    return g.reset_index().sort_values("Arrival Year Month")


def by_hotel(df):
    g = df.groupby("Hotel").agg(Bookings=("Hotel", "size"), CancelRate=("Is Canceled", "mean"))
    return g.reset_index()


def by_segment(df):
    g = df.groupby("Market Segment").agg(Bookings=("Hotel", "size"), CancelRate=("Is Canceled", "mean"))
    return g.reset_index().sort_values("Bookings", ascending=True)


def by_customer(df):
    g = df.groupby("Customer Type").size().rename("Bookings").reset_index()
    return g.sort_values("Bookings", ascending=False)


def top_countries(df, n=10):
    g = df.groupby("Country").size().rename("Bookings").reset_index()
    return g.sort_values("Bookings", ascending=False).head(n).sort_values("Bookings", ascending=True)


def adr_by_month(df):
    g = df.groupby("Arrival Month Num")["ADR"].mean().reindex(range(1, 13))
    out = pd.DataFrame({"Month": MONTHS, "ADR": g.values})
    return out


def lead_time_cancel(df):
    g = df.groupby("Lead Bucket", observed=False).agg(
        Bookings=("Hotel", "size"), CancelRate=("Is Canceled", "mean")
    )
    g = g.reset_index()
    return g[g["Bookings"] > 0]


def insights(df):
    """Short plain-English findings computed from the filtered data."""
    out = []
    if len(df) == 0:
        return out
    m = df.groupby("Arrival Month Num").size()
    out.append(f"Busiest arrival month: {MONTHS[int(m.idxmax()) - 1]} ({int(m.max()):,} bookings).")
    seg = by_segment(df)
    seg = seg[seg["Bookings"] >= max(200, 0.01 * len(df))]
    if len(seg):
        top = seg.sort_values("CancelRate", ascending=False).iloc[0]
        out.append(f"Highest cancellation rate among larger segments: {top['Market Segment']} ({top['CancelRate']:.1%}).")
    lt = lead_time_cancel(df)
    lt = lt[lt["Bookings"] >= max(200, 0.01 * len(df))]
    if len(lt):
        t = lt.sort_values("CancelRate", ascending=False).iloc[0]
        out.append(f"Cancellations are highest when booked {str(t['Lead Bucket']).lower()} ahead ({t['CancelRate']:.1%}).")
    a = adr_by_month(df).dropna()
    if len(a):
        hi = a.loc[a["ADR"].idxmax()]
        out.append(f"Highest average daily rate: {hi['Month']} (${hi['ADR']:,.2f}).")
    return out


def fmt_money(x):
    if x >= 1_000_000:
        return f"${x/1_000_000:,.2f}M"
    if x >= 1_000:
        return f"${x/1_000:,.1f}K"
    return f"${x:,.0f}"
