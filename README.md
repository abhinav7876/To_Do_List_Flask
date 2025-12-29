A **Flask-based To-Do** application that manages:
- Adding new tasks in TO-DO list
- Viewing (All/ Completed/ Pending/ Overdue) tasks from TO-DO list
- Modifying existing tasks in TO-DO list
- Deleting existing tasks from TO-DO list

**Tech Stack**:
- Backend: Flask (Python)
- Database: MySQL
- Testing: pytest

**Steps for Project Setup**-

Step 1-Clone git repository:

git clone https://github.com/abhinav7876/To_Do_List_Flask.git

Step 2- Create virtual environment:

conda create -p venv python==3.11 -y

Step 3- Activate virtual environment:

conda activate venv/

Step 4- Install requirements in virtual environment:

pip install -r requirements.txt

Step 5- Database Setup

Run the following sql queries in MySQL app:

- CREATE DATABASE todo_db;

- USE todo_db;

- CREATE TABLE tasks (
        id INT PRIMARY KEY,
        title VARCHAR(250) NOT NULL,
        description VARCHAR(250),
        due_date DATE,
        status VARCHAR(50) NOT NULL DEFAULT 'Pending'
    );

Step 6- Rename dummy_env to .env file

Step 7- Update DB password in .env file

Step 8-Launch the app:

python app.py

Step 9- Open up localhost

http://127.0.0.1:5000/


**Testing**

Total **22 test cases** for different API endpoints are integrated for testing in this TO-Do Application

STEPS- Run the following command:

- pytest -v


------------------------------------------------------------------------------------------------------------------

For Postman: 
- Request Body (JSON)

{

    "description": "in evening",

    "due_date": "2025-12-25",

    "ID": 1,

    "status": "Completed",

    "title": "My task"

}

---------------------------------------------------------------------------------------------------------------------------

Detailed API Documentation:

Detailed API documentation is available here:  

/docs/API_Documentation.md