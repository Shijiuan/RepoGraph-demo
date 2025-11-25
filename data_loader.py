def load_dataset(path):
    with open(path, "r") as f:
        data = [line.strip() for line in f]
    print(f"Loaded {len(data)} samples from {path}")
    return data
