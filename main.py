import requests
import time
import random
import csv
import json
from tqdm import tqdm
from statistics import mean
import matplotlib.pyplot as plt

# === Load proxies from file ===
def load_proxies(file_path="proxies.txt"):
    try:
        with open(file_path, 'r') as f:
            proxies = [line.strip() for line in f if line.strip()]
        print(f"🧾 Loaded {len(proxies)} proxies.")
        return proxies
    except Exception as e:
        print("❌ Failed to load proxies:", e)
        return []

# === Validate one proxy ===
def is_valid_proxy(proxy, test_url="http://httpbin.org/ip"):
    try:
        r = requests.get(test_url, proxies={
            "http": f"http://{proxy}",
            "https": f"http://{proxy}"
        }, timeout=5)
        return r.status_code == 200
    except:
        return False

# === Filter live proxies (limit to only needed number) ===
def get_live_proxies(proxies, max_needed):
    print("🔍 Validating proxies...")
    live = []
    for proxy in tqdm(proxies, desc="Checking"):
        if is_valid_proxy(proxy):
            live.append(proxy)
            if len(live) >= max_needed:
                break
    print(f"✅ {len(live)} live proxies found.")
    return live

# === Send requests ===
def send_requests(target_url, use_proxies, proxies, max_requests):
    results = []
    print(f"\n🚀 Sending {max_requests} requests {'with proxies' if use_proxies else 'without proxies'}...\n")
    for i in tqdm(range(1, max_requests + 1), desc="Requesting"):
        proxy = random.choice(proxies) if use_proxies and proxies else None
        proxy_dict = {
            "http": f"http://{proxy}",
            "https": f"http://{proxy}"
        } if proxy else None

        start = time.time()
        try:
            r = requests.get(target_url, proxies=proxy_dict, timeout=10)
            duration = round(time.time() - start, 3)
            result = {
                "id": i,
                "status_code": r.status_code,
                "response_time": duration,
                "proxy": proxy if proxy else "NONE",
                "error": None
            }
        except Exception as e:
            result = {
                "id": i,
                "status_code": "ERROR",
                "response_time": None,
                "proxy": proxy if proxy else "NONE",
                "error": str(e)
            }
        results.append(result)
        time.sleep(i * 0.5)  # ⏳ gradually increase delay
    return results

# === Save logs and chart ===
def save_logs(results):
    csv_file = "proxy_test_log.csv"
    json_file = "proxy_test_log.json"
    
    with open(csv_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)
    
    with open(json_file, 'w') as f:
        json.dump(results, f, indent=4)
    
    print(f"\n📁 Logs saved to '{csv_file}' and '{json_file}'")

    # Plot
    times = [r["response_time"] for r in results if r["response_time"] is not None]
    if times:
        plt.figure(figsize=(10, 5))
        plt.plot(times, marker='o', linestyle='-', color='blue')
        plt.title("Response Time per Request")
        plt.xlabel("Request #")
        plt.ylabel("Response Time (s)")
        plt.grid(True)
        plt.tight_layout()
        plt.savefig("proxy_response_chart.png")
        plt.show()
        print("📈 Chart saved as 'proxy_response_chart.png'")

# === Main ===
if __name__ == "__main__":
    print("🌐 Proxy Request Tester (Advanced Mode)")
    target_url = input("Enter the target URL: ").strip()

    try:
        max_requests = int(input("How many requests to send? "))
    except ValueError:
        max_requests = 10

    # Proxy usage option
    use_proxy_input = input("Use proxy? (1 = Yes, 2 = No) [Default: 1]: ").strip()
    use_proxies = use_proxy_input != '2'

    # Proxy validation option (if proxies used)
    validate_proxy_input = input("Validate proxies before sending? (1 = Yes, 2 = No) [Default: 2]: ").strip()
    validate_proxies = validate_proxy_input == '1' if use_proxies else False

    proxies = load_proxies() if use_proxies else []

    if use_proxies:
        if validate_proxies:
            proxies = get_live_proxies(proxies, max_requests)
            if not proxies:
                print("❌ No valid proxies found. Exiting.")
                exit()
        else:
            if len(proxies) < max_requests:
                print(f"⚠️ Warning: You provided {len(proxies)} proxies, but requested {max_requests} requests. Some proxies may be reused.")

    results = send_requests(target_url, use_proxies, proxies, max_requests)
    save_logs(results)
    print("✅ All tasks completed successfully!")
# End of main.py
# Note: Make sure to have the required libraries installed: