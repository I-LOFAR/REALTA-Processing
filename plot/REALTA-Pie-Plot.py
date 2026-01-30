#!/usr/bin/env python3
"""

"""

import argparse
import pandas as pd
import matplotlib.pyplot as plt
import smplotlib

CSV_PATH = "REALTA-Sched-Metadata.csv"


def autopct_hours(values):
    total = sum(values)

    def _fmt(pct):
        hours = pct * total / 100.0
        return f"{pct:.1f}%\n({hours:.1f} h)"

    return _fmt


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--from-date", dest="from_date", default=None)
    return p.parse_args()


def main() -> None:
    args = parse_args()

    df = pd.read_csv(CSV_PATH)

    df["start"] = pd.to_datetime(df["start"], errors="coerce")
    df["end"] = pd.to_datetime(df["end"], errors="coerce")

    if "duration_s" not in df.columns:
        df["duration_s"] = (df["end"] - df["start"]).dt.total_seconds()

    df["source"] = df.get("source", pd.Series(dtype=str)).astype(str)
    df = df.dropna(subset=["duration_s", "start"])
    df = df[df["duration_s"] >= 0]

    if args.from_date is not None:
        from_dt = pd.to_datetime(args.from_date, errors="raise")
        df = df[df["start"] >= from_dt]

    earliest = df["start"].min()
    earliest_str = earliest.strftime("%Y-%m-%d")

    is_sun = df["source"].str.strip().str.lower().eq("sun357")
    df["category"] = is_sun.map({True: "Sun", False: "Other"})

    totals_s = df.groupby("category")["duration_s"].sum()
    totals_hr = totals_s / 3600.0

    labels = list(totals_hr.index)

    colors = []
    for lbl in labels:
        if lbl == "Other":
            colors.append("none")
        elif lbl == "Sun":
            colors.append("tab:orange")

    fig, ax = plt.subplots()

    ax.pie(
        totals_hr.values,
        labels=labels,
        colors=colors,
        autopct=autopct_hours(totals_hr.values),
        startangle=90,
        wedgeprops=dict(edgecolor="black", linewidth=1.2),
    )

    ax.set_title(f"I-LOFAR observing time since {earliest_str}")
    ax.axis("equal")

    plt.tight_layout()
    plt.savefig("sun_vs_other_observing_time.png", dpi=200)


if __name__ == "__main__":
    main()
