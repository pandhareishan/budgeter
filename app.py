from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from pathlib import Path

app = Flask(__name__)
DB_PATH = Path("budget.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    with open("schema.sql", "r", encoding="utf-8") as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        date = request.form["date"]
        category = request.form["category"]
        description = request.form.get("description", "")
        amount = float(request.form["amount"])

        conn = get_db()
        conn.execute(
            "INSERT INTO expenses (date, category, description, amount) VALUES (?, ?, ?, ?)",
            (date, category, description, amount),
        )
        conn.commit()
        conn.close()
        return redirect(url_for("index"))

    conn = get_db()
    expenses = conn.execute(
        "SELECT * FROM expenses ORDER BY date DESC, id DESC"
    ).fetchall()

    monthly = conn.execute("""
        SELECT substr(date, 1, 7) AS month, ROUND(SUM(amount), 2) AS total
        FROM expenses
        GROUP BY month
        ORDER BY month DESC
    """).fetchall()

    conn.close()
    return render_template("index.html", expenses=expenses, monthly=monthly)

@app.route("/edit/<int:expense_id>", methods=["GET", "POST"])
def edit(expense_id):
    conn = get_db()
    expense = conn.execute("SELECT * FROM expenses WHERE id = ?", (expense_id,)).fetchone()

    if request.method == "POST":
        date = request.form["date"]
        category = request.form["category"]
        description = request.form.get("description", "")
        amount = float(request.form["amount"])

        conn.execute(
            "UPDATE expenses SET date=?, category=?, description=?, amount=? WHERE id=?",
            (date, category, description, amount, expense_id),
        )
        conn.commit()
        conn.close()
        return redirect(url_for("index"))

    conn.close()
    return render_template("edit.html", expense=expense)

@app.route("/delete/<int:expense_id>", methods=["POST"])
def delete(expense_id):
    conn = get_db()
    conn.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))

if __name__ == "__main__":
    if not DB_PATH.exists():
        init_db()
    app.run(debug=True)