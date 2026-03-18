filename = "top100_cities_attractions.csv"
expected_fields = 6  # change this if your CSV should have more

with open(filename, "r", encoding="utf-8") as f:
    for i, line in enumerate(f, start=1):
        # Split by comma
        fields = line.strip().split(",")
        if len(fields) != expected_fields:
            print(f"Line {i} has {len(fields)} fields: {line.strip()}")