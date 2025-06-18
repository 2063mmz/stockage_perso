import pandas as pd

def filter_csv(input_path, output_path, column_name, condition_func):

    df = pd.read_csv(input_path, delimiter="\t")

    filtered_df = df[df[column_name].apply(condition_func)]

    filtered_df.to_csv(output_path, index=False, sep="\t")

    print(f"filter done, results already save in:{output_path}")
    return filtered_df

result = filter_csv("csv_revision.csv", "csv_revision_positif.csv", "charge", lambda x: x == "+")
print(result)
