DROP TABLE IF EXISTS users;
CREATE TABLE users (
  id serial PRIMARY KEY,
  name varchar,
  username varchar,
  password varchar

);

DROP TABLE IF EXISTS chirp;
CREATE TABLE chirp (
  id serial PRIMARY KEY,
  user_id integer REFERENCES users (id),
  chirp_date timestamp,
  chirp_content varchar (141)
);

DROP TABLE IF EXISTS follow;
CREATE TABLE follow (
  follower_id integer REFERENCES users (id),
  following_id integer REFERENCES users (id)
);
