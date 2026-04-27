import requests
import time
import zipfile
import io
import os

API_URL = "http://localhost:8000/api/v1"
FILE_PATH = "app/circuits/two_stage_opamp.py"

def test_pipeline():
    if not os.path.exists(FILE_PATH):
        print(f"File not found: {FILE_PATH}")
        return

    print(f"Uploading {FILE_PATH}...")
    with open(FILE_PATH, "rb") as f:
        response = requests.post(f"{API_URL}/run", files={"file": f})
    
    if response.status_code != 200:
        print(f"Upload failed: {response.text}")
        return

    data = response.json()
    process_id = data["process_id"]
    print(f"Started process: {process_id}")

    # Poll status
    while True:
        status_resp = requests.get(f"{API_URL}/status/{process_id}")
        if status_resp.status_code != 200:
            print(f"Status check failed: {status_resp.text}")
            break
        
        status_data = status_resp.json()
        status = status_data["status"]
        print(f"Status: {status}, Progress: {status_data.get('progress')}")

        if status in ["completed", "failed"]:
            break
        time.sleep(2)

    if status == "completed":
        print("Downloading results...")
        download_resp = requests.get(f"{API_URL}/download/{process_id}")
        if download_resp.status_code == 200:
            with zipfile.ZipFile(io.BytesIO(download_resp.content)) as z:
                print("\nZip Contents:")
                for name in z.namelist():
                    print(f" - {name}")
                
                # Check formatted content of DC netlist
                dc_file = next((n for n in z.namelist() if "_dc.spice" in n), None)
                if dc_file:
                    content = z.read(dc_file).decode("utf-8")
                    print("\n--- DC Netlist Content ---")
                    print(content)
                    print("--------------------------")
                    
                    if "Two-Stage Op-Amp" in content:
                        print("SUCCESS: Found expected circuit name.")
                    else:
                        print("FAILURE: Did not find expected circuit name.")
        else:
            print(f"Download failed: {download_resp.text}")
    else:
        print("Pipeline failed to complete.")

if __name__ == "__main__":
    test_pipeline()
