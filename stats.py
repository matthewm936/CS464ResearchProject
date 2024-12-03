import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

file_path = "data1.csv"
df = pd.read_csv(file_path)

df.columns = ["Participant_ID", "Trial", "Avg_Time", "Correctness_Rate", "Num_Keys", "Combination_Correctness"]

df["Adjusted_Trial"] = df.groupby("Participant_ID").cumcount()

mean_stats = df.groupby("Participant_ID").mean()

print("Mean Statistics Per Participant:")
print(mean_stats)

plt.figure(figsize=(12, 6))

for participant in df["Participant_ID"].unique():
    participant_data = df[df["Participant_ID"] == participant]
    plt.plot(
        participant_data["Adjusted_Trial"], 
        participant_data["Avg_Time"], 
        marker="o", 
        label=f"{participant}"
    )

plt.title("Performance")
plt.xlabel("Trial #")
plt.ylabel("Avg Time")
plt.legend(title="Participants")
plt.grid(True)
plt.show()

overall_stats = df.describe()
print("\nOverall Statistics:")
print(overall_stats)
