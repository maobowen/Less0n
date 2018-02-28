/*
* Version:
* Author: Zhijian Jiang <zhijian.jiang at columbia.edu>
* Description: DDL of user database of LessOn
* Reference: https://www.getdonedone.com/building-the-optimal-user-database-model-for-your-application/
 */


CREATE SCHEMA IF NOT EXISTS lessOn_user;

----------------------------------------------------------------------
-- Create a table, users, to store the user's basic info
CREATE TABLE IF NOT EXISTS lessOn_user.users(
    user_id VARCHAR(10) PRIMARY KEY, -- Columbia Uni
    -- [What is a reasonable length limit on person “Name” fields?](https://stackoverflow.com/questions/30485/what-is-a-reasonable-length-limit-on-person-name-fields)
    first_name VARCHAR(40) NOT NULL ,
    last_name VARCHAR(40) NOT NULL,
    email VARCHAR(40) NOT NULL UNIQUE CHECK (email LIKE '%_@__%.__%')
);

----------------------------------------------------------------------
-- Create a procedure to extract uni from email
CREATE OR REPLACE FUNCTION generate_user_id()
  RETURNS trigger AS
$BODY$
/*
    % CREATE TRIGGER before_insert_on_users BEFORE INSERT ON lessOn_user.users
  FOR EACH ROW EXECUTE PROCEDURE generate_user_id();

Extract uni from new user's email and set the uni be new user's user_id.
*/
BEGIN
    NEW.user_id = substring(NEW.email from 1 for (position('@' in NEW.email) - 1));
    RETURN NEW;
END;
$BODY$;

----------------------------------------------------------------------
-- Create a trigger of users to generate user_id from email
CREATE TRIGGER before_insert_on_users BEFORE INSERT ON lessOn_user.users
  FOR EACH ROW EXECUTE PROCEDURE generate_user_id();

----------------------------------------------------------------------
-- Create a table, role, store the role info
CREATE TABLE IF NOT EXISTS lessOn_user.roles(
    role_id SERIAL PRIMARY KEY ,
    name varchar(40) NOT NULL UNIQUE
);

----------------------------------------------------------------------
-- Create a table, memberships, store the user's relevant role and other info
CREATE TABLE IF NOT EXISTS lessOn_user.memberships(
    membership_id SERIAL PRIMARY KEY ,
    user_id INT NOT NULL ,
    role_id INT NOT NULL ,
    FOREIGN KEY (user_id) REFERENCES lessOn_user.users(user_id),
    FOREIGN KEY (role_id) REFERENCES lessOn_user.roles(role_id)
);