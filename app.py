from flask import Flask, request, jsonify, render_template
from db_connection import get_db_connection
from exception import CustomException
from logger import logging
from datetime import date, datetime
from mysql.connector.errorcode import ER_DUP_ENTRY
import mysql.connector
today = date.today()
import sys
app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/add_task", methods=["GET", "POST"])
def create_task():
    try:
        if request.method == "POST":
            if request.is_json:
                data = request.get_json()
            else:
                data = request.form.to_dict()
            conn = get_db_connection()
            cursor = conn.cursor()
            title = data.get("title")
            status=data.get("status")
            valid_status= {"Pending", "Completed", "Overdue"}
            if status not in valid_status:
                logging.info("Invalid status type, Status can be only Pending, Completed, or Overdue and cannot be empty. Cannot create task with ID: %s",data["ID"])
                return jsonify({"error": "Invalid status type, Status can be only Pending, Completed, or Overdue and cannot be empty"}), 400
            if not title or not title.strip():
                logging.info("Title cannot be empty for task created with ID: %s",data["ID"])
                return jsonify({"error": "Title cannot be empty"}), 400
            if data.get("due_date"):
                try:
                    due_date = datetime.strptime(data["due_date"], "%Y-%m-%d").date()
                except ValueError:
                    logging.info("Invalid due_date format: %s", data.get("due_date"))
                    return jsonify({
                        "error": "Invalid due_date format. Use YYYY-MM-DD"
                    }), 400
            else:
                due_date = None
            if (due_date < today and (data.get("status") == "Pending")):
                logging.info("Cannot create task with due date less than current date for task created with ID: and status: %s",data["ID"])
                return jsonify({"error": "Cannot create task with due date less than current date for task with status: %s" % data.get("status")}), 400
            cursor.execute(
                "INSERT INTO tasks (id,title, description, due_date, status) VALUES (%s,%s, %s, %s, %s)",
                (
                   data["ID"],
                    data["title"],
                    data.get("description"),
                    data.get("due_date"),
                    data.get("status")
                )
            )
            conn.commit()
            cursor.close()
            conn.close()
            logging.info("Task created with ID: %s",data["ID"])
            return jsonify({"message": "Task created with id %s and status %s" % (data["ID"], data.get("status"))}), 201
    except mysql.connector.Error as e:
        if e.errno == ER_DUP_ENTRY:
            return jsonify({"error": "Duplicate ID, Task Id already present"}), 409
        return jsonify({"error": "Internal server error"}), 500
    except Exception as e:
        logging.error("Error creating task: %s", str(e))      
        raise CustomException(e,sys)
    return render_template("add_task.html")
    

@app.route("/tasks", methods=["GET"])
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
@app.route("/tasks/<int:id>", methods=["GET"])
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
@app.route("/tasks/completed", methods=["GET"])
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
@app.route("/tasks/pending", methods=["GET"])
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
@app.route("/tasks/overdue", methods=["GET"])
def get_overdue_tasks():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM tasks WHERE status='Overdue' or (due_date < CURDATE() and status != 'Completed') order by due_date ASC")
    tasks = cursor.fetchall()
    for task in tasks:
        if task["due_date"]:
            task["due_date"] = task["due_date"].strftime("%Y-%m-%d") 
    cursor.close()
    conn.close()
    logging.info("Fetched all overdue tasks")
    return jsonify(tasks)

@app.route("/tasks/<int:id>", methods=["PUT"])
def update_task(id):
    try:
        data = request.json
        conn = get_db_connection()
        cursor = conn.cursor()
        title = data.get("title")
        status=data.get("status")
        valid_status= {"Pending", "Completed", "Overdue"}
        if(id!=data.get("ID")):
            logging.info("Task ID in the URL and request body do not match for task with ID: %s",data["ID"])
            return jsonify({"error": "Task ID in the URL and request body do not match"}), 400
        if status not in valid_status:
            logging.info("Invalid status type, Status can be only Pending, Completed, or Overdue and cannot be empty. Cannot modify task with ID: %s",data["ID"])
            return jsonify({"error": "Invalid status type, Status can be only Pending, Completed, or Overdue and cannot be empty"}), 400
        if not title or not title.strip():
            logging.info("Title cannot be empty for task to be modified with ID: %s",data["ID"])
            return jsonify({"error": "Title cannot be empty for task to be modified with ID %s" % id}), 400
        if data.get("due_date"):
                try:
                    due_date = datetime.strptime(data["due_date"], "%Y-%m-%d").date()
                except ValueError:
                    logging.info("Invalid due_date format: %s", data.get("due_date"))
                    return jsonify({
                        "error": "Invalid due_date format. Use YYYY-MM-DD"
                    }), 400
        else:
            due_date = None
        if ((due_date < today) and (data.get("status") != "Completed")):
            data["status"] = "Overdue"
            logging.info("Status updated as overdue for task to be modified with ID: %s as new due date is less than current date",data["ID"])
            return jsonify({"message": "Task updated with id %s and status updated as %s" % (id, data.get("status"))}), 200
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
        logging.info("Task updated with ID: %s",data["ID"])
    except Exception as e:
        logging.error("Error updating task with ID: %s", id)
        raise CustomException(e,sys)
    return jsonify({"message": "Task updated with id %s and status updated as %s" % (id, data.get("status"))})


@app.route("/tasks/<int:id>", methods=["DELETE"])
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


if __name__ == "__main__":
    app.run(debug=True)
