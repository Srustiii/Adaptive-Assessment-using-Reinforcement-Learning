import csv
from ModelClass import *
import pandas as pd
import os
rl_model = RLModel()

rl_model.load_questions_from_csv("sat_world_and_us_history.csv") 

num_students = 1
bacche = []
for i in range(num_students):
    id = int(input("Enter Id : "))
    name = input("Enter name : ")
    dic = {'id': id, 'name': name}
    bacche.append(dic)

df = pd.read_csv('student_data.csv')
ids = [i for i in df['ID']]
with open('student_data.csv', mode='a', newline='') as file:
    writer = csv.writer(file)
    # writer.writerow(['ID', 'Name', 'Proficiency', 'Score'])
    for stu in bacche:
        print(f"\nTesting for Student {stu['id']}:\n")
        proficiency = 0.5
        if(stu['id'] in ids):
            proficiency = df.loc[df['ID'] == stu['id']]['Proficiency'].values[0]
        student = Student(stu['id'],proficiency)

        num_questions_to_answer = 10
        for _ in range(num_questions_to_answer):
            question = rl_model.select_question(student)
            if question is None:
                print("No more available questions.")
                break
            
            print("Q",_+1,")",question['prompt'])
            print("A) ",question['A'])
            print("B) ",question['B'])
            print("C) ",question['C'])
            print("D) ",question['D'])
            print("E) ",question['E'])
            option_selected = input("\nEnter the option selected : ")
            print("\n")
            if(option_selected==question['answer']):
                correct_answer = True
            else:
                correct_answer = False
            
            student.question_reports.append((question['question_id'],correct_answer))
            
            rl_model.update_proficiency(student, correct_answer)
        print("Name:",stu['name']," ID:",stu['id'])
        print("---------------------------------------------------------------")
        print(f"\nProficiency : {student.proficiency:.3f}")
        print(f"\nScore : {student.getScore():.1f}")
        print("---------------------------------------------------------------\n")
        if(stu['id'] in ids):
            df.loc[df['ID' ]== stu['id'],'Proficiency']=student.proficiency
            df.loc[df['ID' ]== stu['id'],'Score']=student.getScore()
            df.to_csv("student_data.csv",index=False)
        else:
            writer.writerow([stu['id'], stu['name'], student.proficiency, student.getScore()])
            print("Data added successfully!")
        

    print("\nTesting complete.")

