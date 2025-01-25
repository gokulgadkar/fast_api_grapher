from fastapi import FastAPI, HTTPException, Query
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import io
import base64

app = FastAPI()

# Function to calculate compound interest for a lump sum investment
def compound_interest(principal, rate, time):
    return principal * (1 + rate) ** time

# Function to calculate compound interest for monthly recurring investments (SIP)
def sip_growth(monthly_investment, rate, time):
    monthly_rate = rate / 12  # Convert annual rate to monthly
    months = time * 12  # Convert years to months
    return monthly_investment * (((1 + monthly_rate) ** months - 1) / monthly_rate) * (1 + monthly_rate)

# Formatter for large numbers
def abbreviate_large_numbers(x, pos):
    if x >= 1_000_000:
        return f"${x / 1_000_000:.1f}M"
    elif x >= 1_000:
        return f"${x / 1_000:.1f}k"
    else:
        return f"${x:.0f}"

# Function to generate the Base64-encoded graph for either SIP or Lump Sum
def generate_graph(data, title, colors):
    fig, ax = plt.subplots(figsize=(10, 6))

    marker_years = [20, 25]
    marker_data = data[data["Year"].isin(marker_years)]

    for rate in data["Rate"].unique():
        rate_df = data[data["Rate"] == rate]
        ax.plot(
            rate_df["Year"], rate_df["Amount"], label=rate, 
            color=colors[rate], marker="o", markersize=5
        )
        for _, row in marker_data[marker_data["Rate"] == rate].iterrows():
            abbreviated_amount = abbreviate_large_numbers(row["Amount"], None)
            ax.text(
                row["Year"], row["Amount"] * 1.08,
                f"{abbreviated_amount}", fontsize=10, color="black", ha="center"
            )

    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("black")
    ax.spines["bottom"].set_color("black")
    ax.tick_params(axis="x", colors="black")
    ax.tick_params(axis="y", colors="black")
    ax.yaxis.set_major_formatter(FuncFormatter(abbreviate_large_numbers))
    ax.set_title(title, fontsize=14, color="black")
    ax.set_xlabel("Year", fontsize=12, color="gray")
    ax.set_ylabel("Investment Amount", fontsize=12, color="gray")
    legend = ax.legend(title="Interest Rate", fontsize=10, title_fontsize=12)
    plt.tight_layout()
    
    # Save plot to a BytesIO object
    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    base64_img = base64.b64encode(buf.getvalue()).decode("utf-8")
    buf.close()
    plt.close(fig)
    
    return base64_img


@app.get("/investments")
def calculate_investments(
    lump: float = Query(..., ge=0, description="Lump sum investment amount (must be greater than or equal to 0)"),
    monthly: float = Query(..., ge=0, description="Monthly SIP investment amount (must be greater than or equal to 0)")
):
    if lump == 0 and monthly == 0:
        raise HTTPException(status_code=400, detail="At least one of lump sum or monthly investment must be greater than 0")

    time_years = np.arange(1, 26)
    rates = [0.10, 0.12, 0.15]
    colors = {"10%": "blue", "12%": "yellow", "15%": "red"}

    # Calculate lump sum growth
    lump_data = {"Year": [], "Amount": [], "Rate": []}
    if lump > 0:
        for rate in rates:
            for year in time_years:
                amount = compound_interest(lump, rate, year)
                lump_data["Year"].append(year)
                lump_data["Amount"].append(amount)
                lump_data["Rate"].append(f"{int(rate * 100)}%")
        lump_df = pd.DataFrame(lump_data)
        lump_graph = generate_graph(lump_df, "Lump Sum Investment Growth Over 25 Years", colors)
    else:
        lump_graph = None

    # Calculate SIP growth
    sip_data = {"Year": [], "Amount": [], "Rate": []}
    if monthly > 0:
        for rate in rates:
            for year in time_years:
                amount = sip_growth(monthly, rate, year)
                sip_data["Year"].append(year)
                sip_data["Amount"].append(amount)
                sip_data["Rate"].append(f"{int(rate * 100)}%")
        sip_df = pd.DataFrame(sip_data)
        sip_graph = generate_graph(sip_df, "SIP Investment Growth Over 25 Years", colors)
    else:
        sip_graph = None

    # Return both graphs as Base64
    return {
        "lump": f"data:image/png;base64,{lump_graph}" if lump_graph else None,
        "monthly": f"data:image/png;base64,{sip_graph}" if sip_graph else None
    }
