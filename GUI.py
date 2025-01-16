import json
import datetime
import sys
import threading
import time
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import tpexam_ap as backend_functions

TIME_PER_SECOND = 20 

def center_window(window):
    """Center the window on the screen."""
    qr = window.frameGeometry()
    cp = QDesktopWidget().availableGeometry().center()
    qr.moveCenter(cp)
    window.move(qr.topLeft())

class MainWindow(QMainWindow):
    def __init__(self, username, backend):
        super().__init__()
        self.backend = backend
        self.username = username  # Save username if needed
        self.setWindowTitle("Quiz Application")
        self.resize(800, 600)
        center_window(self)

        # Set main style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #F7F9FB;
            }
            QLabel {
                color: #34495E;
                font-size: 20px;
                font-weight: bold;
            }
            QPushButton {
                background-color: #3498DB;
                color: white;
                font-size: 16px;
                border: none;
                border-radius: 10px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #2980B9;
            }
            QPushButton:pressed {
                background-color: #1C5980;
            }
        """)

        # Title and Creator Labels
        self.LabelTitle = QLabel("Welcome to the Quiz Application", self)
        self.LabelTitle.setAlignment(Qt.AlignCenter)
        self.LabelTitle.setStyleSheet("font-size: 64px; margin: 20px;")
        
        self.LabelCreator = QLabel(
            "Created by: \nBOUDJELIDA Yanis,\n"
            "MOULOUDJ Mohamed,\n"
            "BRAHIM DJELLOUL ANTRI Hichem,\n"
            "FIALA Zackaria",
            self
        )
        self.LabelCreator.setAlignment(Qt.AlignCenter)
        self.LabelCreator.setStyleSheet("font-size: 16px; margin-bottom: 30px; color: #7F8C8D;")

        # Start Quiz Button
        self.StartQuizButton = QPushButton("Start Quiz", self)
        self.StartQuizButton.setFont(QFont("Arial", 16, QFont.Bold))
        self.StartQuizButton.setCursor(Qt.PointingHandCursor)	
        self.StartQuizButton.clicked.connect(self.start_quiz)

        # Layout setup
        self.layout = QVBoxLayout()
        
        self.layout.addWidget(self.LabelTitle)
        self.layout.addWidget(self.LabelCreator)
        self.layout.addWidget(self.StartQuizButton)
        self.layout.setAlignment(Qt.AlignCenter)
        self.layout.setStretch(0, 1)
        self.layout.setStretch(1, 1)
        self.layout.setStretch(2, 2)

        # Main Widget
        main_widget = QWidget(self)
        main_widget.setLayout(self.layout)
        self.setCentralWidget(main_widget)

    def start_quiz(self):
        """Start the quiz by displaying the category label."""
        # Assuming CategorieLabel is defined elsewhere and takes these parameters
        self.category_widget = CategorieLabel(self, self.username, self.backend)
        self.layout.addWidget(self.category_widget)
        self.LabelTitle.hide()
        self.LabelCreator.hide()
        self.StartQuizButton.hide()

class AuthWindow(QWidget):
    def __init__(self, backend):
        super().__init__()
        self.setWindowTitle("Authentication Page")
        self.setFixedSize(500, 300)
        center_window(self)
        
        # Main layout
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Header Label
        self.headerLabel = QLabel("Login")
        self.headerLabel.setAlignment(Qt.AlignCenter)
        self.headerLabel.setFont(QFont("Arial", 20, QFont.Bold))
        self.headerLabel.setStyleSheet("color: #2C3E50; margin-bottom: 20px;")

        # Username Label and Input
        self.nameLabel = QLabel("Username:")
        self.nameLabel.setFont(QFont("Arial", 16))
        self.nameLabel.setStyleSheet("color: #34495E; margin-top: 10px;")

        self.nameInput = QLineEdit()
        self.nameInput.setPlaceholderText("Enter your username")
        self.nameInput.setFont(QFont("Arial", 14))
        self.nameInput.setStyleSheet("""
            QLineEdit {
                border: 1px solid #7F8C8D;
                border-radius: 5px;
                padding: 8px;
                font-size: 14px;
                background-color: #ECF0F1;
            }
            QLineEdit:focus {
                border: 1px solid #3498DB;
            }
        """)

        # Login Button
        self.loginButton = QPushButton("Login")
        self.loginButton.setFont(QFont("Arial", 12, QFont.Bold))
        self.loginButton.setCursor(Qt.PointingHandCursor)
        self.loginButton.setStyleSheet("""
            QPushButton {
                background-color: #3498DB;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #2980B9;
            }
            QPushButton:pressed {
                background-color: #1C5980;
            }
        """)
        self.loginButton.clicked.connect(lambda: self.handle_login(backend))  # Connect to a method

        # Adding widgets to the layout
        self.layout.addWidget(self.headerLabel)
        self.layout.addWidget(self.nameLabel)
        self.layout.addWidget(self.nameInput)
        self.layout.addWidget(self.loginButton)

        # Add some spacing
        self.layout.setSpacing(15)

    def handle_login(self,backend):
        """Handles login logic."""
        username = self.nameInput.text().strip()
        
        # Check if the username is not empty
        if username:
            backend.set_userName(username)
            # Success message
            success_box = QMessageBox(self)
            success_box.setWindowTitle("Successful login")
            success_box.setText(f"Welcome, {username}!")
            success_box.setIcon(QMessageBox.Information)
            success_box.setStyleSheet("""
                QMessageBox {
                    background-color: #ECF0F1;
                    color: #2C3E50;
                    font-size: 16px;
                }
                QPushButton {
                    background-color: #3498DB;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 5px 10px;
                }
                QPushButton:hover {
                    background-color: #2980B9;
                }
                QPushButton:pressed {
                    background-color: #1C5980;
                }
            """)
            profile = backend.create_user_profile()
            if type(profile) != list:
                success_box.setInformativeText("Your profile has been created.")
            elif len(profile) != 0:
                success_box.setInformativeText("Here is your quiz history:")
                history=''
                for entry in profile:
                    history += f"Date: {entry['date']} - Category: {entry['category']} --> Score: {entry['score']}, Quit: {entry['quit']}"
                success_box.setDetailedText(history)
            success_box.setStandardButtons(QMessageBox.Ok)
            success_box.resize(800, 600)
            success_box.exec_()
            
            self.close()  # Close the authentication window
            self.show_categories_window(username, backend)  # Show categories after login
        
        else:
            # Warning message for empty username
            warning_box = QMessageBox(self)
            warning_box.setWindowTitle("Error")
            warning_box.setText("Username cannot be empty!")
            warning_box.setIcon(QMessageBox.Warning)
            warning_box.setStyleSheet("""
                QMessageBox {
                    background-color: #FDEDEC;
                    color: #C0392B;
                    font-size: 14px;
                }
                QPushButton {
                    background-color: #E74C3C;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 5px 10px;
                }
                QPushButton:hover {
                    background-color: #C0392B;
                }
                QPushButton:pressed {
                    background-color: #A93226;
                }
            """)
            warning_box.exec_()

    def show_categories_window(self, username,backend):
        """Show the categories window after login."""
        self.main_window = MainWindow(username,backend)
        self.main_window.show()


class CategorieLabel(QWidget):
    def __init__(self, parent, username, backend):
        super().__init__(parent)
        self.backend = backend
        self.categories, self.questions_by_category = backend.getCategories()
        self.username = username
        self.users = backend.getUsers()

        self.container_layout = QVBoxLayout(self)

        self.titleLabel=QLabel("Choose a category:", self)
        self.titleLabel.setAlignment(Qt.AlignLeft)
        self.titleLabel.setAlignment(Qt.AlignVCenter)
        self.titleLabel.setFont(QFont("Arial", 64, QFont.Bold))
        self.titleLabel.setStyleSheet("color: #34495E; margin-bottom: 20px;")

        self.container_layout.addWidget(self.titleLabel)

        # Create a scroll area to hold the category labels
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.create_categories_widget())

        self.container_layout.addWidget(self.scroll_area)

        # Apply styles
        self.setStyleSheet("""
            QScrollArea {
                background-color: #f9f9f9;
                border: 1px solid #dcdcdc;
                border-radius: 5px;
            }
            QPushButton {
                font-size: 24px;
                font-family: 'Arial';
                background-color: #007BFF;
                color: white;
                padding: 8px 15px;
                border-radius: 5px;
                border: none;   
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)

    def create_categories_widget(self):
        """Create a widget to hold category labels."""
        category_widget = QWidget(self)
        category_layout = QGridLayout(category_widget)

        # Add a button for each category
        rows=0
        for i,category in self.categories.items():
            button = QPushButton(category, self)
            button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            button.setCursor(Qt.PointingHandCursor)
            button.clicked.connect(lambda checked, cat=category: self.handle_category_click(cat))
            category_layout.addWidget(button,rows,(int(i)-1)%4)
            if int(i) % 4 == 0:
                rows=rows+1

        category_layout.setHorizontalSpacing(20)
        category_layout.setVerticalSpacing(20)
        category_layout.setContentsMargins(20, 20, 20, 20)
        return category_widget

    def handle_category_click(self,categorie):
        """Handle category button click."""
        button = self.sender()
        questions = self.questions_by_category[button.text()]
        self.quiz_widget = QuizLabel(questions, self.username, self.users, categorie, parent=self)
        self.container_layout.addWidget(self.quiz_widget)
        self.quiz_widget.return_to_parent = self.show_parent_widgets
        self.titleLabel.hide()
        self.scroll_area.hide()

    def show_parent_widgets(self):
        """Show the parent widgets."""
        if hasattr(self, "quiz_widget"):
            self.container_layout.removeWidget(self.quiz_widget)
            self.quiz_widget.deleteLater()
            del self.quiz_widget

        self.titleLabel.show()
        self.scroll_area.show()


class QuizLabel(QWidget):
    def __init__(self, questions, username, users, categorie, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Quiz")
        self.setMinimumSize(400, 300)
        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignCenter)
        self.categorie = categorie
        self.questions = questions
        self.username = username
        self.users = users
        self.score = 0
        self.idx = 0  # Keeps track of the current question
        self.return_to_parent = None

        self.question_label = QLabel("", self)
        self.question_label.setFont(QFont("Arial", 32))
        self.question_label.setAlignment(Qt.AlignCenter)
        self.question_label.setWordWrap(True)

        self.timerLabel = QLabel("",self)
        self.timerLabel.setFont(QFont("Arial", 32))
        self.timerLabel.setAlignment(Qt.AlignCenter)

        self.group = QGroupBox("Options", self)
        self.group.setLayout(QVBoxLayout())

        self.layout.addWidget(self.question_label)
        self.layout.addWidget(self.timerLabel)
        self.layout.addWidget(self.group)

        self.group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.submit_button = QPushButton("Submit", self)
        self.submit_button.clicked.connect(lambda: self.handle_submit(False))
        self.layout.addWidget(self.submit_button)

        self.labelCorrect = QLabel("", self)
        self.labelCorrect.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.labelCorrect)

        self.display_question(self.idx)

        # Apply styles
        self.setStyleSheet("""
            QLabel {
                font-family: 'Arial';
                font-size: 24px;
            }
            QGroupBox {
                font-family: 'Arial';
                font-size: 20px;
                border: 1px solid #dcdcdc;
                border-radius: 5px;
                padding: 10px;
            }
            QRadioButton {
                font-size: 20px;
            }
            QPushButton {
                font-size: 20px;
                font-family: 'Arial';
                background-color: #28a745;
                color: white;
                padding: 8px 15px;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)

    def display_question(self, idx):
        """Displays the current question and its options."""
        # question is actually a list of questions
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
        quit_button = QRadioButton("Quit", self)
        self.group.layout().addWidget(quit_button)

        self.display_timer(TIME_PER_SECOND)

    def handle_submit(self,timeEnd):
        """Handles the submit button click."""
        if timeEnd == True : 
            selected_answer = " "
        else :
            selected_answer = None
            for radio_button in self.group.findChildren(QRadioButton):
                if radio_button.isChecked():
                    selected_answer = radio_button.text()
                    break
        

        if selected_answer:
            # Ensure self.idx is within bounds before accessing self.questions
            if self.idx < len(self.questions):
                correct_answer = self.questions[self.idx]['correct_answer']
                result=self.check_answer(selected_answer, correct_answer)
                if result==-1:
                    return
                self.idx += 1  # Move to the next question
            if self.idx < len(self.questions):
                # Show the next question after a delay
                QTimer.singleShot(1000, lambda: self.display_question(self.idx))
            else:
                # Finish the quiz when no more questions are left
                QTimer.singleShot(1000, lambda: self.show_finish_dialog(False))
        else:
            QMessageBox.warning(self, "Error", "Please select an answer.")

    def check_answer(self, answer, correct_answer):
        """Check if the answer is correct."""
        if answer == "Quit":
            self.users[self.username]['history'].append({'date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 'category':self.categorie, 'score': f"{self.score}/{len(self.questions)}", 'quit': True})
            self.show_finish_dialog(True)
            return -1
        if answer != correct_answer:
            QMessageBox.warning(self, "Error", f"The correct answer was: {correct_answer}")
        else:
            self.score += 1
        return 1

    def show_finish_dialog(self,quit=False):
        """Show dialog when quiz finishes."""
        message_box = QMessageBox(self)
        message_box.setIcon(QMessageBox.Question)
        message_box.setWindowTitle("Quiz Finished!")
        message_box.setText("Do you want to save your history to a CSV file?")
        message_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        response = message_box.exec_()

        if response == QMessageBox.Yes:
            if quit:
                backend_functions.save_result(self.username, self.users, len(self.questions), self.categorie,"")
                backend_functions.export_results_to_csv(self.username,self.users)
            else:
                backend_functions.save_result(self.username, self.users, len(self.questions), self.categorie, self.score)
                backend_functions.export_results_to_csv(self.username,self.users)
            QMessageBox.information(self, "History Saved", f"Your results have been saved to {self.username}_results.csv.")
        else:
            if quit:
                backend_functions.save_result(self.username, self.users, len(self.questions), self.categorie, self.score)
        
        QMessageBox.information(self, "Your final score", f"Your final score is: {self.score}/{len(self.questions)}")
        # Return to parent (CategorieLabel)
        if self.return_to_parent:
            self.return_to_parent()

    def display_timer(self, time_left):
        """Display a countdown timer for the remaining time."""
        self.timer = QTimer(self)
        self.time_left = time_left

        def update_timer():
            if self.time_left >= 0:
                self.timerLabel.setText(f"Time: {self.time_left} s")
                self.time_left -= 1
            else:
                self.timer.stop()
                self.handle_submit(True)

        self.timer.timeout.connect(update_timer)
        self.timer.start(1000)  # Timer ticks every second

    
        


    # def save_result(self):
    #     """Save the result of a quiz for a user."""
    #     questions_count = len(self.questions)

    #     current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    #     self.users[self.username]['history'].append({'date': current_date, 'category':self.categorie, 'score': f"{self.score}/{questions_count}", 'quit': False})
    #     self.save_users() 
    
    # def save_users(self, file='users.json'):
    #     """Save user data to a JSON file."""
    #     with open(file, 'w') as f:
    #         json.dump(self.users, f, indent=4)


class BackEnd:
    def __init__(self):
        self.users = backend_functions.load_users()
        with open("questions.json", 'r') as f:
            self.questions_by_category = json.load(f)
    
    def set_userName(self, username):
        self.userName = username

    def getUsers(self):
        return self.users
    
    def create_user_profile(self):
        if self.userName in self.users:
            history = self.users.get(self.userName, {}).get('history', [])
            return history
        else:
            self.users[self.userName] = {'history': []}
            backend_functions.save_users(self.users)
            return self.userName
    
    def getCategories(self):
        categories = {str(i+1): category for i, category in enumerate(self.questions_by_category.keys())}
        return categories, self.questions_by_category



if __name__ == "__main__":
    app = QApplication(sys.argv)
    backend = BackEnd()
    auth_window = AuthWindow(backend)
    auth_window.show()
    sys.exit(app.exec_())