import sys
import os
import pandas as pd
from bertopic import BERTopic

def run_bertopic_process(input_path, output_path):
    # --- 1. Load Data ---
    if not os.path.exists(input_path):
        print(f"Error: Input file not found at {input_path}")
        sys.exit(1)

    print(f"Loading data from {input_path}...")
    df = pd.read_csv(input_path)

    # Validate required columns
    required_cols = ['UserName', 'Condition', 'text']
    if not all(col in df.columns for col in required_cols):
        print(f"Error: CSV must contain columns: {required_cols}")
        print(f"Found: {df.columns.tolist()}")
        sys.exit(1)

    # Ensure text is string and drop empty rows
    df['text'] = df['text'].astype(str)
    docs = df['text'].tolist()

    # --- 2. Run BERTopic ---
    print(f"Initializing BERTopic model for {len(docs)} documents...")
    
    # We use "multilingual" because your student names/IDs suggest a mixed setting, 
    # and some reflections might reference Chinese terms. 
    # If strictly English, you can change to language="english".
    topic_model = BERTopic(
        language="multilingual", 
        verbose=True,
        calculate_probabilities=False, # Set True only if you need soft-clustering
        min_topic_size=3 # Adjust this if you want larger/smaller topics
    )

    print("Fitting model and transforming data...")
    topics, probs = topic_model.fit_transform(docs)

    # --- 3. Format for ENA (One-Hot Encoding) ---
    print("Formatting data for 3D ENA...")
    
    # Assign topics back to DataFrame
    df['Topic_ID'] = topics

    # Create readable topic labels (e.g., "0_python_code_list")
    topic_info = topic_model.get_topic_info()
    
    # Create a map: Topic ID -> Custom Label
    # We create a label that combines the ID and the top 3 words
    # e.g., Topic 0 -> "T0_python_list_data"
    label_map = {}
    for index, row in topic_info.iterrows():
        t_id = row['Topic']
        name = row['Name'] # Default Name is usually "0_python_list_data"
        # Clean the name for R compatibility (remove spaces, special chars)
        clean_name = "Topic_" + name.replace(" ", "_").replace("-", "_").replace("__", "_")
        label_map[t_id] = clean_name

    df['Topic_Label'] = df['Topic_ID'].map(label_map)

    # Generate Binary Matrix (One-Hot Encoding)
    # ENA needs: Rows=Units, Cols=Codes. Values=1 if present, 0 if not.
    # We pivot the data.
    
    # Get dummies creates a column for every topic found
    topic_matrix = pd.get_dummies(df['Topic_Label'])
    
    # Concatenate with Metadata (UserName, Condition)
    # We intentionally exclude 'text' to keep the ENA file small and clean
    output_df = pd.concat([df[['UserName', 'Condition']], topic_matrix], axis=1)

    # Handle Outliers (Topic -1)
    # BERTopic assigns -1 to noise. You might want to drop this column for ENA 
    # so "Noise" doesn't become a node in your network.
    outlier_col = [col for col in output_df.columns if "minus_1" in col or "-1" in col]
    if outlier_col:
        print(f"Note: Dropping outlier column '{outlier_col[0]}' from ENA input.")
        output_df.drop(columns=outlier_col, inplace=True)

    # --- 4. Save Outputs ---
    print(f"Saving ENA matrix to {output_path}...")
    output_df.to_csv(output_path, index=False)

    # Save Topic Descriptions (So you know what the topics mean!)
    desc_path = output_path.replace("topic_matrix.csv", "topic_descriptions.csv")
    topic_info.to_csv(desc_path, index=False)
    print(f"Saved topic definitions to {desc_path}")

if __name__ == "__main__":
    # Handle arguments passed from main.py
    if len(sys.argv) < 3:
        # Fallback for manual testing
        print("Usage: python bertopic_runner.py <input_path> <output_path>")
        sys.exit(1)
    
    input_csv = sys.argv[1]
    output_csv = sys.argv[2]
    
    run_bertopic_process(input_csv, output_csv)