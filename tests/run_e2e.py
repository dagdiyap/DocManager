import requests
import time
import sys
import os

# --- Configuration ---
LICENSE_SERVER_URL = "http://localhost:8000/api/v1"
CA_DESKTOP_URL = "http://localhost:8443/api/v1"


def log(msg, color="white"):
    colors = {
        "green": "\033[92m",
        "red": "\033[91m",
        "yellow": "\033[93m",
        "white": "\033[0m",
    }
    print(f"{colors.get(color, '')}[E2E] {msg}\033[0m")


def wait_for_service(url, name, retries=10, delay=2):
    log(f"Waiting for {name} to be ready...", "yellow")
    for i in range(retries):
        try:
            resp = requests.get(url)
            if resp.status_code in [
                200,
                404,
            ]:  # 404 is fine for health check if root returns it
                log(f"{name} is UP!", "green")
                return True
        except requests.ConnectionError:
            pass
        time.sleep(delay)
    log(f"{name} failed to start.", "red")
    return False


def run_tests():
    # 1. Setup Data Paths
    log("1. Setting up Environment...", "yellow")
    os.makedirs("/tmp/ca_docs/9876543210", exist_ok=True)
    with open("/tmp/ca_docs/9876543210/FY2024_Return.pdf", "w") as f:
        f.write("Dummy Content")

    # 2. Register CA
    log("2. Registering CA...", "yellow")
    payload = {
        "id": "CA-TEST",
        "name": "Test Accountant",
        "email": "test@accountant.com",
    }
    resp = requests.post(f"{LICENSE_SERVER_URL}/ca/register", json=payload)
    if resp.status_code == 201 or (
        resp.status_code == 422 and "already exists" in resp.text
    ):
        log("CA Registered (or exists).", "green")
    else:
        log(f"CA Registration Failed: {resp.text}", "red")
        return False

    # 3. Issue License
    log("3. Issuing License...", "yellow")
    lic_payload = {"ca_id": "CA-TEST", "device_id": "TEST-DEVICE", "expiry_days": 30}
    resp = requests.post(f"{LICENSE_SERVER_URL}/license/issue", json=lic_payload)
    if resp.status_code != 200:
        log(f"License Issue Failed: {resp.text}", "red")
        return False
    token = resp.json()["license_token"]
    log("License Token Issued.", "green")

    # 4. Install License
    log("4. Installing License on CA Desktop...", "yellow")
    reg_resp = requests.post(
        f"{CA_DESKTOP_URL}/license/register", json={"license_token": token}
    )
    if reg_resp.status_code == 200:
        log("License Installed Successfully.", "green")
    else:
        log(f"License Install Failed: {reg_resp.text}", "red")
        return False

    # 5. Add Client
    log("5. Adding Client...", "yellow")
    client_payload = {
        "name": "Rajesh Client",
        "phone_number": "9876543210",
        "email": "rajesh@client.com",
        "password": "password123",
        "is_active": True,
    }
    # Using Session to handle potential redirects or cookies if needed
    s = requests.Session()
    client_resp = s.post(f"{CA_DESKTOP_URL}/clients/", json=client_payload)

    if client_resp.status_code in [200, 201]:
        log("Client Registered.", "green")
    elif client_resp.status_code == 422:  # Might already exist
        # Try to update or ignore
        log("Client might already exist, proceeding.", "yellow")
    else:
        log(f"Client Registration Failed: {client_resp.text}", "red")
        return False

    # 6. Trigger Scan
    log("6. Triggering Document Scan...", "yellow")
    scan_resp = requests.get(f"{CA_DESKTOP_URL}/documents/scan")
    if scan_resp.status_code == 200:
        log(f"Scan Complete. Found {len(scan_resp.json())} docs.", "green")
    else:
        log(f"Scan Failed: {scan_resp.text}", "red")
        return False

    # 7. Client Login
    log("7. Testing Client Login...", "yellow")
    login_payload = {"username": "9876543210", "password": "password123"}
    login_resp = requests.post(f"{CA_DESKTOP_URL}/auth/login", data=login_payload)
    if login_resp.status_code != 200:
        log(f"Login Failed: {login_resp.text}", "red")
        return False

    client_token = login_resp.json()["access_token"]
    log("Client Logged In.", "green")

    # 8. Client List Docs
    log("8. Verifying Client Document Access...", "yellow")
    headers = {"Authorization": f"Bearer {client_token}"}
    portal_resp = requests.get(
        f"{CA_DESKTOP_URL}/documents/", headers=headers
    )  # Using /documents/ for portal view if separated
    # Note: Router might be /portal/documents depending on implementation. Let's try both.

    if portal_resp.status_code == 404:
        portal_resp = requests.get(
            f"{CA_DESKTOP_URL}/portal/documents/", headers=headers
        )

    if portal_resp.status_code == 200:
        docs = portal_resp.json()
        log(f"Client sees {len(docs)} documents.", "green")
    else:
        log(f"Client Document Access Failed: {portal_resp.text}", "red")
        return False

    return True


if __name__ == "__main__":
    if not wait_for_service("http://localhost:8000/docs", "License Server"):
        sys.exit(1)
    if not wait_for_service("http://localhost:8443/docs", "CA Desktop"):
        sys.exit(1)

    success = run_tests()
    if success:
        log("\n✅ E2E VERIFICATION SUCCESSFUL", "green")
        sys.exit(0)
    else:
        log("\n❌ E2E VERIFICATION FAILED", "red")
        sys.exit(1)
