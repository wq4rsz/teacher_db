import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox)
import sqlite3

conn = sqlite3.connect('mydatabase.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS teachers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        subject TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        age INTEGER
    )
''')

try:
    cursor.execute("SELECT age FROM teachers LIMIT 1;")
except sqlite3.OperationalError:
    cursor.execute("ALTER TABLE teachers ADD COLUMN age INTEGER;")

conn.commit()
conn.close()

class TeacherApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Teachers Database')

        self.name_label = QLabel('Name:')
        self.name_edit = QLineEdit()
        self.age_label = QLabel('Age:')
        self.age_edit = QLineEdit()
        self.email_label = QLabel('Email:')
        self.email_edit = QLineEdit()
        self.subject_label = QLabel('Subject:')
        self.subject_edit = QLineEdit()

        self.add_button = QPushButton('Add Teacher')
        self.add_button.clicked.connect(self.add_teacher)

        self.delete_button = QPushButton('Delete Teacher')
        self.delete_button.clicked.connect(self.delete_teacher)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(['ID', 'Name', 'Age', 'Email', 'Subject'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.update_table()

        vbox = QVBoxLayout()
        vbox.addWidget(self.name_label)
        vbox.addWidget(self.name_edit)
        vbox.addWidget(self.age_label)
        vbox.addWidget(self.age_edit)
        vbox.addWidget(self.email_label)
        vbox.addWidget(self.email_edit)
        vbox.addWidget(self.subject_label)
        vbox.addWidget(self.subject_edit)
        vbox.addWidget(self.add_button)
        vbox.addWidget(self.delete_button)
        vbox.addWidget(self.table)
        self.setLayout(vbox)

    def add_teacher(self):
        name = self.name_edit.text().strip()
        subject = self.subject_edit.text().strip()
        email = self.email_edit.text().strip()
        age = self.age_edit.text().strip()

        if not name or not subject or not email or not age:
            QMessageBox.warning(self, 'Input Error', 'All fields are required!')
            return

        try:
            age = int(age)
        except ValueError:
            QMessageBox.warning(self, 'Input Error', 'Age must be a number!')
            return

        conn = sqlite3.connect('mydatabase.db')
        cursor = conn.cursor()

        try:
            cursor.execute("INSERT INTO teachers (name, subject, email, age) VALUES (?, ?, ?, ?)", (name, subject, email, age))
            conn.commit()
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, 'Database Error', 'Teacher with this email already exists!')
        finally:
            conn.close()

        self.name_edit.clear()
        self.age_edit.clear()
        self.email_edit.clear()
        self.subject_edit.clear()
        self.update_table()

    def delete_teacher(self):
        selected_row = self.table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, 'Selection Error', 'Please select a teacher to delete!')
            return

        teacher_id = self.table.item(selected_row, 0).text()

        conn = sqlite3.connect('mydatabase.db')

        cursor = conn.cursor()
        cursor.execute("DELETE FROM teachers WHERE id = ?", (teacher_id,))
        conn.commit()
        conn.close()

        self.update_table()

    def update_table(self):
        self.table.setRowCount(0)
        conn = sqlite3.connect('mydatabase.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM teachers")
        rows = cursor.fetchall()
        conn.close()

        for row in rows:
            row_count = self.table.rowCount()
            self.table.insertRow(row_count)
            self.table.setItem(row_count, 0, QTableWidgetItem(str(row[0])))  # ID
            self.table.setItem(row_count, 1, QTableWidgetItem(row[1]))       # Name
            self.table.setItem(row_count, 2, QTableWidgetItem(str(row[4])))  # Age
            self.table.setItem(row_count, 3, QTableWidgetItem(row[3]))       # Email
            self.table.setItem(row_count, 4, QTableWidgetItem(row[2]))       # Subject

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = TeacherApp()
    ex.show()
    sys.exit(app.exec_())
