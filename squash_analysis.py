import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# 1. Load the data sheet
try:
    df = pd.read_csv("squash_data.csv")
    print("✅ Successfully loaded 'squash_data.csv'!")
except FileNotFoundError:
    print("❌ Error: Could not find 'squash_data.csv' in this folder.")

# 2. Historical vs Modern Statistical Comparison
print("\n=== HISTORICAL VS MODERN TACTICAL METRICS ===")
eras = df["Era"].unique()

for era in eras:
    print(f"\n--- Era: {era} ---")
    era_df = df[df["Era"] == era]
    
    # Calculate Efficiency Formula: (Winners - Errors) / Total Shots
    stats = era_df.groupby("Shot_Type")["Outcome"].value_counts().unstack(fill_value=0)
    for col in ["Winner", "Error", "In Play"]:
        if col not in stats.columns:
            stats[col] = 0
            
    stats["Total_Shots"] = stats[["Winner", "Error", "In Play"]].sum(axis=1)
    stats["Efficiency_Index"] = (stats["Winner"] - stats["Error"]) / stats["Total_Shots"]
    print(stats[["Total_Shots", "Winner", "Error", "Efficiency_Index"]])

# 3. Setup Spatial Grid Coordinates for Heatmapping
zone_coords = {
    1: (1.6, 8.0),  # Front Left (Nick/Drop)
    2: (4.8, 8.0),  # Front Right (Nick/Drop)
    3: (3.2, 4.8),  # Mid-Court (Around the T)
    4: (1.6, 1.6),  # Back Left (Deep Corner)
    5: (4.8, 1.6),  # Back Right (Deep Corner)
}

df["X"] = df["Estimated_Zone"].map(lambda z: zone_coords.get(z, (3.2, 4.8)))
df["Y"] = df["Estimated_Zone"].map(lambda z: zone_coords.get(z, (3.2, 4.8)))

# Add statistical jitter noise so dots don't overlay seamlessly
df["X"] += np.random.uniform(-0.4, 0.4, len(df))
df["Y"] += np.random.uniform(-0.4, 0.4, len(df))

# 4. Generate Side-by-Side Spatial Maps
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 9.75))

def draw_court(ax, title_name, era_filter):
    # Draw squash court boundaries (6.4m x 9.75m)
    ax.plot([0, 6.4, 6.4, 0, 0], [0, 0, 9.75, 9.75, 0], color="black", lw=2)
    ax.plot([0, 6.4], [4.26, 4.26], color="red", linestyle="--") # Short line
    ax.plot([3.2, 3.2], [0, 4.26], color="red", linestyle="--") # Half court line
    
    era_data = df[df["Era"] == era_filter]
    
    winners = era_data[era_data["Outcome"] == "Winner"]
    errors = era_data[era_data["Outcome"] == "Error"]
    in_play = era_data[era_data["Outcome"] == "In Play"]
    
    ax.scatter(in_play["X"], in_play["Y"], color="blue", s=80, alpha=0.4, label="In Play")
    ax.scatter(winners["X"], winners["Y"], color="green", s=120, edgecolors="black", label="Winners")
    ax.scatter(errors["X"], errors["Y"], color="red", s=120, edgecolors="black", label="Errors")
    
    ax.set_title(title_name, fontsize=12, pad=10)
    ax.set_xlim(-0.5, 7.0)
    ax.set_ylim(-0.5, 10.5)
    ax.legend(loc="upper right", fontsize=8)

# Render historical era on the left, modern era on the right
draw_court(ax1, "Vintage Era Strategy Mapping", eras[0] if len(eras) > 0 else "Vintage")
draw_court(ax2, "Modern Era Strategy Mapping", eras[1] if len(eras) > 1 else "Modern")

plt.suptitle("Evolutionary Spatial Analysis of Professional Squash", fontsize=16, y=0.95)
plt.show()
