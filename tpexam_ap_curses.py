import json
import os
import datetime
import csv
import subprocess
import threading
import time
import curses

TIME_PER_SECOND = 20  # Time limit per question in seconds
COLUMN_INDEX_RESPONSE = 7
COLUMN_INDEX_TITLE = 5
def get_input(stdscr, prompt,actual_line):
    """Prompt the user for input and return the result."""
    curses.echo()  
    clear_screen(stdscr)
    actual_line = 3
    stdscr.addstr(actual_line, 0, prompt)  
    stdscr.refresh()
    user_input = stdscr.getstr(1, 0) 
    curses.noecho()  
    return user_input.decode("utf-8")   

class Colors:
    HEADER = '\033[95m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'  # Reset to default color
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def load_users(file='users.json'):
    """Load user data from a JSON file."""
    if os.path.exists(file):
        with open(file, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    else : 
        with open(file, 'w') as f:
            json.dump({}, f)
            return {}
   
    

def save_users(users, file='users.json'):
    """Save user data to a JSON file."""
    with open(file, 'w') as f:
        json.dump(users, f, indent=4)

def create_user_profile(users,stdscr,actual_line):
    """Create or retrieve a user profile."""
    user_id = get_input(stdscr, "Enter your user ID: ",actual_line)
    y, x = stdscr.getyx()
    if user_id in users:
        stdscr.addstr(actual_line, 0, f"\nWelcome back, {user_id}! Here is your quiz history:")
        
        stdscr.refresh()
        display_history(user_id, users,stdscr)
    else:
        stdscr.addstr(actual_line, 0, f"\nWelcome, {user_id}! Your profile has been created.")
        stdscr.refresh()
        users[user_id] = {'history': []}
    return user_id

def display_history(user_id, users,stdscr):
    """Display a user's quiz history."""
    history = users.get(user_id, {}).get('history', [])
    y, x = stdscr.getyx()
    if history:
        stdscr.addstr(y, 0, f"Quiz History:")
        for entry in history:
            y, x = stdscr.getyx()
            stdscr.addstr(y, 0, f"Date: {entry['date']} - Category: {entry['category']} --> Score: {entry['score']}, Quit: {entry['quit']}")
        stdscr.refresh()
    else:
        stdscr.addstr(y, 0, f"No history available.")
        stdscr.refresh()



def display_timer(time_left, timer_event, question,stdscr):
    """Display a countdown timer for the remaining time."""
    y, x = stdscr.getyx()

    while time_left >= 0 and not timer_event.is_set():
        stdscr.addstr(1, 80, f"Time: {time_left} seconds")
        stdscr.refresh()
        time.sleep(1)
        time_left -= 1
        if time_left == 5:
            stdscr.addstr(2, 80, f"Hurry up! 5 seconds left...")
            stdscr.refresh()
    if not timer_event.is_set():
        stdscr.addstr(3, 80, f"Time's up!")
        stdscr.addstr(4, 80, f"The correct answer was: {question['correct_answer']}")
        stdscr.refresh()
        timer_event.set()

def ask_questions(questions,category,questions_count, time_per_question, user_id, users,stdscr,actual_line):
    """Ask the questions to the user with a time limit for each question."""
    score = 0
    clear_screen(stdscr)
    actual_line = 3
    stdscr.refresh()
    for question in questions:
        clear_screen(stdscr)
        actual_line = 4
        stdscr.refresh()
        stdscr.addstr(actual_line, COLUMN_INDEX_TITLE, f"\n{question['question']}")
        actual_line +=1
        
        timer_event = threading.Event()
        timer_thread = threading.Thread(
            target=display_timer, args=(time_per_question, timer_event, question,stdscr)
        )
        timer_thread.start()
        current_option = 0 
        question["options"].append("Exit")
        while True:
            for i, option in enumerate(question['options'], 1):
                if i - 1 == current_option:
                    stdscr.addstr(actual_line+i, COLUMN_INDEX_RESPONSE, f"{i}. {option}", curses.A_REVERSE)
                else:
                    stdscr.addstr(actual_line+i, COLUMN_INDEX_RESPONSE, f"{i}. {option}")
           
            stdscr.refresh()
            key = stdscr.getch()
            if key == curses.KEY_DOWN and current_option < len(question['options'])-1 :
                current_option += 1
            elif key == curses.KEY_UP and current_option > 0:
                current_option -= 1
            elif key == 10:
                actual_line += len(question['options'])
                if question['options'][current_option] == "Exit":
                    current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    users[user_id]['history'].append({'date': current_date, 'category':category, 'score': f"{score}/{questions_count}", 'quit': True})
                    save_users(users)
                    stdscr.addstr(actual_line, COLUMN_INDEX_RESPONSE, f"\nYou chose to quit. Your progress has been saved.")
                    actual_line += 1
                    stdscr.refresh()
                    return [score,True]
                else:
                    answer = question['options'][current_option]
                    break
        timer_event.set()
        timer_thread.join()

        # I added this condition to check if the timer was set (i.e., time's up), so the answer is not considered.
        # note: We can't stop IO operations , so the user can still input an answer after the timer is up.
        if timer_event.is_set():

            if answer:
                answer=str(answer).strip()
                if answer.isdigit() and 1 <= int(answer) <= len(question['options']):
                    choice = int(answer) - 1
                    if question['options'][choice] == question['correct_answer']:
                        stdscr.addstr(30, 0, f"Correct answer!")
                        actual_line += 1
                        stdscr.refresh()
                        score += 1
                    else:
                        stdscr.addstr(30, 0, f"Wrong answer. The correct answer was: {question['correct_answer']}")
                        actual_line += 1
                        stdscr.refresh()
    return [score,False]



def save_result(user_id, users,questions_count,category, score,stdscr,actual_line):
    """Save the result of a quiz for a user."""
    current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    users[user_id]['history'].append({'date': current_date, 'category':category, 'score': f"{score}/{questions_count}", 'quit': False})
    save_users(users)
    stdscr.addstr(actual_line, 0, f"\nYour final score is: {score}/{questions_count}")
    stdscr.refresh()

def export_results_to_csv(user_id, users,stdscr,actual_line):
    """Export a user's results to a CSV file."""
    file_name = f"{user_id}_results.csv"
    with open(file_name, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Date", "Score", "Category", "Quit"])
        for entry in users[user_id]['history']:
            writer.writerow([entry['date'], entry['score'], entry['category'], entry['quit']])
    stdscr.addstr(actual_line, 0, f"\nResults have been exported to {file_name}.")
    
    stdscr.refresh()

def clear_screen(stdscr):
    stdscr.clear()
    draw_border(stdscr)
    curses.start_color()

    # Define color pairs
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_YELLOW)  # White text, blue background

    # Clear screen with color pair 1
    stdscr.bkgd(' ', curses.color_pair(1))
    stdscr.refresh()

def draw_border(stdscr):
    """Draw a rectangle border around the screen."""
    stdscr.clear()
    height, width = stdscr.getmaxyx()
    stdscr.border(0)  
    stdscr.refresh()

def start_quiz(stdscr):
    actual_line = 3
    curses.curs_set(0)  
    clear_screen(stdscr)
    actual_line = 3
    menu = ["Start Quiz", "View History", "Exit"]
    current_option = 0
    while True: 
        for idx, item in enumerate(menu):
            print("idx ",idx)
            print("actual line ",actual_line)
            if idx == current_option:
                stdscr.addstr(actual_line + idx, 2, item, curses.A_REVERSE)
            else:
                stdscr.addstr(actual_line + idx, 2, item)
        key = stdscr.getch()
        if key == curses.KEY_DOWN and current_option < len(menu) - 1:
            current_option += 1
        elif key == curses.KEY_UP and current_option > 0:
            current_option -= 1
        elif key == 10:
            if menu[current_option] == "Exit":
                actual_line += len(menu)
                stdscr.addstr(actual_line, 0, "Exiting Quiz.")
                stdscr.refresh()
                break
            elif menu[current_option] == "Start Quiz":
                clear_screen(stdscr)
                actual_line = 3
                users = load_users()  
                user_id = create_user_profile(users,stdscr,actual_line) 
                while True:
                    with open("questions.json", 'r') as f:
                        questions_by_category = json.load(f)

                    categories = {str(i+1): category for i, category in enumerate(questions_by_category.keys())}
                    categories['4'] = 'Exit'
                    stdscr.addstr(actual_line, 0, "Choose a category (-1 to quit Quiz):")
                    stdscr.refresh()
                    category_option = 0  # Default category option
                    while True:
                        for idx, (key, value) in enumerate(categories.items()):
                            if idx == category_option:
                                stdscr.addstr(idx + actual_line, 0, f"{key}. {value}", curses.A_REVERSE)
                            else:
                                stdscr.addstr(idx + actual_line, 0, f"{key}. {value}")
                        stdscr.refresh()

                        key = stdscr.getch()
                        if key == curses.KEY_DOWN and category_option < len(categories) - 1:
                            category_option += 1
                        elif key == curses.KEY_UP and category_option > 0:
                            category_option -= 1
                        elif key == 10:  # Enter key to select category
                            if list(categories.values())[category_option] == "Exit":
                                stdscr.addstr(actual_line, 0, "Exiting Quiz.")
                                exit()
                                break
                            else: 
                                clear_screen(stdscr)
                                actual_line = 3
                                selected_category = list(categories.values())[category_option]
                                category = selected_category
                                stdscr.addstr(actual_line, 0, f"You chose the category: {category}")
                                
                                stdscr.refresh()
                                questions = questions_by_category[category]
                                questions_count = len(questions)
                                result = ask_questions(questions, category, questions_count, TIME_PER_SECOND, user_id, users,stdscr,actual_line)
                                if not result[1]:
                                    save_result(user_id, users, questions_count, category, result[0],stdscr,actual_line)
                                clear_screen(stdscr)
                                actual_line = 3
                                stdscr.addstr(actual_line, 0, f"Would you like to export your results to a CSV file? (y/n):")
                                actual_line += 1
                                stdscr.refresh()
                                option = 0
                                optionYN = ["Yes", "No"]
                                while True:
                                    for idx, item in enumerate(optionYN):
                                        if idx == option:
                                            stdscr.addstr(idx + actual_line, 2, item, curses.A_REVERSE)
                                            
                                        else:
                                            stdscr.addstr(idx + actual_line, 2,item)
                                            
                                        stdscr.refresh()
                                    key = stdscr.getch()
                                    if key == curses.KEY_DOWN and option < len(optionYN) - 1:
                                        option += 1
                                    elif key == curses.KEY_UP and option > 0:
                                        option -= 1
                                    elif key == 10:
                                        if optionYN[option] == "Yes":
                                            export_results_to_csv(user_id, users,stdscr,actual_line)
                                            stdscr.addstr(actual_line, 0, "Returning to main menu...")
                                            stdscr.refresh()
                                            break
                                        else:
                                            stdscr.addstr(actual_line, 0, "Returning to main menu...")
                                            stdscr.refresh()
                                            break
                                    break  # Exit category selection 

# Start the application
if __name__ == "__main__":
    curses.wrapper(start_quiz)
    # start_quiz(stdscr)
