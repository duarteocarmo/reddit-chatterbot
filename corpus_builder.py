import sqlite3
import json
from datetime import datetime
import bz2
import pandas as pd
import os

# edit these
DATA_FOLDER = "reddit_data"
SQLITE_DATABASE = "reddit_data/RC_2014-10.db"
SUBREDDIT_NAME = "all"  # None if no subreddit filtering
LIMIT = 50000
SCORE_THRESHOLD = 1


# dont touch these
connection = sqlite3.connect(SQLITE_DATABASE)
c = connection.cursor()


if SUBREDDIT_NAME:
    query = f"SELECT * FROM parent_reply WHERE parent NOT NULL and score > {SCORE_THRESHOLD} and subreddit = '{SUBREDDIT_NAME}' LIMIT {LIMIT}"

else:
    query = f"SELECT * FROM parent_reply WHERE parent NOT NULL and score > {SCORE_THRESHOLD} LIMIT {LIMIT}"

df = pd.read_sql(query, connection)

print(f"Writing a total of {df.shape[0]} rows.")


def clean_string(sentence):
    # no emoji
    sentence = sentence.encode("ascii", "ignore").decode("ascii")
    # dont fuckup yml
    sentence = sentence.replace(":", " ")
    # tabs also create problems
    sentence = sentence.replace("\t", " ")
    if len(sentence) > 0:
        if sentence[0].isalpha() or sentence[0].isdigit():
            return str(sentence)

        else:
            for i in range(len(sentence)):
                if sentence[i].isalpha() or sentence[i].isdigit():
                    return str(sentence[i:])
    else:
        return "None"


def main():
    with open(
        f"{DATA_FOLDER}/{SUBREDDIT_NAME}.yml", "a", encoding="utf-8"
    ) as file:
        file.write("categories:\n")
        file.write(f"- {SUBREDDIT_NAME}\n")
        file.write("conversations:\n")

        for index, row in df.iterrows():
            question = clean_string(row["parent"])
            answer = clean_string(row["comment"])

            try:
                file.write(f"- - {question}\n")
                file.write(f"  - {answer}\n")
            except Exception as e:
                print(f"{str(e)}")


if __name__ == "__main__":
    main()
