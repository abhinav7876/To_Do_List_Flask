from flask import Flask, request, jsonify, render_template, redirect, url_for
from db_connection import get_db_connection
from exception import CustomException
from logger import logging
from datetime import date, datetime

today = date.today()
import sys
app = Flask(__name__)


@app.route("/api/tasks", methods=["POST"])
def create_task():
    try:
        data = request.json
        conn = get_db_connection()
        cursor = conn.cursor()
        title = data.get("title")
        status=data.get("status")
        valid_status= {"Pending", "Completed", "Overdue"}
        if status not in valid_status:
            logging.info("Invalid status type, Status can be only Pending, Completed, or Overdue and cannot be empty. Cannot create task with ID: %s", data["id"])
            return jsonify({"error": "Invalid status type, Status can be only Pending, Completed, or Overdue and cannot be empty"}), 400
        if not title or not title.strip():
            logging.info("Title cannot be empty for task created with ID: %s", data["id"])
            return jsonify({"error": "Title cannot be empty"}), 400
        if data.get("due_date"):
            due_date = datetime.strptime(data["due_date"], "%Y-%m-%d").date()
        if (due_date < today and (data.get("status") == "pending")):
            logging.info("Cannot create task with due date less than current date for task created with ID: and status: %s", data["id"])
            return jsonify({"error": "Cannot create task with due date less than current date for task created with ID: %s and status: %s" % (data["id"], data.get("status"))}), 400
        cursor.execute(
            "INSERT INTO tasks (id,title, description, due_date, status) VALUES (%s,%s, %s, %s, %s)",
            (
                data["id"],
                data["title"],
                data.get("description"),
                data.get("due_date"),
                data.get("status")
            )
        )
        conn.commit()
        cursor.close()
        conn.close()
        logging.info("Task created with ID: %s", data["id"])
    except Exception as e:
        logging.error("Error creating task: %s", str(e))
        raise CustomException(e,sys)
    return jsonify({"message": "Task created with id %s and status %s" % (data["id"], data.get("status"))}), 201


@app.route("/api/tasks", methods=["GET"])
def get_tasks():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""SELECT *,
                                CASE
                                WHEN due_date < CURDATE() AND status != 'Completed'
                                THEN 'Overdue'
                                ELSE status
                                END AS status
                                FROM tasks;""")
        tasks = cursor.fetchall()
        for task in tasks:
            if task["due_date"]:
                task["due_date"] = task["due_date"].strftime("%Y-%m-%d") 
        cursor.close()
        conn.close()
        logging.info("Fetched all tasks")
    except Exception as e:
        logging.error("Error in fetching tasks",)
        raise CustomException(e,sys)
    return jsonify(tasks)
@app.route("/api/tasks/<int:id>", methods=["GET"])
def get_task(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM tasks WHERE id=%s", (id,))
        tasks = cursor.fetchall()
        if not tasks:
            logging.info("No task found with ID: %s", id)
            return jsonify({"error": "Task not found with ID: %s" % id}), 404
        for task in tasks:
            if task["due_date"]:
                task["due_date"] = task["due_date"].strftime("%Y-%m-%d") 
        cursor.close()
        conn.close()
        logging.info("Fetched task with ID: %s", id)
    except Exception as e:
        logging.error("Error in fetching task with ID: %s", id)
        raise CustomException(e,sys)
    return jsonify(tasks)
@app.route("/api/tasks/completed", methods=["GET"])
def get_completed_tasks():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM tasks WHERE status='Completed' order by due_date desc")
    tasks = cursor.fetchall()
    for task in tasks:
        if task["due_date"]:
            task["due_date"] = task["due_date"].strftime("%Y-%m-%d") 
    cursor.close()
    conn.close()
    logging.info("Fetched all completed tasks")
    return jsonify(tasks)
@app.route("/api/tasks/pending", methods=["GET"])
def get_pending_tasks():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM tasks WHERE status in ('Pending', 'Overdue') order by due_date ASC")
    tasks = cursor.fetchall()
    for task in tasks:
        if task["due_date"]:
            task["due_date"] = task["due_date"].strftime("%Y-%m-%d") 
    cursor.close()
    conn.close()
    logging.info("Fetched all pending tasks")
    return jsonify(tasks)
@app.route("/api/tasks/overdue", methods=["GET"])
def get_overdue_tasks():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM tasks WHERE status='Overdue' or due_date < CURDATE() order by due_date ASC")
    tasks = cursor.fetchall()
    for task in tasks:
        if task["due_date"]:
            task["due_date"] = task["due_date"].strftime("%Y-%m-%d") 
    cursor.close()
    conn.close()
    logging.info("Fetched all overdue tasks")
    return jsonify(tasks)

@app.route("/api/tasks/<int:id>", methods=["PUT"])
def update_task(id):
    try:
        data = request.json
        conn = get_db_connection()
        cursor = conn.cursor()
        title = data.get("title")
        status=data.get("status")
        valid_status= {"Pending", "Completed", "Overdue"}
        if(id!=data.get("id")):
            logging.info("Task ID in the URL and request body do not match for task with ID: %s", data["id"])
            return jsonify({"error": "Task ID in the URL and request body do not match"}), 400
        if status not in valid_status:
            logging.info("Invalid status type, Status can be only Pending, Completed, or Overdue and cannot be empty. Cannot modify task with ID: %s", data["id"])
            return jsonify({"error": "Invalid status type, Status can be only Pending, Completed, or Overdue and cannot be empty"}), 400
        if not title or not title.strip():
            logging.info("Title cannot be empty for task to be modified with ID: %s", data["id"])
            return jsonify({"error": "Title cannot be empty for task to be modified with ID %s" % id}), 400
        if data.get("due_date"):
            due_date = datetime.strptime(data["due_date"], "%Y-%m-%d").date()
        if ((due_date < today) and (data.get("status") != "Completed")):
            data["status"] = "Overdue"
        cursor.execute(
            "UPDATE tasks SET title=%s, description=%s, due_date=%s, status=%s WHERE id=%s",
            (
                data["title"],
                data["description"],
                data["due_date"],
                data["status"],
                id
            )
        )
        if cursor.rowcount == 0:
            return jsonify({"error": "Task with id %s not found in database" % id}), 404
        conn.commit()
        cursor.close()
        conn.close()
        logging.info("Task updated with ID: %s", data["id"])
    except Exception as e:
        logging.error("Error updating task with ID: %s", id)
        raise CustomException(e,sys)
    return jsonify({"message": "Task updated with id %s and status updated as %s" % (id, data.get("status"))})


@app.route("/api/tasks/<int:id>", methods=["DELETE"])
def delete_task(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE id=%s", (id,))
        if cursor.rowcount == 0:
            return jsonify({"error": "Task with id %s not found in database" % id}), 404
        conn.commit()
        cursor.close()
        conn.close()
        logging.info("Task deleted with ID: %s", id)
    except Exception as e:
        logging.error("Error deleting task with ID: %s", id)
        raise CustomException(e,sys)
    return jsonify({"message": "Task deleted with id %s" % id})



@app.route("/")
def index():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM tasks")
        tasks = cursor.fetchall()

        cursor.close()
        conn.close()
        logging.info("Fetched all tasks for web interface")
    except Exception as e:
        logging.error("Error fetching tasks: %s", e)
    return render_template("index.html", tasks=tasks)


@app.route("/add", methods=["GET", "POST"])
def add_task():
    try:

        if request.method == "POST":
            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute(
                "INSERT INTO tasks (ID, title, description, due_date,status) VALUES (%s, %s, %s, %s, %s)",
                (
                    request.form["ID"],
                    request.form["title"],
                    request.form["description"],
                    request.form["due_date"],
                    request.form["status"]
                )
            )
            conn.commit()
            cursor.close()
            conn.close()
            logging.info("Task added with ID: %s", request.form["ID"])
            return redirect(url_for("index"))
    except Exception as e:
        logging.error("Error adding task via web interface: %s", e)      
        raise CustomException(e,sys)                                                                                                   
    return render_template("add_task.html")


if __name__ == "__main__":
    app.run(debug=True)
