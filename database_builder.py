# stolen from sentdex https://pythonprogramming.net/ - just with a couple of modifications
# basically transforms a .bz2 comment dump from : https://files.pushshift.io/reddit/comments/
# into a sqlite database of pairs of answers and replies
# let it run, and hit ctrl-c when satisfied with size.
import sqlite3
import json
from datetime import datetime
import bz2

# tweak these
DUMP_NAME = "RC_2014-10"  # the name of your bz2 dump
DATA_DIRECTORY = "reddit_data"  # the directory where the dump is stored
MIN_COMMENT_LENGTH = 1
MAX_COMMENT_LENGTH = 50
MIN_UPVOTES = 2


# don't touch these
dump_path = f"{DATA_DIRECTORY}/{DUMP_NAME}.bz2"
connection = sqlite3.connect(f"reddit_data/{DUMP_NAME}.db")
sql_transaction = []
c = connection.cursor()


def create_table():
    c.execute(
        "CREATE TABLE IF NOT EXISTS parent_reply(parent_id TEXT PRIMARY KEY, comment_id TEXT UNIQUE, parent TEXT, comment TEXT, subreddit TEXT, unix INT, score INT)"
    )


def format_data(data):
    data = (
        data.replace("\n", " newlinechar ")
        .replace("\r", " newlinechar ")
        .replace('"', "'")
    )
    return data


def transaction_bldr(sql):
    global sql_transaction
    sql_transaction.append(sql)
    if len(sql_transaction) > 1000:
        c.execute("BEGIN TRANSACTION")
        for s in sql_transaction:
            try:
                c.execute(s)
            except:
                pass
        connection.commit()
        sql_transaction = []


def sql_insert_replace_comment(
    commentid, parentid, parent, comment, subreddit, time, score
):
    try:
        sql = """UPDATE parent_reply SET parent_id = ?, comment_id = ?, parent = ?, comment = ?, subreddit = ?, unix = ?, score = ? WHERE parent_id =?;""".format(
            parentid,
            commentid,
            parent,
            comment,
            subreddit,
            int(time),
            score,
            parentid,
        )
        transaction_bldr(sql)
    except Exception as e:
        print("s0 insertion", str(e))


def sql_insert_has_parent(
    commentid, parentid, parent, comment, subreddit, time, score
):
    try:
        sql = """INSERT INTO parent_reply (parent_id, comment_id, parent, comment, subreddit, unix, score) VALUES ("{}","{}","{}","{}","{}",{},{});""".format(
            parentid, commentid, parent, comment, subreddit, int(time), score
        )
        transaction_bldr(sql)
    except Exception as e:
        print("s0 insertion", str(e))


def sql_insert_no_parent(commentid, parentid, comment, subreddit, time, score):
    try:
        sql = """INSERT INTO parent_reply (parent_id, comment_id, comment, subreddit, unix, score) VALUES ("{}","{}","{}","{}",{},{});""".format(
            parentid, commentid, comment, subreddit, int(time), score
        )
        transaction_bldr(sql)
    except Exception as e:
        print("s0 insertion", str(e))


def acceptable(data):
    if (
        len(data.split(" ")) > MAX_COMMENT_LENGTH
        or len(data) < MIN_COMMENT_LENGTH
    ):
        return False
    elif len(data) > 1000:
        return False
    elif data == "[deleted]":
        return False
    elif data == "[removed]":
        return False
    else:
        return True


def find_parent(pid):
    try:
        sql = "SELECT comment FROM parent_reply WHERE comment_id = '{}' LIMIT 1".format(
            pid
        )
        c.execute(sql)
        result = c.fetchone()
        if result != None:
            return result[0]
        else:
            return False
    except Exception as e:
        # print(str(e))
        return False


def find_existing_score(pid):
    try:
        sql = "SELECT score FROM parent_reply WHERE parent_id = '{}' LIMIT 1".format(
            pid
        )
        c.execute(sql)
        result = c.fetchone()
        if result != None:
            return result[0]
        else:
            return False
    except Exception as e:
        # print(str(e))
        return False


def main():
    create_table()
    row_counter = 0
    paired_rows = 0
    with bz2.open(filename=dump_path, mode="rt") as f:
        for row in f:
            row_counter += 1
            row = json.loads(row)
            parent_id = row["parent_id"]
            body = format_data(row["body"])
            created_utc = row["created_utc"]
            score = row["score"]
            comment_id = row["name"]
            subreddit = row["subreddit"]
            parent_data = find_parent(parent_id)
            if score >= MIN_UPVOTES:
                existing_comment_score = find_existing_score(parent_id)
                if existing_comment_score:
                    if score > existing_comment_score:
                        if acceptable(body):
                            sql_insert_replace_comment(
                                comment_id,
                                parent_id,
                                parent_data,
                                body,
                                subreddit,
                                created_utc,
                                score,
                            )

                else:
                    if acceptable(body):
                        if parent_data:
                            sql_insert_has_parent(
                                comment_id,
                                parent_id,
                                parent_data,
                                body,
                                subreddit,
                                created_utc,
                                score,
                            )
                            paired_rows += 1
                        else:
                            sql_insert_no_parent(
                                comment_id,
                                parent_id,
                                body,
                                subreddit,
                                created_utc,
                                score,
                            )

            if row_counter % 100000 == 0:
                print(
                    "Total Rows Read: {}, Paired Rows: {}, Time: {}".format(
                        row_counter, paired_rows, str(datetime.now())
                    )
                )
                print("Cleanin up!")
                sql = "DELETE FROM parent_reply WHERE parent IS NULL"
                c.execute(sql)
                connection.commit()
                c.execute("VACUUM")
                connection.commit()


if __name__ == "__main__":
    main()
