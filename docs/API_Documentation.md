**Base URL**:

http://localhost:5000

**Fields description**:

| Field        | Type      | Description                                   |
|-------------|-----------|-----------------------------------------------|
| ID          | Integer   | Unique                                        |
| title       | String    | Title of the task                             |
| description | String    | Task details                                  |
| due_date    | Date      | Task due date (YYYY-MM-DD)                    |
| status      | String    | Task status (`Pending`, `Completed`,`Overdue`)          |



**API Endpoints Description**:

| Method | Endpoint            | Description |
|------|--------------------|------------|
| GET | `/` | Loads home page |
| GET | `/tasks` | Fetch all tasks |
| GET | `/tasks/{id}` | Fetch task with id |
| GET | `/tasks/completed` | Fetch all completed tasks |
| GET | `/tasks/pending` | Fetch all pending tasks (includes overdue tasks) |
| GET | `/tasks/overdue` | Fetch all overdue tasks |
| POST | `/add_task` | Create new task (with proper validations) |
| PUT | `/tasks/{id}` | Update existing task |
| DELETE | `/tasks/{id}` | Delete existing task |

----------------------------------------------------------------------------------------------------------------------------
**Data validations added in all above API endpoints**.

- Task ID must be unique
- Title is mandatory
- Due date must be in YYYY-MM-DD format
- Status must be one of: Pending, Completed, Overdue
- Invalid or missing fields returns proper error messages
- Due date cannot be in the past if status is Pending
- When updating a task, if the due date is in the past and status is not Completed, status is automatically updated to Overdue
- Task ID in URL and request body must match during update
- Fetching, updating, or deleting a task that does not exist in db returns 404 Not Found error
- Handles duplicate entry in task creation
- Logged all important events, validation failures, and errors
- All necessary data validations while creating, updating and deleting tasks are handled with proper error codes

-----------------------------------------------------------------------------------------------------------------------------------

**Status Codes used**

| Status Code | Meaning            | Description                                      |
|------------|--------------------|--------------------------------------------------|
| 200        | OK                 | Request processed successfully                  |
| 201        | Created            | Resource created successfully                   |
| 400        | Bad Request        | Invalid request payload or missing fields       |
| 404        | Not Found          | Requested resource does not exist               |
| 409        | Conflict           | Duplicate resource or conflicting request    |
| 500        | Internal Server Error | Server-side error occurred                  |

-------------------------------------------------------------------------------------------------------------------------------

**Create new task**

Method: POST  
API ENDPOINT: http://127.0.0.1:5000/add_task

- Request Body (JSON)-

{

    "description": "in evening",

    "due_date": "2025-12-25",

    "ID": 1,

    "status": "Completed",

    "title": "My task"

}

- Response from API-

{

    "message": "Task created with id 1 and status Completed"

}

Error code:201 [CREATED]
Automatically record will get store in 'tasks' table in MySQL db

![alt text](image-4.png)

![alt text](image-5.png)

----------------------------------------
**View task with id**:

Method: GET  
API ENDPOINT: http://127.0.0.1:5000/tasks/{id}

- Response from API-

[
    {

    "description": "in evening",

    "due_date": "2025-12-25",

    "ID": 1,

    "status": "Completed",

    "title": "My task"

}
]

Error code:200 [OK]

![alt text](image-3.png)

----------------------------------------------------------------------------------------------------------------------------------

**View all available tasks**:

Method: GET  
API ENDPOINT: http://127.0.0.1:5000/tasks

- Response from API-

[
    {

    "description": "in evening",

    "due_date": "2025-12-25",

    "ID": 1,

    "status": "Completed",

    "title": "My task"

},
{

        "description": "in eve",

        "due_date": "2025-12-29",

        "id": 2,

        "status": "Pending",

        "title": "html "

}
]

Error code:200 [OK]

------------------------------------------------------------------------------------------------------

**View all pending tasks**:

Method: GET  
API ENDPOINT: http://127.0.0.1:5000/tasks/pending

- Response from API-

[
{

        "description": "in eve",

        "due_date": "2025-12-29",

        "id": 2,

        "status": "Pending",

        "title": "html "

}
]

Error code:200 [OK]

------------------------------------------------------------------------------------------------------

**View all available tasks**:

Method: GET  
API ENDPOINT: http://127.0.0.1:5000/tasks/completed

- Response from API-

[
    {

    "description": "in evening",

    "due_date": "2025-12-25",

    "ID": 1,

    "status": "Completed",

    "title": "My task"

}
]

Error code:200 [OK]

------------------------------------------------------------------------------------------------------

**View all overdue tasks**:

Method: GET  
API ENDPOINT: http://127.0.0.1:5000/tasks/overdue

- Response from API-

[
    {

        "description": "in eve",
        
        "due_date": "2025-12-25",
        
        "id": 7,
        
        "status": "Overdue",
        
        "title": "java "
    }
]

Error code:200 [OK]

------------------------------------------------------------------------------------------------------

**Creating duplicate task id**

Method: POST  
API ENDPOINT: http://127.0.0.1:5000/add_task

- Request Body-

{

    "description": "in evening",

    "due_date": "2025-12-25",

    "ID": 1,

    "status": "Completed",

    "title": "My task"

}

- Response from API containing error message-

{

    "error": "Duplicate ID, Task Id already present"

}

Error code:409 [CONFLICT]

--------------------------------------------------------------------------------------------------------------------

**Update existing task**

Method: PUT  
API ENDPOINT: http://127.0.0.1:5000/tasks/{id}

- Request Body (JSON)-

{

    "description": "in evening",

    "due_date": "2025-12-29",

    "ID": 1,

    "status": "Completed",

    "title": "My task"

}

- Response from API-

{

   "message": "Task updated with id 1 and status updated as Completed"

}

Error code:200 [OK]

-----------------------------------------------------------------------------------------------------------------

**Delete existing task**

Method: DELETE  
API ENDPOINT: http://127.0.0.1:5000/tasks/{id}

- Response from API-

{

   "message": "Task deleted with id 1"

}

Error code:200 [OK]

-----------------------------------------------------------------------------------------------------------------


