import json
import os
import datetime
import csv
import threading
import time
# import curses

TIME_PER_SECOND = 20  # Time limit per question in seconds

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
    # if not os.path.exists(file):
    #     with open(file, 'w') as f:
    #         json.dump({}, f)  
    with open(file, 'r') as f:
        # try:
        #     return json.load(f)
        # except json.JSONDecodeError:
        #     return {}
        return json.load(f)
    return {}
    
    

def save_users(users, file='users.json'):
    """Save user data to a JSON file."""
    with open(file, 'w') as f:
        json.dump(users, f, indent=4)

def create_user_profile(users):
    """Create or retrieve a user profile."""
    user_id = input("Enter your user ID: ")
    if user_id in users:
        print(f"\nWelcome back, {user_id}! Here is your quiz history:")
        display_history(user_id, users)
    else:
        print(f"\nWelcome, {user_id}! Your profile has been created.")
        users[user_id] = {'history': []}
    return user_id

def display_history(user_id, users):
    """Display a user's quiz history."""
    history = users.get(user_id, {}).get('history', [])
    if history:
        print(f"\n{Colors.BOLD}Quiz History:{Colors.ENDC}")
        for entry in history:
            print(f"Date: {entry['date']} - Category: {entry['category']} --> Score: {entry['score']}, Quit: {entry['quit']}")
    else:
        print("\nNo history available.")



def display_timer(time_left, timer_event, question):
    """Display a countdown timer for the remaining time."""
    print(f"\nTime: {Colors.OKCYAN}{time_left} seconds{Colors.ENDC}")
    while time_left >= 0 and not timer_event.is_set():
        time.sleep(1)
        time_left -= 1
        if time_left == 5:
            print(f"\n{Colors.WARNING}Hurry up! 5 seconds left...{Colors.ENDC}")
    
    if not timer_event.is_set():
        print(f"{Colors.FAIL}Time's up!{Colors.ENDC}")
        print(f"{Colors.BOLD}The correct answer was: {Colors.OKGREEN}{question['correct_answer']}{Colors.ENDC}\n")
        print("Press <<Enter>> to move to the next question -->")
        timer_event.set()

def ask_questions(questions,category,questions_count, time_per_question, user_id, users):
    """Ask the questions to the user with a time limit for each question."""
    score = 0
    did_quit = False
    for question in questions:
        print(f"\n{question['question']}")
        for i, option in enumerate(question['options'], 1):
            print(f"{i}. {option}")

        timer_event = threading.Event()
        timer_thread = threading.Thread(
            target=display_timer, args=(time_per_question, timer_event, question)
        )
        timer_thread.start()
        answer = input("Your answer (enter the number or -1 to quit): ")
        timer_event.set()
        timer_thread.join()

        # I added this condition to check if the timer was set (i.e., time's up), so the answer is not considered.
        # note: We can't stop IO operations , so the user can still input an answer after the timer is up.
        if timer_event.is_set():

            if answer :
                answer=str(answer).strip()
                if answer.isdigit() and 1 <= int(answer) <= len(question['options']):
                    choice = int(answer) - 1
                    if question['options'][choice] == question['correct_answer']:
                        print(f"{Colors.OKGREEN}Correct answer!{Colors.ENDC}")
                        score += 1
                    else:
                        print(f"{Colors.FAIL}Wrong answer. The correct answer was: {Colors.OKGREEN}{question['correct_answer']}")
                        print(Colors.ENDC)
                elif answer == "-1":
                    current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    users[user_id]['history'].append({'date': current_date, 'category':category, 'score': f"{score}/{questions_count}", 'quit': True})
                    save_users(users)
                    print("\nYou chose to quit. Your progress has been saved.")
                    did_quit = True
                    return [score,did_quit]
                else:
                    print(f"{Colors.FAIL}Wrong answer. The correct answer was: {Colors.OKGREEN}{question['correct_answer']}")
                    print(Colors.ENDC)
    return [score,did_quit]



def save_result(user_id, users,questions_count,category, score):
    """Save the result of a quiz for a user."""
    
    if score == "":
         save_users(users)
    else:
        print("test")
        current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        users[user_id]['history'].append({'date': current_date, 'category':category, 'score': f"{score}/{questions_count}", 'quit': False})
        save_users(users)
        print(f"\n{Colors.BOLD}Your final score is: {Colors.OKCYAN}{score}/{questions_count}{Colors.ENDC}")

def export_results_to_csv(user_id, users):
    """Export a user's results to a CSV file."""
    file_name = f"{user_id}_results.csv"
    with open(file_name, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Date", "Score", "Category", "Quit"])
        for entry in users[user_id]['history']:
            writer.writerow([entry['date'], entry['score'], entry['category'], entry['quit']])
    print(f"\nResults have been exported to {file_name}.")

def start_quiz():
    """Start the quiz application."""
    users = load_users()  
    user_id = create_user_profile(users) 
    save_result(user_id, users, "", "", "")

    with open("questions.json", 'r') as f:
        questions_by_category = json.load(f)
    categories = {str(i+1): category for i, category in enumerate(questions_by_category.keys())}

    while True:
        while True:
            print(f"\n{Colors.HEADER}Choose a category (-1 to quit Quiz):{Colors.ENDC}")
            for key, value in categories.items():
                print(f"{key}. {value}")

            choice = input("Enter the number of the category: ")

            if choice.lower() == "exit" or choice == "-1":
                print(f"{Colors.BOLD}Exit Quiz.{Colors.ENDC}")
                return

            if choice.isdigit() and choice in categories.keys():
                break  
            
            print(f"\n{Colors.FAIL}Invalid category! Please try again.{Colors.ENDC}")
            print(f"\n{Colors.WARNING}Reloading categories, be patient please... {Colors.ENDC}")

        category = categories.get(choice)

        print(f"\nYou chose the category: {Colors.HEADER}{category}{Colors.ENDC}")
        questions = questions_by_category[category]

        questions_count = len(questions)
        result = ask_questions(questions, category, questions_count, TIME_PER_SECOND, user_id, users)
        
        if not result[1]:
            save_result(user_id, users, questions_count, category, result[0])

        export_choice = input(f"{Colors.WARNING}Would you like to export your results to a CSV file? (y/n):{Colors.ENDC} ")
        if export_choice.lower() == 'y':
            export_results_to_csv(user_id, users)

        print(f"\n{Colors.BOLD}Returning to main menu...{Colors.ENDC}")


if __name__ == "__main__":
    start_quiz()
