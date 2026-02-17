import requests
import time
import zipfile
import io
import os

API_URL = "http://localhost:8000/api/v1"
FILE_PATH = "app/circuits/current_mirror.py"

def test_full_pipeline():
    if not os.path.exists(FILE_PATH):
        print(f"File not found: {FILE_PATH}")
        return

    print(f"Uploading {FILE_PATH}...")
    with open(FILE_PATH, "rb") as f:
        # We can pass width and length as parameters
        response = requests.post(f"{API_URL}/run", files={"file": f}, data={"width": 2.0, "length": 0.5})
    
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
        print(f"Status: {status}, Progress: {status_data.get('progress')}%")

        if status in ["completed", "failed"]:
            break
        time.sleep(2)

    if status == "completed":
        print("\nSimulation successful!")
        results = status_data.get("results", {})
        
        print("\nGenerated Plots:")
        for plot in results.get("plots", []):
            print(f"  - {plot}")

        print("\nDownloading results zip...")
        download_resp = requests.get(f"{API_URL}/download/{process_id}")
        if download_resp.status_code == 200:
            with zipfile.ZipFile(io.BytesIO(download_resp.content)) as z:
                files = z.namelist()
                print("\nZip Contents:")
                for name in files:
                    print(f" - {name}")
                
                # Check for all three types of plots
                plot_types = ["dc", "ac", "tran"]
                for pt in plot_types:
                    has_plot = any(f"_{pt}.png" in name for name in files)
                    print(f"Checking for {pt} plot: {'FOUND' if has_plot else 'MISSING'}")
        else:
            print(f"Download failed: {download_resp.text}")
    else:
        print("\nPipeline failed.")
        print(f"Error logs: {status_data.get('error')}")

if __name__ == "__main__":
    test_full_pipeline()
