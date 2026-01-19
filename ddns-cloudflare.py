import requests
import os
from datetime import datetime

# -----------------------------
# CONFIGURATION
# -----------------------------

API_TOKEN  = os.getenv("CF_API_TOKEN")
ZONE_NAME  = os.getenv("CF_ZONE_NAME")

# Split comma-separated hostnames into a list
hosts_raw = os.getenv("CF_HOSTS", "")
HOSTSUPDATE = [h.strip() for h in hosts_raw.split(",") if h.strip()]

GOTIFY_URL     = os.getenv("GOTIFY_URL")
GOTIFY_TOKEN   = os.getenv("GOTIFY_TOKEN")
GOTIFY_IF_UNCH = os.getenv("GOTIFY_IF_UNCH", "False").lower() == "true"


BASE_URL = "https://api.cloudflare.com/client/v4"

if not API_TOKEN or API_TOKEN.strip() == "":
    msg = "Cloudflare API token missing — cannot continue."
    print(msg)
    send_gotify(msg, title="Cloudflare DDNS ERROR")
    exit(1)


def get_public_ip():
    try:
        ip = requests.get("https://api.ipify.org").text.strip()
        return ip
    except Exception as e:
        raise Exception(f"Failed to get public IP: {e}")

def get_zone_id():
    url      = f"{BASE_URL}/zones?name={ZONE_NAME}"
    headers  = {"Authorization": f"Bearer {API_TOKEN}"}

    try:
        response = requests.get(url, headers=headers, timeout=5)
        data = response.json()
    except Exception as e:
        msg = f"Cloudflare API unreachable in get_zone_id: {e}"
        print(msg)
        send_gotify(msg, title="Cloudflare DDNS ERROR")
        exit(1)

    # Handle invalid token or permission errors
    if not data.get("success", False):
        msg = f"Cloudflare rejected token in get_zone_id: {data.get('errors')}"
        print(msg)
        send_gotify(msg, title="Cloudflare DDNS ERROR")
        exit(1)

    if len(data["result"]) == 0:
        msg = f"Zone '{ZONE_NAME}' not found — check token permissions."
        print(msg)
        send_gotify(msg, title="Cloudflare DDNS ERROR")
        exit(1)

    return data["result"][0]["id"]


def list_a_records(zone_id):
    url     = f"{BASE_URL}/zones/{zone_id}/dns_records?type=A"
    headers = {"Authorization": f"Bearer {API_TOKEN}"}

    try:
        response = requests.get(url, headers=headers, timeout=5)
        data = response.json()
    except Exception as e:
        msg = f"Cloudflare API error while listing A records: {e}"
        print(msg)
        send_gotify(msg, title="Cloudflare DDNS ERROR")
        exit(1)

    if not data.get("success", False):
        msg = f"Cloudflare API rejected request in list_a_records: {data}"
        print(msg)
        send_gotify(msg, title="Cloudflare DDNS ERROR")
        exit(1)

    print(f"\nA-records for {ZONE_NAME}:\n")

    print(f"{'NAME':35} {'CONTENT':20} {'ID'}")
    print("-" * 80)

    for record in data["result"]:
        name    = record['name']
        content = record['content']
        rec_id  = record['id']
        print(f"{name:35} {content:20} {rec_id}")

    print(' ')




# -----------------------------
# GET SPECIFIC DNS RECORD
# -----------------------------
def get_dns_record(zone_id, hostname):
    url = f"{BASE_URL}/zones/{zone_id}/dns_records?type=A&name={hostname}"
    headers = {"Authorization": f"Bearer {API_TOKEN}"}

    response = requests.get(url, headers=headers)
    data = response.json()

    if not data["success"] or len(data["result"]) == 0:
        #print(f"Hostname not found in DNS: {hostname}")
        return None

    return data["result"][0]


# -----------------------------
# UPDATE DNS RECORD
# -----------------------------
def update_a_record(zone_id, record_id, hostname, new_ip):
    url = f"{BASE_URL}/zones/{zone_id}/dns_records/{record_id}"
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "type":    "A",
        "name":    hostname,
        "content": new_ip,
        "ttl":     300,
        "proxied": False
    }

    response = requests.put(url, headers=headers, json=payload)
    data = response.json()

    if not data["success"]:
        raise Exception(f"Failed to update DNS record: {data}")

    print(f"✔ Updated {hostname} → {new_ip}")

def send_gotify(message, title="DDNS Update"):
    try:
        url = f"{GOTIFY_URL}/message?token={GOTIFY_TOKEN}"
        payload = {
            "title": title,
            "message": message,
            "priority": 5
        }
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        print(f"Gotify notification failed: {e}")


if __name__ == "__main__":

    print('')
    print('******* COMMENCING CHECK & UPDATE ********')
    print(datetime.now().strftime("%d-%b-%Y %H:%M"))
    print('')

    public_ip = get_public_ip()
    print(f"\nCurrent Public IP: {public_ip}\n")

    # --- Catch Cloudflare token/zone errors ---
    try:
        zone_id = get_zone_id()
    except Exception as e:
        error_msg = f"Cloudflare API failure: {e}"
        print(error_msg)
        send_gotify(error_msg, title="Cloudflare DDNS ERROR")
        exit(1)

    list_a_records(zone_id)

    # Loop through all hostnames
    for hostname in HOSTSUPDATE:
        print(' ')
        print(f"\nChecking {hostname}...")

        record = get_dns_record(zone_id, hostname)

        if record is None:
            print("NO DNS RECORD - SKIP")
            continue

        current_dns_ip = record["content"]
        record_id      = record["id"]

        print(f"Current DNS IP: {current_dns_ip}")

        if current_dns_ip != public_ip:
            print("IP mismatch — updating...")
            update_a_record(zone_id, record_id, hostname, public_ip)
            send_gotify(
                message=f"{hostname} updated to {public_ip}",
                title="Cloudflare DDNS Updated"
            )

        else:
            print("MATCHES - No update.")
            if GOTIFY_IF_UNCH:
                send_gotify(
                    message=f"{hostname} unchanged at {current_dns_ip}",
                    title="Cloudflare DDNS Unchanged"
                )
    print(' ')
    print('waiting.....')
