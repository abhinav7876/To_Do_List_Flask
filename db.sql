CREATE DATABASE todo_db;
USE todo_db;

CREATE TABLE tasks (
    id INT PRIMARY KEY,
    title VARCHAR(250) NOT NULL,
    description VARCHAR(250),
    due_date DATE,
    status VARCHAR(50) NOT NULL DEFAULT 'Pending',
);
