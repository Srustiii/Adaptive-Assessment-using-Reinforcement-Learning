import csv
import random
import math

import numpy as np 
import pandas as pd

class RLModel:
    def __init__(self):
        self.questions = []
        self.difficulties = {}
        self.responses = {}
        self.learning_rate = 0.07 
        self.learning_rate_decay = 1.00 

    def load_questions_from_csv(self, file_name="sat_world_and_us_history.csv"):
        with open(file_name, 'r', encoding='latin-1') as file:
            reader = csv.DictReader(file)
            self.questions = list(reader)
            for question in self.questions:
                self.difficulties[question['question_id']] = float(question['difficulty'])
                self.responses[question['question_id']] = {'total': 0, 'correct': 0}
                
    def _filter_available_questions(self, student):
        answered_question_ids = [report[0] for report in student.question_reports]
        return [question for question in self.questions if question['question_id'] not in answered_question_ids]

    def _calculate_proficiency_distance(self, student_proficiency, question_difficulty):
        return abs(student_proficiency - question_difficulty)
    
    def select_question(self, student):
        epsilon = 0.1 * self.learning_rate 
        explore = random.uniform(0, 1) < epsilon

        available_questions = self._filter_available_questions(student)
        selected_question = None
        while available_questions and not selected_question:
            question = random.choice(available_questions)
            if question['question_id'] not in student.question_reports:
                selected_question = question
                available_questions.remove(question)
        if not available_questions:
            print("No available questions for the student.")
            return None
        if explore:
            return random.choice(available_questions)
        else:
            self.learning_rate *= self.learning_rate_decay
            selected_question = min(available_questions, key=lambda q: self._calculate_proficiency_distance(student.proficiency, self.difficulties[q['question_id']]))
            return selected_question
        
    def update_proficiency(self, student, answer):
        correctness = int(answer == True)
        question_id = student.question_reports[-1][0]

        try:
            phat = sigmoid(student.proficiency - self.difficulties[question_id])
            reward = correctness - phat

            new_proficiency = student.proficiency + self.learning_rate * reward
            new_proficiency = max(0, min(1, new_proficiency))
            student.proficiency = new_proficiency
        except Exception as e:
            print(f"Error updating proficiency: {e}")
            raise Exception("Error updating proficiency") from e
        
def sigmoid(x):
    return 1 / (1 + math.exp(-x))
    
class Student:
    def __init__(self, student_id, proficiency=0.5):
        self.student_id = student_id
        self.proficiency = proficiency
        self.question_reports = []
        
    def getScore(self):
        total_questions = len(self.question_reports)
        correct_answers = sum([int(answer) for _, answer in self.question_reports])

        proficiency_score = self.proficiency * 100 
        correctness_score = (correct_answers / total_questions) * 100
        final_score = (proficiency_score + correctness_score) / 2  # Average 
        return final_score
