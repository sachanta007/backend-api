CREATE TABLE IF NOT EXISTS users(
  user_id SERIAL PRIMARY KEY,
  first_name VARCHAR(50),
  last_name VARCHAR(50),
  email VARCHAR(355) UNIQUE NOT NULL,
  password VARCHAR(100),
  security_question VARCHAR(100),
  security_answer VARCHAR(100),
  status VARCHAR(100),
  created_on TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS role(
 role_id SERIAL PRIMARY KEY,
 role_name VARCHAR (255) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS user_role
(
  user_id INTEGER NOT NULL,
  role_id INTEGER NOT NULL,
  grant_date TIMESTAMP WITHOUT TIME ZONE,
  PRIMARY KEY (user_id, role_id),
  CONSTRAINT user_role_role_id_fkey FOREIGN KEY (role_id)
      REFERENCES role (role_id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION,
  CONSTRAINT user_role_user_id_fkey FOREIGN KEY (user_id)
      REFERENCES users (user_id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION
);

INSERT INTO role(role_name) VALUES('ADMIN');
INSERT INTO role(role_name) VALUES('PROFESSOR');
INSERT INTO role(role_name) VALUES('STUDENT');

CREATE TABLE IF NOT EXISTS courses(
  course_id SERIAL PRIMARY KEY,
  course_name VARCHAR(50),
  description VARCHAR(500),
  prof_id VARCHAR(50),
  location VARCHAR(100),
  start_time VARCHAR(50),
  end_time VARCHAR(50),
  days INTEGER,
  department VARCHAR(50)
);

ALTER TABLE users ADD COLUMN otp VARCHAR(20);

ALTER TABLE courses
ALTER COLUMN days TYPE INTEGER[] USING ARRAY[days]::INTEGER[]
ALTER TABLE courses ADD COLUMN course_code VARCHAR(40);
CREATE TABLE IF NOT EXISTS cart(
  cart_id SERIAL PRIMARY KEY,
  course_id INTEGER,
  user_id INTEGER
);
CREATE TABLE IF NOT EXISTS course_comments(
  comment_id SERIAL PRIMARY KEY,
  course_id INTEGER,
  user_id INTEGER,
  comment VARCHAR(100),
  course_ratings INTEGER
);

ALTER TABLE cart ADD COLUMN enrolled BOOLEAN DEFAULT FALSE;
