import os
from random import shuffle
from flask import Flask, session, request, redirect, render_template, url_for
from db_fix import get_question_after, get_quises, check_answer, get_completed_quizzes, save_completed_quiz, get_total_points, reset_quiz_progress

def start_quiz(quiz_id):
    session['quiz'] = int(quiz_id)
    session['last_question'] = 0
    session['answers'] = 0
    session['total'] = 0

def end_quiz():
    session.clear()

def quiz_form():
    q_list = get_quises()
    completed_quizzes = get_completed_quizzes()
    all_completed = len(completed_quizzes) == len(q_list)
    return render_template(
        'start.html',
        q_list=q_list,
        completed_quizzes=completed_quizzes,
        points=get_total_points(),
        all_completed=all_completed
    )

def init_game():
    if 'completed_quizzes' not in session:
        session['completed_quizzes'] = []
        session['points'] = 0
        session['total_points'] = 0

def index():
    if request.method == 'GET':
        return quiz_form()
    else:
        quest_id = int(request.form.get('quiz'))

        if quest_id in get_completed_quizzes():
            return redirect(url_for('index'))

        start_quiz(quest_id)
        return redirect(url_for('test'))

def save_answers():
    '''receives data from the form, checks if the answer is correct, writes the results to the session'''
    answer = request.form.get('ans_text')
    quest_id = request.form.get('q_id')
    session['last_question'] = quest_id
    session['total'] += 1
    if check_answer(quest_id, answer):
        session['answers'] += 1

def question_form(question):
    answers_list = [question[2], question[3], question[4], question[5]]
    shuffle(answers_list)
    return render_template('test.html', question=question[1], quest_id=question[0], answers_list=answers_list)

def test():
    if not ('quiz' in session) or int(session['quiz']) < 0:
        return redirect(url_for('index'))
    else:
        if request.method == 'POST':
            save_answers()
        next_question = get_question_after(session['last_question'], session['quiz'])
        if next_question is None or len(next_question) == 0:
            return redirect(url_for('result'))
        else:            
            return question_form(next_question)

def result():
    quiz_id = int(session['quiz'])
    completed = get_completed_quizzes()
    if quiz_id not in completed:
        save_completed_quiz(quiz_id, session['answers'])
    html = render_template(
        'result.html',
        right=session['answers'],
        total=session['total'],
        points=get_total_points(),
        completed=len(get_completed_quizzes())
    )
    session.pop('quiz', None)
    session.pop('last_question', None)
    session.pop('answers', None)
    session.pop('total', None)
    return html

folder = os.getcwd() # remember the current working folder
app = Flask(__name__, template_folder=folder, static_folder=folder)  
app.add_url_rule('/', 'index', index, methods=['post', 'get'])   # creates rule for URL '/'
app.add_url_rule('/test', 'test', test, methods=['post', 'get']) # creates rule for URL '/test'
app.add_url_rule('/result', 'result', result) # creates rule for URL '/test'
app.config['SECRET_KEY'] = 'ThisIsSecretSecretSecretLife'

if __name__ == "__main__":
    reset_quiz_progress()
    app.run()