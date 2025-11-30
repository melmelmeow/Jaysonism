import csv
import os
import random
import sys
from typing import List, Dict, Optional

# CONFIGURATION

TEAM_NAME = "Jaysonism" # the team’s name for the project folder
MAX_ITEMS = 5
ENABLE_RANDOMIZATION = True        # for shuffle question order in Student Mode
ENABLE_FILE_STORAGE = True         # to load/save questions to CSV
CSV_FILE = "questions.csv"         # CSV path 

# Each item in 'questions' is a dict:
# { "question": str, "choices": [str, str, str, str], "answer": "A"|"B"|"C"|"D" } and blah blah 

Question = Dict[str, object]

def default_questions() -> List[Question]:
    return [
        {
            "question": "What is the capital of France?",
            "choices": ["London", "Paris", "Rome", "Berlin"],
            "answer": "B",
        },
        {
            "question": "Which data structure stores items in LIFO order?",
            "choices": ["Queue", "Stack", "Array", "Tree"],
            "answer": "B",
        },
        {
            "question": "Which language is primarily used for styling web pages?",
            "choices": ["HTML", "CSS", "Python", "SQL"],
            "answer": "B",
        },
        {
            "question": "What does CPU stand for?",
            "choices": ["Central Processing Unit", "Computer Power Unit", "Central Program Utility", "Control Processing Unit"],
            "answer": "A",
        },
        {
            "question": "Which keyword defines a function in Python?",
            "choices": ["func", "def", "function", "lambda"],
            "answer": "B",
        },
    ]


# FILE STORAGE (CSV)
def ensure_csv_exists(path: str):
    if not os.path.exists(path):
        save_to_csv(path, default_questions())

def load_from_csv(path: str) -> List[Question]:
    questions: List[Question] = []
    if not os.path.exists(path):
        return default_questions()
    with open(path, mode="r", newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        # format: question, choiceA, choiceB, choiceC, choiceD, answer_letter
        for row in reader:
            if len(row) != 6:
                continue
            q, a, b, c, d, ans = [x.strip() for x in row]
            if not validate_answer_letter(ans):
                continue
            questions.append({"question": q, "choices": [a, b, c, d], "answer": ans.upper()})
    # trimer 
    if len(questions) < MAX_ITEMS:
        base = default_questions()
        for i in range(MAX_ITEMS - len(questions)):
            questions.append(base[i % len(base)])
    elif len(questions) > MAX_ITEMS:
        questions = questions[:MAX_ITEMS]
    return questions

def save_to_csv(path: str, questions: List[Question]):
    with open(path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        for q in questions:
            # placeholder entries and meow
            if not is_filled(q):
                writer.writerow(["", "", "", "", "", "A"])
            else:
                writer.writerow([
                    str(q["question"]),
                    str(q["choices"][0]),
                    str(q["choices"][1]),
                    str(q["choices"][2]),
                    str(q["choices"][3]),
                    str(q["answer"]),
                ])


# VALIDATION variable
def validate_answer_letter(ans: str) -> bool:
    return ans.upper() in {"A", "B", "C", "D"}

def letter_to_index(ans: str) -> int:
    return ord(ans.upper()) - ord("A")

def index_to_letter(idx: int) -> str:
    return chr(ord("A") + idx)

def require_int(prompt: str, min_val: int, max_val: int) -> int:
    while True:
        raw = input(prompt).strip()
        if raw.lower() == "q":
            return -1
        if raw.isdigit():
            val = int(raw)
            if min_val <= val <= max_val:
                return val
        print(f"Invalid input. Enter a number between {min_val} and {max_val}, or 'q' to cancel.")

def require_nonempty(prompt: str) -> str:
    while True:
        val = input(prompt).strip()
        if val:
            return val
        print("Input cannot be empty.")

def require_answer_letter(prompt: str) -> str:
    while True:
        ans = input(prompt).strip().upper()
        if validate_answer_letter(ans):
            return ans
        print("Invalid answer. Please enter A, B, C, or D.")

def is_filled(q: Question) -> bool:
    return bool(q.get("question")) and len(q.get("choices", [])) == 4 and validate_answer_letter(str(q.get("answer", "")))

# DISPLAY 

def print_divider():
    print("-" * 60)

def print_question(q: Question, idx: Optional[int] = None):
    header = f"Question {idx}: " if idx is not None else ""
    print(f"{header}{q['question']}")
    for i, choice in enumerate(q["choices"]):
        print(f"  {index_to_letter(i)}. {choice}")
    print(f"Correct Answer: {q['answer']}")

def print_placeholder(idx: int):
    print(f"Question {idx}: [Empty slot]")
  
# ADMIN CRUD
def admin_menu(questions: List[Question]):
    while True:
        print_divider()
        print("ADMIN MODE")
        print("1. View all questions")
        print("2. Create/Add a question")
        print("3. Edit/Update a question")
        print("4. Delete a question")
        print("5. Return to main menu")
        choice = require_int("Select an option (1-5): ", 1, 5)
        if choice == -1 or choice == 5:
            break
        if choice == 1:
            view_all(questions)
        elif choice == 2:
            create_question(questions)
        elif choice == 3:
            edit_question(questions)
        elif choice == 4:
            delete_question(questions)

def view_all(questions: List[Question]):
    print_divider()
    print("ALL QUESTIONS")
    for i in range(MAX_ITEMS):
        q = questions[i]
        if is_filled(q):
            print_question(q, i + 1)
        else:
            print_placeholder(i + 1)

def create_question(questions: List[Question]):
    print_divider()
    print("CREATE / ADD QUESTION")
  
    empty_indices = [i for i, q in enumerate(questions) if not is_filled(q)]
    if empty_indices:
        slot = empty_indices[0]
        print(f"Adding to empty slot #{slot + 1}")
    else:
        print("No empty slots. You can replace an existing question.")
        slot = require_int("Choose a question number to replace (1-5): ", 1, MAX_ITEMS)
        if slot == -1:
            return
        slot -= 1

    qtext = require_nonempty("Enter question text: ")
    choices = []
    for label in ["A", "B", "C", "D"]:
        choices.append(require_nonempty(f"Enter choice {label}: "))
    ans = require_answer_letter("Enter correct answer (A/B/C/D): ")

    questions[slot] = {"question": qtext, "choices": choices, "answer": ans}
    print("Question saved.")

def edit_question(questions: List[Question]):
    print_divider()
    print("EDIT / UPDATE QUESTION")
    idx = require_int("Select question number to edit (1-5): ", 1, MAX_ITEMS)
    if idx == -1:
        return
    idx -= 1
    q = questions[idx]
    if not is_filled(q):
        print("Selected slot is empty. Consider creating a question instead.")
        return

    print_question(q, idx + 1)
    print("Which field do you want to edit?")
    print("1. Question text")
    print("2. Choices")
    print("3. Correct answer")
    print("4. Edit all fields")
    field = require_int("Select (1-4): ", 1, 4)
    if field == -1:
        return

    if field in (1, 4):
        q["question"] = require_nonempty("New question text: ")
    if field in (2, 4):
        new_choices = []
        for label in ["A", "B", "C", "D"]:
            new_choices.append(require_nonempty(f"New choice {label}: "))
        q["choices"] = new_choices
    if field in (3, 4):
        q["answer"] = require_answer_letter("New correct answer (A/B/C/D): ")

    # Validate after edit
    if not is_filled(q):
        print("Warning: The updated question is incomplete. Please ensure all fields are set.")
    else:
        print("Question updated successfully.")

def delete_question(questions: List[Question]):
    print_divider()
    print("DELETE QUESTION")
    idx = require_int("Select question number to delete (1-5): ", 1, MAX_ITEMS)
    if idx == -1:
        return
    idx -= 1
    questions[idx] = {"question": "", "choices": ["", "", "", ""], "answer": "A"}  # Placeholder/empty
    print(f"Question #{idx + 1} cleared.")


# STUDENT MODE

def student_mode(questions: List[Question]):
    print_divider()
    print("STUDENT MODE: TAKE TEST")
    # Build a list of valid, filled questions
    quiz_items = [q for q in questions if is_filled(q)]
    # If some are empty, pad with placeholders to ensure 5 iterations
    while len(quiz_items) < MAX_ITEMS:
        quiz_items.append({
            "question": "[Placeholder question — no content]",
            "choices": ["", "", "", ""],
            "answer": "A",
        })

    order = list(range(MAX_ITEMS))
    if ENABLE_RANDOMIZATION:
        random.shuffle(order)

    answers_given = []
    correct_count = 0

    for i, pos in enumerate(order, start=1):
        q = quiz_items[pos]
        print_divider()
        print(f"Question {i} of {MAX_ITEMS}")
        print(q["question"])
        for idx, choice in enumerate(q["choices"]):
            print(f"  {index_to_letter(idx)}. {choice}")
        student_ans = require_answer_letter("Your answer (A/B/C/D): ")
        answers_given.append(student_ans)
        if student_ans == q["answer"]:
            correct_count += 1

    # Results
    print_divider()
    print("RESULTS")
    score = correct_count
    percentage = round((score / MAX_ITEMS) * 100, 2)
    print(f"Score: {score} out of {MAX_ITEMS}")
    print(f"Percentage: {percentage}%")

    print_divider()
    print("ANSWER REVIEW")
    for i, pos in enumerate(order, start=1):
        q = quiz_items[pos]
        given = answers_given[i - 1]
        status = "Correct" if given == q["answer"] else "Incorrect"
        print(f"Q{i}: {status} (Your: {given}, Correct: {q['answer']})")
        print(f"   {q['question']}")


# MAIN MENU
def main():
    print_divider()
    print("MULTIPLE CHOICE QUIZ MANAGER")
    print("Array-based CLI application")
    print_divider()

    # Load questions
    if ENABLE_FILE_STORAGE:
        ensure_csv_exists(CSV_FILE)
        questions = load_from_csv(CSV_FILE)
    else:
        questions = default_questions()

    # this is exactly MAX_ITEMS
    questions = (questions + default_questions())[:MAX_ITEMS]

    while True:
        print_divider()
        print("MAIN MENU")
        print("1. Admin Mode (Manage Questions)")
        print("2. Student Mode (Take Test)")
        print("3. Exit")
        choice = require_int("Select an option (1-3): ", 1, 3)

        if choice == -1 or choice == 3:
            # Save if enabled
            if ENABLE_FILE_STORAGE:
                save_to_csv(CSV_FILE, questions)
                print("Changes saved to CSV.")
            print("Goodbye!")
            break
        elif choice == 1:
            admin_menu(questions)
        elif choice == 2:
            student_mode(questions)

        print("\nInterrupted. Exiting...")
        sys.exit(0)
