from PyQt5.QtWidgets import (
    QScrollArea , QGridLayout , QApplication, QMainWindow, QLineEdit, QPushButton, QLabel, QVBoxLayout, QWidget, QMessageBox
)
import sys
import json
import os
import csv
import datetime
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

class MainWindow(QMainWindow):
    def __init__(self, username, users):
        super().__init__()
        self.users = users
        self.username = username  # Save username if needed
        self.setWindowTitle("Quiz Application")
        self.setGeometry(100, 100, 400, 300)

        # Title and Creator Labels
        self.LabelTitle = QLabel("Welcome to the Quiz Application", self)
        self.LabelTitle.setAlignment(Qt.AlignCenter)
        
        self.LabelCreator = QLabel(
            "Created by: BOUDJELIDA Yanis,\n"
            "BRAHIM DJELLOUL ANTRI Hichem,\n"
            "MOULOUDJ Mojhamed,\n"
            "FIALA Zackaria",
            self
        )
        self.LabelCreator.setAlignment(Qt.AlignCenter)

        # Start Quiz Button
        self.StartQuizButton = QPushButton("Start Quiz", self)
        self.StartQuizButton.clicked.connect(self.start_quiz)

        # Layout setup
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.LabelTitle)
        self.layout.addWidget(self.LabelCreator)
        self.layout.addWidget(self.StartQuizButton)

        # Main Widget
        main_widget = QWidget(self)
        main_widget.setLayout(self.layout)
        self.setCentralWidget(main_widget)

    def start_quiz(self):
        """Start the quiz by displaying the category label."""
        # Assuming CategorieLabel is defined elsewhere and takes these parameters
        self.category_label = CategorieLabel(self, self.username, self.users)
        self.layout.addWidget(self.category_label)
        self.LabelTitle.hide()
        self.LabelCreator.hide()
        self.StartQuizButton.hide()

class AuthWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Authentication Page")
        self.setGeometry(100, 100, 400, 300)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.headerLabel = QLabel("Login")
        self.headerLabel.setAlignment(Qt.AlignCenter)

        self.nameLabel = QLabel("Username:")
        self.nameInput = QLineEdit()
        self.nameInput.setPlaceholderText("Enter your username")

        self.layout.addWidget(self.headerLabel)
        self.layout.addWidget(self.nameLabel)
        self.layout.addWidget(self.nameInput)

        self.loginButton = QPushButton("Login")
        self.loginButton.clicked.connect(self.handle_login)  # Connect to a method
        self.layout.addWidget(self.loginButton)

    def handle_login(self):
        """Handles login logic."""
        username = self.nameInput.text().strip()
        if username:  # Check if the username is not empty
            backend = AuthBackEnd(username, self)  # Create an instance of AuthBackEnd
            QMessageBox.information(self, "Success", f"Welcome, {username}!")
            self.close()  # Close the authentication window
            self.show_categories_window(username,backend.getUser())  # Show categories after login
        else:
            QMessageBox.warning(self, "Error", "Username cannot be empty!")

    def show_categories_window(self, username,users):
        """Show the categories window after login."""
        self.main_window = MainWindow(username,users)
        self.main_window.show()


class CategorieLabel(QWidget):
    def __init__(self, parent,username,users):
        super().__init__(parent)
        self.categories = self.load_categories()[0]
        self.questions_by_category = self.load_categories()[1]
        self.username = username
        self.users = users
        print(self.questions_by_category)
        self.layoutCategories = QGridLayout(self)

        # Create a scroll area to hold the category labels
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.create_categories_widget())

        self.layoutCategories.addWidget(scroll_area)

    def create_categories_widget(self):
        """Create a widget to hold category labels."""
        category_widget = QWidget(self)
        category_layout = QVBoxLayout(category_widget)

        # Add a label for each category
        for category in self.categories:
            button = QPushButton(category, self)
            button.clicked.connect(self.handle_category_click)
            category_layout.addWidget(button)

        return category_widget

    def handle_category_click(self):
        """Handle category button click."""
        button = self.sender()
        # print("Category selected:", button.text(), "\n", self.categories[1])
        questions = self.questions_by_category[button.text()]
        print(questions)
        self.quiz_window = QuizLabel(questions,self.username,self.users)
        self.quiz_window.show()

    def load_categories(self):
        """Load categories from the JSON2 file."""
        with open("questions2.json", 'r') as f:
            questions_by_category = json.load(f)

        # Convert the dictionary of categories into a list
        categories = [category for category in questions_by_category.keys()]
        return categories,questions_by_category


class QuizLabel(QWidget):
    def __init__(self, questions, username,users, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.questions = questions
        self.username = username
        self.users = users
        self.score = 0

        self.idx = 0  # Keeps track of the current question
        self.question_label = QLabel("", self)
        self.question_label.setAlignment(Qt.AlignCenter)
        self.group = QGroupBox("Options", self)
        radio_layout = QVBoxLayout()
        self.group.setLayout(radio_layout)

        self.layout.addWidget(self.question_label)
        self.layout.addWidget(self.group)

        self.submit_button = QPushButton("Submit", self)
        self.submit_button.clicked.connect(self.handle_submit)
        self.layout.addWidget(self.submit_button)

        self.labelCorrect = QLabel("", self)
        self.layout.addWidget(self.labelCorrect)

        self.display_question(self.idx)  # Display the first question

    def display_question(self, idx):
        """Displays the current question and its options."""
        question = self.questions[idx]
        self.question_label.setText(question["question"])

        # Clear previous options
        for i in reversed(range(self.group.layout().count())):
            widget = self.group.layout().itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()

        # Display new options for the current question
        for option in question['options']:
            radio_button = QRadioButton(option, self)
            self.group.layout().addWidget(radio_button)

    def handle_submit(self):
        """Handles the submit button click."""
        selected_answer = None
        for radio_button in self.group.findChildren(QRadioButton):
            if radio_button.isChecked():
                selected_answer = radio_button.text()
                break

        if selected_answer:
            correct_answer = self.questions[self.idx]['correct_answer']
            self.check_answer(selected_answer, correct_answer)
            self.idx += 1  # Move to the next question
            if self.idx < len(self.questions):
                QTimer.singleShot(1000, lambda: self.display_question(self.idx))  # Show next question after delay
            else:
                QTimer.singleShot(1000, lambda: self.show_finish_dialog())
        else:
            QMessageBox.warning(self, "Error", "Please select an answer.")

    def check_answer(self, answer, correct_answer):
        """Check if the answer is correct."""
        if answer != correct_answer:
            QMessageBox.warning(self, "Error", f"The correct answer was: {correct_answer}")
        else:
            self.score += 1
    def show_finish_dialog(self):
        """Show dialog when quiz finishes."""
        message_box = QMessageBox(self)
        message_box.setIcon(QMessageBox.Question)
        message_box.setWindowTitle("Quiz Finished!")
        message_box.setText("Do you want to save your history to a CSV file?")
        message_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        response = message_box.exec_()

        if response == QMessageBox.Yes:
            self.save_result()
            self.export_results_to_csv()
            self.close()
        else: 
            self.save_result()
            self.close()

    def export_results_to_csv(self):
        """Export a user's results to a CSV file."""
        file_name = f"{self.username}_results.csv"
        with open(file_name, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Date", "Score", "Category", "Quit"])
            for entry in self.users[self.username]['history']:
                writer.writerow([entry['date'], entry['score'], entry['category'], entry['quit']])
        QMessageBox.information(self, "History Saved", f"Your results have been saved to {file_name}.")

    def save_result(self):
        """Save the result of a quiz for a user."""
        questions_count = len(self.questions)
        category = "General Knowledge"  # Example, adjust based on your question's category

        current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.users[self.username]['history'].append({
            'date': current_date,
            'category': category,
            'score': f"{self.score}/{questions_count}",
            'quit': False
        })
        save_users(self.users)  # Assuming you have a function to save user data

def save_users(users):
    """Save user data to a JSON file."""
    with open("users.json", 'w') as f:
        json.dump(users, f, indent=4)
    print("Users' data saved.")

class AuthBackEnd:
    def __init__(self, username, authWindow):
        self.userName = username
        self.authWindow = authWindow
        self.file = 'users.json'
        self.users = self.load_users()
        self.initialize_user()

    def getUser(self):
        return self.users
    
    def load_users(self):
        """Load user data from a JSON file."""
        if not os.path.exists(self.file):
            with open(self.file, 'w') as f:
                json.dump({}, f)
        with open(self.file, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}

    def save_users(self, users):
        """Save user data to a JSON file."""
        with open(self.file, 'w') as f:
            json.dump(users, f, indent=4)

    def initialize_user(self):
        """Check if the user exists, and initialize if not."""
        if self.userName in self.users:
            print(f"\nWelcome back, {self.userName}!")
        else:
            print(f"\nWelcome, {self.userName}! Your profile has been created.")
            self.users[self.userName] = {'history': []}
            self.save_users(self.users)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    auth_window = AuthWindow()
    auth_window.show()
    sys.exit(app.exec_())