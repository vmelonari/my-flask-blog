import sqlite3

# with sqlite3.connect("database.db") as connection:
#     c = connection.cursor()
#     #c.execute("""DROP TABLE users""")
#     c.execute("""CREATE TABLE users (
#       id integer(11) primary key,
#       name VARCHAR(100),
#       email VARCHAR(100),
#       username VARCHAR(30),
#       password VARCHAR(100),
#       register_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#     )""")
#     c.execute('INSERT INTO users VALUES(1, "Vlad", "vlad@vlad.de", "vladdy", "xxxx", "10.03.2018")')
#     c.execute('INSERT INTO users VALUES(2, "Miha", "mihai@asdadsde", "micky", "xxxx", "10.03.2018")')

#ONLY TO CREATE A NEW DATABASE. JUST RUN THE SCRIPT

#crate a new table
with sqlite3.connect("database.db") as connection:
    c = connection.cursor()
    c.execute("""CREATE TABLE articles(
        id integer(11) PRIMARY KEY,
        title VARCHAR(225),
        author VARCHAR(100),
        body TEXT,
        create_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")
