import requests
import time
import csv
import json
from tqdm import tqdm

# === Send Single Request ===
def send_request(i, target_url, method="GET", headers=None, body=None):
    start = time.time()
    try:
        if headers is None:
            headers = {"User-Agent": "LoadTester/1.0"}
        
        if method == "POST":
            r = requests.post(target_url, json=body, headers=headers, timeout=10)
        else:
            r = requests.get(target_url, headers=headers, timeout=10)
        
        duration = round(time.time() - start, 3)
        return {
            "id": i,
            "method": method,
            "status_code": r.status_code,
            "response_time": duration,
            "error": None
        }
    except Exception as e:
        return {
            "id": i,
            "method": method,
            "status_code": "ERROR",
            "response_time": None,
            "error": str(e)
        }

# === Save Logs ===
def save_logs(results):
    csv_file = "request_log.csv"
    with open(csv_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)
    
    print(f"\n📁 Logs saved to '{csv_file}'")

# === Main ===
if __name__ == "__main__":
    print("🌐 Simple Load Tester")

    # Get target URL
    default_url = "http://localhost:5000"
    target_url = input(f"Enter the target URL [Default: {default_url}]: ").strip() or default_url

    # Get number of requests
    try:
        max_requests = int(input("How many requests to send? [Default: 10]: ").strip() or 10)
    except ValueError:
        max_requests = 10

    # Choose request method
    print("\nChoose request method:")
    print("1 - GET (default)")
    print("2 - POST")
    method_choice = input("Enter choice (1 or 2): ").strip() or "1"
    method = "GET" if method_choice == "1" else "POST"

    headers = {"User-Agent": "LoadTester/1.0"}
    body = None

    # Handle POST request options
    if method == "POST":
        print("\nPOST Request Options:")
        print("1 - Simple (default)")
        print("2 - Advanced")
        post_choice = input("Enter choice (1 or 2): ").strip() or "1"
        
        if post_choice == "2":
            # Custom headers
            print("\nEnter custom header (key:value) or leave blank to continue:")
            header_input = input("Header (e.g., Content-Type: application/json): ")
            if header_input and ':' in header_input:
                key, value = header_input.split(':', 1)
                headers[key.strip()] = value.strip()
            
            # Custom body
            print("\nEnter POST body as JSON (e.g., {\"name\": \"John\", \"age\": 30})")
            print("Guidelines:")
            print("- Use double quotes for strings")
            print("- Example: {\"key\": \"value\", \"number\": 42}")
            print("- Leave blank for default body")
            body_input = input("POST body: ").strip()
            if body_input:
                try:
                    body = json.loads(body_input)
                except json.JSONDecodeError:
                    print("❌ Invalid JSON! Using default body.")
                    body = {"test_id": f"test_{time.time()}", "value": "sample"}
            else:
                body = {"test_id": f"test_{time.time()}", "value": "sample"}
        else:
            body = {"test_id": f"test_{time.time()}", "value": "sample"}

    print(f"\n🚀 Sending {max_requests} {method} request(s) to {target_url}...")

    results = []
    for i in tqdm(range(1, max_requests + 1), desc="Processing"):
        result = send_request(i, target_url, method, headers, body)
        results.append(result)

    save_logs(results)
    print("✅ Done.")