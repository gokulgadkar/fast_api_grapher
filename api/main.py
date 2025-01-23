from fastapi import FastAPI, HTTPException, Query
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import base64
from io import BytesIO

app = FastAPI()

# Function to calculate compound interest
def compound_interest(principal, rate, time):
    return principal * (1 + rate) ** time

@app.get("/go/")
def generate_output(investment: float = Query(..., gt=0, description="Initial investment amount (must be greater than 0)")):
    if investment <= 0:
        raise HTTPException(status_code=400, detail="Investment amount must be greater than 0")

    time_years = np.arange(1, 21)  # 20 years
    rates = [0.10, 0.12, 0.15]  # 10%, 12%, 15%
    
    # Create a DataFrame to store results
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
    
    # Convert data to a DataFrame
    df = pd.DataFrame(investment_data)
    
    # Generate the graph and save it to a buffer
    buffer = BytesIO()
    sns.set_theme(style="whitegrid")
    plt.figure(figsize=(8, 4))
    sns.lineplot(data=df, x="Year", y="Amount", hue="Rate", marker="o")
    plt.title("Investment Growth Over 20 Years", fontsize=12)
    plt.xlabel("Year", fontsize=10)
    plt.ylabel("Investment Amount (in $)", fontsize=10)
    plt.legend(title="Interest Rate", fontsize=8)
    plt.xticks(ticks=range(1, 21), fontsize=8)
    plt.yticks(fontsize=8)
    plt.tight_layout()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    
    # Convert to base64
    img_base64 = base64.b64encode(buffer.read()).decode("utf-8")
    buffer.close()
    
    return {"image_base64": img_base64}
