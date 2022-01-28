import pandas as pd
import os


# file_path = os.listdir('./industry/')
# file_path = [os.path.abspath('./industry/' + file) for file in file_path if file.endswith('.csv')]
file_path = ['./data/addon_industry.csv', './data/fi_industry.csv']


def merge_tables(merge_list):
    dfs = [pd.read_csv(file) for file in merge_list]
    output = pd.concat(dfs, join='outer', ignore_index=True)

    output.sort_values(
            by='公布日', axis=0, ascending=False,
            inplace=True, ignore_index=True
            )

    output.drop_duplicates(ignore_index=True, inplace=True)

    return output


if __name__ == "__main__":
    result = merge_tables(file_path)
    result.to_csv('./data/industry.csv', index=False)

    # print(file_path)

