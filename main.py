import requests
import csv
import json
import time
from tqdm import tqdm
from statistics import mean
import matplotlib.pyplot as plt

# Collect user input
print("🌐 CLI Web Request Tool")
target_url = input("Enter the target URL: ").strip()
try:
    num_requests = int(input("Enter the number of requests to send: "))
except ValueError:
    num_requests = 10

# Data store
results = []

# Send requests with progress bar
print("\n🚀 Sending requests...\n")
for i in tqdm(range(1, num_requests + 1), desc="Progress"):
    try:
        start = time.time()
        response = requests.get(target_url)
        duration = round(time.time() - start, 3)
        result = {
            "id": i,
            "status_code": response.status_code,
            "response_time": duration,
            "error": None
        }
    except Exception as e:
        result = {
            "id": i,
            "status_code": "ERROR",
            "response_time": None,
            "error": str(e)
        }

    results.append(result)

# Save logs
csv_file = "request_log.csv"
json_file = "request_log.json"

with open(csv_file, 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=results[0].keys())
    writer.writeheader()
    writer.writerows(results)

with open(json_file, 'w') as f:
    json.dump(results, f, indent=4)

print(f"\n📁 Logs saved as '{csv_file}' and '{json_file}'.")

# Summary
success_count = len([r for r in results if r["status_code"] != "ERROR"])
error_count = num_requests - success_count
avg_response_time = round(mean([r["response_time"] for r in results if r["response_time"] is not None]), 3)

print(f"""
✅ Done! {success_count} successful, {error_count} failed.
📊 Average response time: {avg_response_time}s
""")

# Plot response times (optional)
times = [r["response_time"] for r in results if r["response_time"] is not None]
plt.figure(figsize=(10, 5))
plt.plot(times, marker='o', linestyle='-', color='green')
plt.title("Response Time per Request")
plt.xlabel("Request #")
plt.ylabel("Response Time (s)")
plt.grid(True)
plt.tight_layout()
plt.savefig("response_time_chart.png")
plt.show()

print("📈 Response time chart saved as 'response_time_chart.png'")