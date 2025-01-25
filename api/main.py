from fastapi import FastAPI, HTTPException, Query
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import base64
from io import BytesIO
from matplotlib.ticker import FuncFormatter
import io
import base64

app = FastAPI()

# Function to calculate compound interest
def compound_interest(principal, rate, time):
    return principal * (1 + rate) ** time

def abbreviate_large_numbers(x, pos):
    if x >= 1_000_000:
        return f"${x / 1_000_000:.1f}M"
    elif x >= 1_000:
        return f"${x / 1_000:.1f}k"
    else:
        return f"${x:.0f}"


@app.get("/go")
def generate_output(investment: float = Query(..., gt=0, description="Initial investment amount (must be greater than 0)")):
    if investment <= 0:
        raise HTTPException(status_code=400, detail="Investment amount must be greater than 0")

    time_years = np.arange(1, 26)
    rates = [0.10, 0.12, 0.15]
    colors = {"10%": "blue", "12%": "yellow", "15%": "red"}
    
    investment_data = {
        "Year": [],
        "Amount": [],
        "Rate": []
    }
    
    for rate in rates:
        for year in time_years:
            amount = compound_interest(investment, rate, year)
            investment_data["Year"].append(year)
            investment_data["Amount"].append(amount)
            investment_data["Rate"].append(f"{int(rate * 100)}%")
    
    df = pd.DataFrame(investment_data)
    marker_years = [20, 25]
    marker_data = df[df["Year"].isin(marker_years)]

    fig, ax = plt.subplots(figsize=(10, 6))

    for rate in df["Rate"].unique():
        rate_df = df[df["Rate"] == rate]
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
    ax.set_title("Investment Growth Over 25 years", fontsize=14, color="black")
    ax.set_xlabel("Year", fontsize=12, color="gray")
    ax.set_ylabel("Investment Amount", fontsize=12, color="gray")
    legend = ax.legend(title="Interest Rate", fontsize=10, title_fontsize=12)
    plt.tight_layout()
    
    # Save plot to a BytesIO object with compression
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    plt.show()
    buf.seek(0)
    
    # Get size of the image
    image_size = buf.getbuffer().nbytes
    
    # Encode to Base64
    base64_img = base64.b64encode(buf.getvalue()).decode('utf-8')
    
    # Close the buffer and plot
    buf.close()
    plt.close(fig)
    
    return "data:image/png;base64,"+ str(base64_img)
