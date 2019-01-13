drop table if exists entries;
create table users (
  id integer(11) primary key autoincrement,
  name VARCHAR(100),
  email VARCHAR(100),
  username VARCHAR(30),
  password VARCHAR(100),
  register_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
