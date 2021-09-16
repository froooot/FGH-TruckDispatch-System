import sqlite3

sqliteConnection = sqlite3.connect("./finance.db", check_same_thread=False)
sqliteConnection.row_factory = sqlite3.Row
cur = sqliteConnection.cursor()

