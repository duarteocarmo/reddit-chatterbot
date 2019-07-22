import sqlite3
import json
from datetime import datetime
import bz2
import pandas as pd
import os




connection = sqlite3.connect("reddit_data/RC_2014-10.db")
subreddit = "all"


c = connection.cursor()


#df = pd.read_sql(
#    f"SELECT * FROM parent_reply WHERE parent NOT NULL and score > 0 and subreddit = '{subreddit}'",
#    connection
#)

df = pd.read_sql(
    f"SELECT * FROM parent_reply WHERE parent NOT NULL and score > 0 LIMIT 50000",
    connection
)

print(f"Writing a total of {df.shape[0]} rows.")

def clean_string(sentence):
    sentence = sentence.encode('ascii', 'ignore').decode('ascii')
    sentence = sentence.replace(":", " ")
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

try:
    os.remove(f"reddit_data/{subreddit}.yml")
except Exception as e:
    print(f"Did not remove: {str(e)}.")



with open(f"reddit_data/{subreddit}.yml", "a", encoding="utf-8") as file:
    file.write("categories:\n")
    file.write(f"- {subreddit}\n")
    file.write("conversations:\n")

    for index, row in df.iterrows():
        question = clean_string(row["parent"])
        answer = clean_string(row["comment"])



        try:
            file.write(f"- - {question}\n")
            file.write(f"  - {answer}\n")
        except Exception as e:
            print(f"{str(e)}")


# for index, row in df.iterrows():
#    print(f"Q:{row['parent']}\nA:{row['comment']}\n")



