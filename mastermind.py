from argparse import ArgumentParser
import pandas as pd
import logging
import math
import itertools
from hashlib import sha256

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S', level=logging.DEBUG)

def find_combined_encodings(df):
    """
    for an encoding dataframe df, return a list of all valid encodings
    that result from combining two columns into one column
    """
    comboencodings = []
    for columns in itertools.combinations(df.columns, r=2):
        column1, column2 = sorted(columns)
        colvals = df[column1] + df[column2]
        # only support positive or negative
        colvals = [1 if x else 0 for x in colvals]
        todrop = set([column1, column2] + column1.split("+") + column2.split("+"))
        todrop = todrop.intersection(df.columns)
        combodf = df.drop(todrop, axis=1)
        combodf["+".join([column1, column2])] = colvals
        if is_valid_encoding(combodf):
            comboencodings.append(combodf)
    return remove_duplicate_encodings(comboencodings)

def find_all_combined_encodings(xs):
    """
    for a list of encodings, return all valid combined encodings
    """
    comboencodings = []
    for df in xs:
        comboencodings += find_combined_encodings(df)
    return remove_duplicate_encodings(comboencodings)

def find_valid_subencodings(df):
    """
    for an encoding dataframe df, return a list of all valid encodings
    that result from removing a column from the dataframe
    """
    subencodings = []
    for column in df.columns:
        subencoding = df.drop([column], axis=1)
        if is_valid_encoding(subencoding):
            subencodings.append(subencoding)
    return subencodings

def find_all_subencodings(xs):
    """
    for a list of encodings, return all valid subencodings
    """
    subencodings = []
    for df in xs:
        subencodings += find_valid_subencodings(df)
    return remove_duplicate_encodings(subencodings)

def is_valid_encoding(df):
    """
    check if a dataframe has rows that are all unique
    """
    # drop_duplicates removes duplicate rows
    deduped = df.drop_duplicates()
    return len(deduped) == len(df)

def get_df_hash(df):
    return sha256(pd.util.hash_pandas_object(df, index=True).values).hexdigest()

def remove_duplicate_encodings(xs):
    """
    using a dataframe hash as a key, remove duplicate dataframes
    """
    xs = [df[sorted(df.columns)] for df in xs]
    hashdict = {get_df_hash(df): df for df in xs}
    return hashdict.values()

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("markerfile", help="CSV of markers")
    args = parser.parse_args()

    encodings = {}
    logging.info(f"Reading {args.markerfile}.")
    data = pd.read_csv(args.markerfile, index_col="type")
    logging.info(f"Reducing list of markers.")
    minbits = math.ceil(math.log2(len(data)))
    logging.info(f"Minimum genes to encode all celltypes is {minbits}.")
    encodings = [data]
    optimized = [data]
    round = 0
    while True:
        round += 1
        logging.info(f"Round: {round}")
        encodings = list(find_all_subencodings(optimized))
        if len(encodings) == 0:
            logging.info(f"Found {len(optimized)} valid subencodings.")
            break
        optimized = encodings
        logging.info(f"Found {len(optimized)} valid subencodings.")
        logging.info(f"Lengths: {[len(x.columns) for x in optimized]}")
    while True:
        round += 1
        logging.info(f"Round: {round}.")
        encodings = list(find_all_combined_encodings(optimized))
        if len(encodings) == 0:
            logging.info(f"Found {len(optimized)} valid subencodings.")
            logging.info(f"Lengths: {[len(x.columns) for x in optimized]}")
            break
        optimized = encodings
        logging.info(f"Found {len(optimized)} valid subencodings.")
        logging.info(f"Lengths: {[len(x.columns) for x in optimized]}")

    while True:
        round += 1
        logging.info(f"Round: {round}.")
        encodings = list(find_all_subencodings(optimized))
        if len(encodings) == 0:
            logging.info(f"Found {len(optimized)} valid subencodings.")
            break
        optimized = encodings
        logging.info(f"Found {len(optimized)} valid subencodings.")
        logging.info(f"Lengths: {[len(x.columns) for x in optimized]}")

    for index, df in enumerate(optimized):
        outfile = f"subencoding{index}.csv"
        logging.info(f"Writing {outfile}.")
        df.to_csv(outfile, index=True)
