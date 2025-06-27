import requests
import time
import csv
import json
import random
from tqdm import tqdm
from statistics import mean
import matplotlib.pyplot as plt
from collections import Counter
from concurrent.futures import ThreadPoolExecutor

# === Get Geolocation ===
def get_geo_info():
    try:
        r = requests.get("https://ipapi.co/json/", timeout=5)
        if r.status_code == 200:
            return r.json()
    except:
        return {}
    return {"country": "Unknown", "city": "Unknown"}

GEO = get_geo_info()  # One-time lookup

# === Generate Default JSON Body ===
def generate_default_body():
    return {
        "test_id": f"test_{random.randint(1, 1000)}",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "value": random.choice(["data", "load_test", "sample"])
    }

# === Send Single Request ===
def send_request(i, target_url, method="GET", headers=None, body=None, proxy=None):
    start = time.time()
    try:
        if headers is None:
            headers = {"User-Agent": "LoadTester/1.0"}

        proxies = {"http": proxy, "https": proxy} if proxy else None
        if method == "POST":
            r = requests.post(target_url, json=body or generate_default_body(), headers=headers, proxies=proxies, timeout=10)
        elif method == "PUT":
            r = requests.put(target_url, json=body or generate_default_body(), headers=headers, proxies=proxies, timeout=10)
        else:
            r = requests.get(target_url, headers=headers, proxies=proxies, timeout=10)
        
        duration = round(time.time() - start, 3)
        return {
            "id": i,
            "method": method,
            "status_code": r.status_code,
            "response_time": duration,
            "country": GEO.get("country", "Unknown"),
            "city": GEO.get("city", "Unknown"),
            "error": None
        }
    except Exception as e:
        return {
            "id": i,
            "method": method,
            "status_code": "ERROR",
            "response_time": None,
            "country": GEO.get("country", "Unknown"),
            "city": GEO.get("city", "Unknown"),
            "error": str(e)
        }

# === Save Logs and Plot ===
def save_logs(results):
    csv_file = "request_log.csv"
    json_file = "request_log.json"
    
    with open(csv_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)
    
    with open(json_file, 'w') as f:
        json.dump(results, f, indent=4)
    
    print(f"\n📁 Logs saved to '{csv_file}' and '{json_file}'")

    # Plot response times
    times = [r["response_time"] for r in results if r["response_time"] is not None]
    if times:
        plt.figure(figsize=(10, 5))
        plt.plot(times, marker='o', linestyle='-', color='green')
        plt.title("Response Time per Request")
        plt.xlabel("Request #")
        plt.ylabel("Response Time (s)")
        plt.grid(True)
        plt.tight_layout()
        plt.savefig("response_chart.png")
        plt.show()
        print("📈 Chart saved as 'response_chart.png'")

    # Method and Country Summary
    methods = [r["method"] for r in results]
    countries = [r["country"] for r in results if r["country"] != "Unknown"]
    
    print("\n📊 Request Method Summary:")
    for method, count in Counter(methods).items():
        print(f"   {method}: {count} request(s)")
    
    if countries:
        print("\n🌍 Country-wise Request Summary:")
        for country, count in Counter(countries).items():
            print(f"   {country}: {count} request(s)")

# === Main ===
if __name__ == "__main__":
    print("🌐 Advanced Load Tester (Random Methods & Proxy Support)")

    # Default values
    default_url = "http://localhost:3000"  # Default target URL
    default_max_requests = 10
    default_concurrency = 5
    default_headers = {"User-Agent": "LoadTester/1.0"}
    default_proxy = None

    # Get target URL
    target_url = input(f"Enter the target URL [Default: {default_url}]: ").strip() or default_url

    # Get number of requests
    try:
        max_requests = int(input(f"How many requests to send? [Default: {default_max_requests}]: ").strip() or default_max_requests)
    except ValueError:
        max_requests = default_max_requests

    # Choose request method mode
    method_mode = input("Use random request methods (GET/POST/PUT) or fixed? (random/fixed) [Default: random]: ").strip().lower()
    if method_mode not in ["random", "fixed"]:
        method_mode = "random"

    fixed_method = "GET"
    if method_mode == "fixed":
        fixed_method = input("Request method? (GET/POST/PUT) [Default: GET]: ").strip().upper()
        if fixed_method not in ["GET", "POST", "PUT"]:
            fixed_method = "GET"

    # Custom headers
    use_headers = input("Add custom headers? (y/n) [Default: n]: ").strip().lower() == 'y'
    headers = default_headers.copy()
    if use_headers:
        print("Enter headers as key:value (blank line to stop):")
        while True:
            h = input("> ")
            if not h.strip():
                break
            if ':' in h:
                k, v = h.split(':', 1)
                headers[k.strip()] = v.strip()

    # JSON body for POST/PUT
    body = None
    if method_mode == "fixed" and fixed_method in ["POST", "PUT"]:
        use_body = input(f"Send JSON body with {fixed_method}? (y/n) [Default: n]: ").strip().lower() == 'y'
        if use_body:
            try:
                body_input = input("Enter JSON data (e.g. {\"name\": \"Farhan\"}): ")
                body = json.loads(body_input)
            except json.JSONDecodeError:
                print(f"❌ Invalid JSON! Using default body for {fixed_method}.")
                body = generate_default_body()
        else:
            body = generate_default_body()
    elif method_mode == "random":
        print("ℹ️ Random mode: Default JSON body will be used for POST/PUT requests.")

    # Proxy support
    proxy = None
    use_proxy = input("Use proxy? (y/n) [Default: n]: ").strip().lower() == 'y'
    if use_proxy:
        proxy = input("Enter proxy (e.g., http://proxy:port): ").strip()
        if not proxy:
            print("❌ No proxy provided. Proceeding without proxy.")
            proxy = None

    # Concurrency level
    try:
        concurrency = int(input(f"Concurrency level? (e.g. 5 means 5 threads) [Default: {default_concurrency}]: ").strip() or default_concurrency)
    except ValueError:
        concurrency = default_concurrency

    print(f"\n🚀 Sending {max_requests} request(s) to {target_url} using {concurrency} thread(s)...")
    if method_mode == "random":
        print("   Method: Random (GET/POST/PUT)")
    else:
        print(f"   Method: {fixed_method}")
    if proxy:
        print(f"   Proxy: {proxy}")

    results = []
    methods = ["GET", "POST", "PUT"]
    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = []
        for i in range(max_requests):
            method = random.choice(methods) if method_mode == "random" else fixed_method
            futures.append(executor.submit(send_request, i+1, target_url, method, headers, body, proxy))
        for f in tqdm(futures, desc="Processing"):
            results.append(f.result())

    save_logs(results)
    print("✅ Done.")