from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import random

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# ---------- Suspect Data ----------
suspects = {
    "Alice": {
        "role": "Daughter",
        "motive": "Recently cut from the will",
        "truths": {
            1: "I was reading in the library all evening.",
            2: "I didn’t touch the wine. The butler served it.",
            3: "Father looked stressed at dinner.",
            4: "I saw Bryan head toward the study after dinner."
        },
        "lies": {
            1: "I went outside after dinner for fresh air.",
            2: "I served wine because the butler was busy.",
            3: "He seemed perfectly fine.",
            4: "I didn’t see anything unusual that evening."
        }
    },
    "Bryan": {
        "role": "Butler",
        "motive": "Was about to be fired",
        "truths": {
            1: "I was preparing the guest room the whole time.",
            2: "Yes, I poured the wine, but I didn’t touch his glass after.",
            3: "Mr. Doyle looked pale during dessert.",
            4: "Ella seemed very nervous."
        },
        "lies": {
            1: "I went to the wine cellar after dinner.",
            2: "Ella poured the wine, not me.",
            3: "He looked healthy and cheerful.",
            4: "I didn’t notice anything strange."
        }
    },
    "Ella": {
        "role": "Maid",
        "motive": "Angry after being denied a raise despite years of loyalty",
        "truths": {
            1: "I was cleaning the dining room.",
            2: "I didn’t serve anything. That’s Bryan’s duty.",
            3: "Mr. Doyle barely ate and looked uneasy.",
            4: "Alice seemed upset during dinner."
        },
        "lies": {
            1: "I was asleep in my room during dinner.",
            2: "I served the wine because Bryan was busy.",
            3: "He looked fine and even joked with me.",
            4: "I didn’t notice anything suspicious."
        }
    }
}

# ---------- Game Configuration ----------
TOTAL_ROUNDS = 4

questions = {
    1: "Where were you during the murder?",
    2: "Did you serve the wine?",
    3: "How was Mr. Doyle behaving?",
    4: "Did you see anything suspicious?"
}

# ---------- Routes ----------

@app.route('/')
def start():
    killer = random.choice(list(suspects.keys()))
    session['killer'] = killer
    session['log'] = []
    session['round'] = 0
    session['suspects'] = suspects
    return render_template('start.html', suspects=suspects)

@app.route('/gameplay')
def gameplay():
    if 'killer' not in session:
        return redirect(url_for('start'))

    return render_template(
        'gameplay.html',
        suspects=suspects,
        questions=questions,
        rounds=session.get('round', 0)
    )

@app.route('/ask', methods=['POST'])
def ask():
    if 'killer' not in session:
        return jsonify({'error': 'Game not started'}), 400

    data = request.get_json()
    suspect = data.get('suspect')

    try:
        question = int(data.get('question'))
    except (TypeError, ValueError):
        return jsonify({'error': 'Invalid question number'}), 400

    if suspect not in suspects or question not in questions:
        return jsonify({'error': 'Invalid input'}), 400

    log = session.get('log', [])
    round_num = session.get('round', 0)

    # 🚫 Prevent asking more than 4 questions
    if round_num >= TOTAL_ROUNDS:
        return jsonify({'error': 'No more questions allowed. Please guess the killer.'}), 403

    killer = session['killer']
    answer = suspects[suspect]['lies'][question] if suspect == killer else suspects[suspect]['truths'][question]

    log.append({
        'suspect': suspect,
        'question': questions[question],
        'answer': answer
    })

    round_num += 1
    session['log'] = log
    session['round'] = round_num

    show_hint = round_num >= 2
    game_over = round_num >= TOTAL_ROUNDS

    return jsonify({
        'log': log,
        'show_hint': show_hint,
        'killer': killer if game_over else None,
        'game_over': game_over
    })


    round_num += 1
    session['log'] = log
    session['round'] = round_num

    show_hint = round_num >= 2
    game_over = round_num >= TOTAL_ROUNDS

    return jsonify({
        'log': log,
        'show_hint': show_hint,
        'killer': killer if game_over else None,
        'game_over': game_over
    })


@app.route('/conclusion', methods=['GET', 'POST'])
def conclusion():
    if 'killer' not in session:
        return redirect(url_for('start'))

    killer = session['killer']
    guess = None
    solved = None

    if request.method == 'POST':
        guess = request.form.get('guess')
        solved = (guess == killer)
        session['solved'] = solved
        return redirect(url_for('true_story'))

    return render_template('conclusion.html', killer=killer, solved=None, suspects=suspects)

@app.route('/true_story')
def true_story():
    killer = session.get('killer')
    solved = session.get('solved')
    all_suspects = session.get('suspects', {})

    if not killer or killer not in all_suspects:
        return redirect(url_for('start'))

    role = all_suspects[killer]['role']
    motive = all_suspects[killer]['motive']

    return render_template('true_story.html', killer=killer, role=role, motive=motive, solved=solved)

# ---------- Run App ----------
if __name__ == '__main__':
    app.run(debug=True)
