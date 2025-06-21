from flask import Flask, render_template, request, session, redirect, url_for
import random
import csv
import os
from datetime import datetime
import matplotlib.pyplot as plt
import io
import base64
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for using session

# Function to save user data to CSV
def save_student_data(user_id, user_name):
    try:
        with open('student_data.csv', mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([user_id, user_name])
            print(f"✅ Saved user data: {user_id}, {user_name}")
    except Exception as e:
        print(f"❌ Error saving user data: {e}")

# Function to load questions from CSV
def load_questions_from_csv():
    questions = []
    try:
        with open('sat_world_and_us_history.csv', mode='r', newline='', encoding='cp1252') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                if all(k in row for k in ["question_id", "prompt", "A", "B", "C", "D", "E", "answer"]):
                    questions.append({
                        "question_id": int(row["question_id"]),
                        "prompt": row["prompt"],
                        "A": row["A"],
                        "B": row["B"],
                        "C": row["C"],
                        "D": row["D"],
                        "E": row["E"],
                        "answer": row["answer"]
                    })
        print(f"✅ Loaded {len(questions)} questions from the CSV!")
    except Exception as e:
        print(f"❌ Error reading CSV: {e}")
    return questions

@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('base.html')

@app.route('/index', methods=['GET', 'POST'])
def start_test():
    if request.method == 'POST':
        user_id = request.form['user_id']
        user_name = request.form['name']
        save_student_data(user_id, user_name)

        questions_data = load_questions_from_csv()
        if not questions_data:
            return "No questions available. Please check the CSV file 🥺"

        selected_questions = random.sample(questions_data, min(5, len(questions_data)))
        session['selected_questions'] = selected_questions

        return render_template('index.html', user_id=user_id, user_name=user_name, questions=selected_questions)

    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit_answers():
    user_id = request.form['user_id']
    user_name = request.form['user_name']
    correct_count = 0
    total_questions = 0

    selected_questions = session.get('selected_questions', [])
    results = []  # ✅ Define results list here

    with open('user_responses.csv', mode='a', newline='', encoding='cp1252') as file:
        fieldnames = ['user_id', 'user_name', 'question_id', 'your_answer', 'correct_answer']
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        for q in selected_questions:
            key = f'answer_{q["question_id"]}'
            if key in request.form:
                user_choice = request.form[key]
                correct_choice = q['answer']

                is_correct = (user_choice == correct_choice)
                if is_correct:
                    correct_count += 1

                writer.writerow({
                    'user_id': user_id,
                    'user_name': user_name,
                    'question_id': q['question_id'],
                    'your_answer': user_choice,
                    'correct_answer': correct_choice
                })

                results.append({
                    'question_id': q['question_id'],
                    'prompt': q['prompt'],
                    'your_answer': user_choice,
                    'correct_answer': correct_choice,
                    'is_correct': is_correct
                })

                total_questions += 1

    # Save user score to user_scores.csv
    with open('user_scores.csv', mode='a', newline='', encoding='cp1252') as score_file:
        score_writer = csv.DictWriter(score_file, fieldnames=['user_id', 'user_name', 'score', 'total_questions', 'timestamp'])
        score_writer.writerow({
            'user_id': user_id,
            'user_name': user_name,
            'score': correct_count,
            'total_questions': total_questions,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })

    return render_template(
        'result.html',
        user_name=user_name,
        user_id=user_id,
        score=correct_count,
        total=total_questions,
        results=results  # ✅ Now results is defined
    )

# Function to load user attempts from user_scores.csv
import csv

def load_user_attempts(user_id):
    attempts = []
    try:
        with open('user_scores.csv', mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                print(f"Reading row: {row}")  # Debug print to check data
                
                # Convert both user_id from route and row to string for comparison
                if str(row['user_id']) == str(user_id):  
                    print(f"Match found for user_id {user_id}: {row}")  # Debug print to check if match is found
                    attempts.append({
                        'score': row['score'],
                        'total_questions': row['total_questions'],
                        'timestamp': row['timestamp']
                    })
    except Exception as e:
        print(f"Error loading user attempts: {e}")
    
    return attempts

import matplotlib.pyplot as plt
import io
import base64

@app.route('/dashboard/<user_id>')
def dashboard(user_id):
    print(f"User ID received: {user_id}")
    attempts = load_user_attempts(user_id)
    
    # Check if attempts are loaded correctly
    if not attempts:
        print(f"No attempts found for user {user_id}")
    else:
        print(f"Attempts for user {user_id}: {attempts}")
    
    # Prepare attempt_scores to pass to template
    attempt_scores = []
    total_score = 0
    total_attempts = len(attempts)

    # Extract data for the graph
    timestamps = []
    scores = []

    for i, attempt in enumerate(attempts, start=1):
        attempt_scores.append({
            'attempt_number': i,
            'score': attempt.get('score', 'N/A'),
            'total_questions': attempt.get('total_questions', 'N/A'),
            'timestamp': attempt.get('timestamp', 'Unknown')
        })
        total_score += int(attempt.get('score', 0))  # Add up all the scores
        
        # Extracting timestamp and score for graph
        timestamps.append(attempt.get('timestamp'))
        scores.append(int(attempt.get('score', 0)))  # Ensure the score is an integer
    
    # Create a plot for user performance
    fig, ax = plt.subplots()
    ax.plot(timestamps, scores, marker='o', linestyle='-', color='b', label='Score')

    ax.set(xlabel='Time', ylabel='Score', title=f'User Performance over Attempts (User {user_id})')
    ax.grid()
    ax.legend()

    # Save the plot to a BytesIO object and convert it to a base64 string for embedding in HTML
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    img_base64 = base64.b64encode(img.getvalue()).decode('utf-8')

    # Return the dashboard page with the plot
    return render_template(
        'dashboard.html',
        user_id=user_id,
        attempt_scores=attempt_scores,
        total_score=total_score,
        total_attempts=total_attempts,
        img_base64=img_base64  # Pass the base64 image to the template
        
    )

if __name__ == '__main__':
    app.run(debug=True)
