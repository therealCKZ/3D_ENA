import subprocess
import os
import sys

def run_pipeline():
    # --- Configuration ---
    # Define your paths clearly so they are easy to change later
    RAW_DATA_PATH = os.path.join("data", "raw", "topicena_input_filtered.csv")
    PROCESSED_DATA_PATH = os.path.join("data", "processed", "topic_matrix.csv")
    
    # Define script locations
    PYTHON_SCRIPT = os.path.join("topicena", "bertopic_runner.py")
    R_SCRIPT = os.path.join("scripts", "3DENA_script.R")

    # --- Step 0: Pre-flight Checks ---
    print("Starting TopicENA Pipeline...")
    
    # Check if input data exists
    if not os.path.exists(RAW_DATA_PATH):
        print(f"Error: Input file not found at {RAW_DATA_PATH}")
        print("   Please place 'topicena_input_filtered.csv' in 'data/raw/'")
        sys.exit(1)

    # Create output directories if they don't exist
    os.makedirs(os.path.dirname(PROCESSED_DATA_PATH), exist_ok=True)
    os.makedirs("outputs", exist_ok=True)

    # --- Step 1: Run BERTopic (Python) ---
    print("\n[Step 1/2] Running BERTopic Analysis...")
    try:
        # We pass the input and output paths as arguments to the Python script
        # Note: You need to ensure bertopic_runner.py accepts sys.argv or hardcode paths there too
        # For now, we assume bertopic_runner.py is set up to read from RAW_DATA_PATH
        # and save to PROCESSED_DATA_PATH
        
        # If your bertopic_runner is a module, run it as a script:
        result = subprocess.run(
            [sys.executable, PYTHON_SCRIPT, RAW_DATA_PATH, PROCESSED_DATA_PATH],
            capture_output=True, text=True, check=True
        )
        print("BERTopic completed successfully.")
        # Optional: Print script output for debugging
        # print(result.stdout) 

    except subprocess.CalledProcessError as e:
        print(f"BERTopic failed with error:\n{e.stderr}")
        sys.exit(1)

    # --- Step 2: Run 3D ENA (R) ---
    print("\n[Step 2/2] Generating 3D ENA Visualization...")
    try:
        # Check if Rscript is available
        r_check = subprocess.run(["Rscript", "--version"], capture_output=True, text=True)
        if r_check.returncode != 0:
             print("Warning: Rscript not found. Is R installed and in your PATH?")
        
        # Execute R script
        result_r = subprocess.run(
            ["Rscript", R_SCRIPT, PROCESSED_DATA_PATH],
            capture_output=True, text=True, check=True
        )
        print("3D ENA Graph generated.")
        print(result_r.stdout) # Often R scripts print useful info

    except subprocess.CalledProcessError as e:
        print(f"R Script failed with error:\n{e.stderr}")
        sys.exit(1)

    print("\n Pipeline Finished! Check the 'outputs/' folder for your HTML file.")

if __name__ == "__main__":
    run_pipeline()