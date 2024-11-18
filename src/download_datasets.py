import os
from datasets import load_dataset
import pandas as pd

DATASETS = ["vidore/arxivqa_test_subsampled"]

OUTPUT_DIR = "data/full"

def download_datasets():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    for i, dataset in enumerate(DATASETS):
        dataset = load_dataset(dataset)
        df = pd.DataFrame(dataset["test"])
        # Convert image to bytes
        df['image'] = df['image'].apply(lambda x: {'bytes': x.tobytes()})
        file_name = DATASETS[i].split("/")[1]
        output_path = os.path.join(OUTPUT_DIR, f"{file_name}.pkl")
        df.to_pickle(output_path)
        print(f"Saved dataset to {output_path}")

if __name__ == "__main__":
    download_datasets()
