import pandas as pd

df = pd.read_json("annotator_annotation.json")
print(df.head())
