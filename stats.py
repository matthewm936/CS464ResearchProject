import pandas as pd
import matplotlib.pyplot as plt

file_path = "data1.csv"
df = pd.read_csv(file_path)

df.columns = ["Participant_ID", "Trial", "Avg_Time", "Correctness_Rate", "Num_Keys", "Combination_Correctness"]

df["Adjusted_Trial"] = df.groupby("Participant_ID").cumcount()

mean_stats = df.groupby("Participant_ID").mean()

novice_group = ['Wolverine', 'Tony Stark', 'Batman1']
df['Group'] = df['Participant_ID'].apply(lambda x: 'Novice' if x in novice_group else 'Experienced')

summary_stats = df.groupby('Group').agg({
    'Avg_Time': ['mean', 'std'],
    'Correctness_Rate': ['mean', 'std'],
    'Num_Keys': ['mean', 'std'],
    'Combination_Correctness': ['mean', 'std']
}).reset_index()

overall_stats = df.describe()

text_content = (
    "Mean Statistics Per Participant:\n\n" +
    mean_stats.to_string() +
    "\n\nPerformance Summary by Group:\n\n" +
    summary_stats.to_string(index=False) +
    "\n\nOverall Statistics:\n\n" +
    overall_stats.to_string()
)

fig, ax = plt.subplots(figsize=(12, 12))
ax.axis('off')
ax.text(0, 1, text_content, fontsize=10, va='top', family='monospace')
plt.tight_layout()

statistics_file = "statistics_summary.png"
plt.savefig(statistics_file, dpi=300)
print(f"Summary saved to {statistics_file}")

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

performance_file = "performance_plot.png"
plt.savefig(performance_file, dpi=300)
print(f"Performance plot saved to {performance_file}")

plt.show()
