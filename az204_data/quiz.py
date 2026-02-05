import json
import random
import os
from datetime import datetime

PROGRESS_FILE = 'quiz_progress.json'

def load_questions():
    questions = []
    with open('exam_questions.jsonl', 'r') as f:
        for line in f:
            questions.append(json.loads(line.strip()))
    return questions

def load_progress():
    """Load saved progress if it exists."""
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r') as f:
            return json.load(f)
    return None

def save_progress(seed, current_index, score, answers, total, filtered_questions):
    """Save current quiz progress."""
    progress = {
        'seed': seed,
        'current_index': current_index,
        'score': score,
        'answers': answers,
        'total': total,
        'filtered_questions': filtered_questions,
        'timestamp': datetime.now().isoformat()
    }
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(progress, f, indent=2)

def clear_progress():
    """Remove progress file."""
    if os.path.exists(PROGRESS_FILE):
        os.remove(PROGRESS_FILE)

def run_quiz():
    questions = load_questions()
    total_available = len(questions)
    
    # Check for existing progress
    progress = load_progress()
    resume = False
    
    if progress:
        print("=" * 50)
        print("Found saved progress!")
        print(f"Last session: {progress['timestamp'][:19]}")
        print(f"Progress: {progress['current_index']}/{progress['total']} questions")
        print(f"Score so far: {progress['score']}/{progress['current_index']}")
        print("=" * 50)
        choice = input("\nResume previous quiz? (Y/N): ").upper().strip()
        
        if choice == 'Y':
            resume = True
            seed = progress['seed']
            current_index = progress['current_index']
            score = progress['score']
            answers = progress['answers']
            total = progress['total']
            questions = progress['filtered_questions']
        else:
            clear_progress()
    
    if not resume:
        # Get all unique learning paths
        learning_paths = sorted(set(q['learning_path'] for q in questions))
        
        print("=" * 50)
        print("LEARNING PATHS")
        print("=" * 50)
        for i, path in enumerate(learning_paths, 1):
            count = sum(1 for q in questions if q['learning_path'] == path)
            print(f"{i}. {path} ({count} questions)")
        
        print("\n" + "=" * 50)
        filter_choice = input("\nFilter by learning paths? (Y/N): ").upper().strip()
        
        if filter_choice == 'Y':
            print("\nEnter numbers separated by commas (e.g., 1,3,4)")
            print("Or press Enter to include all")
            selection = input("Your choice: ").strip()
            
            if selection:
                try:
                    selected_indices = [int(x.strip()) for x in selection.split(',')]
                    selected_paths = [learning_paths[i-1] for i in selected_indices if 1 <= i <= len(learning_paths)]
                    questions = [q for q in questions if q['learning_path'] in selected_paths]
                    print(f"\nFiltered to {len(questions)} questions from {len(selected_paths)} learning path(s)")
                except (ValueError, IndexError):
                    print("Invalid selection, using all questions")
        
        total_available = len(questions)
        
        # Ask how many questions
        print("\n" + "=" * 50)
        print(f"Available questions: {total_available}")
        print("=" * 50)
        while True:
            choice = input(f"\nHow many questions? (1-{total_available}, or press Enter for all): ").strip()
            if choice == "":
                total = total_available
                break
            try:
                total = int(choice)
                if 1 <= total <= total_available:
                    break
                print(f"Please enter a number between 1 and {total_available}")
            except ValueError:
                print("Please enter a valid number")
        
        # Start new quiz with random seed
        seed = random.randint(0, 999999)
        current_index = 0
        score = 0
        answers = []
    
    # Use seed for consistent shuffling
    random.seed(seed)
    random.shuffle(questions)
    filtered_questions = questions[:total]  # Take only the requested number
    questions = filtered_questions

    if not resume:
        print("=" * 50)
        print(f"Azure Quiz - {total} questions")
        print("=" * 50)

    for i in range(current_index, total):
        q = questions[i]
        print(f"\nQuestion {i+1}/{total}:")
        print("-" * 13)
        print()
                
        print(q['question'])
        print()
        
        for option, text in q['options'].items():
            print(f"{option}) {text}")
        print()
        print("-" * 28)
        
        while True:
            answer = input("\nYour answer (A/B/C/D): ").upper().strip()
            if answer in ['A', 'B', 'C', 'D']:
                break
            print("Please enter A, B, C, or D")
            
        if answer == q['correct_answer']:
            print("✓ Correct!")
            score += 1
        else:
            print(f"✗ Wrong. Correct answer: {q['correct_answer']}")
        
        # Track this answer
        answers.append({
            'user_answer': answer,
            'correct_answer': q['correct_answer']
        })
        
        # Save progress after each question
        save_progress(seed, i + 1, score, answers, total, questions)
            
        print("-" * 28)
        
        print(f"\nExplanation: {q['explanation']}")
        print(f"\nLearning Path: {q['learning_path']}")
        print(f"Module: {q['module']}")
        
        print()
        print("=" * 50)

        if i < total - 1:
            input("\nPress Enter for next question...")

    # Enhanced final feedback
    print("\n" + "=" * 50)
    print("QUIZ COMPLETE - RESULTS")
    print("=" * 50)
    
    percentage = (score / total) * 100
    print(f"\nFinal Score: {score}/{total} ({percentage:.1f}%)")
    
    # Performance assessment
    if percentage >= 85:
        print("Grade: EXCELLENT ✓✓✓ - You're well-prepared!")
    elif percentage >= 70:
        print("Grade: PASS ✓✓ - Good job! Review weak areas.")
    elif percentage >= 60:
        print("Grade: BORDERLINE ✓ - More study needed.")
    else:
        print("Grade: NEEDS WORK ✗ - Focus on fundamentals.")
    
    # Analyze wrong answers by learning path
    wrong_answers = [q for i, q in enumerate(questions) if i < len(answers) and answers[i]['user_answer'] != answers[i]['correct_answer']]
    
    if wrong_answers:
        print(f"\n{'-' * 50}")
        print(f"Areas Needing Review ({len(wrong_answers)} questions):")
        print(f"{'-' * 50}")
        
        # Group by learning path
        by_path = {}
        for i, q in enumerate(questions):
            if i < len(answers) and answers[i]['user_answer'] != answers[i]['correct_answer']:
                path = q['learning_path']
                if path not in by_path:
                    by_path[path] = []
                by_path[path].append(q)
        
        for path, qs in sorted(by_path.items(), key=lambda x: len(x[1]), reverse=True):
            print(f"\n• {path}: {len(qs)} incorrect")
            for q in qs[:3]:  # Show up to 3 modules per path
                print(f"  - {q['module']}")
            if len(qs) > 3:
                print(f"  - ... and {len(qs) - 3} more")
        
        print(f"\n{'-' * 50}")
        print("Review Your Mistakes:")
        print(f"{'-' * 50}")
        
        for i, q in enumerate(questions):
            if i < len(answers) and answers[i]['user_answer'] != answers[i]['correct_answer']:
                print(f"\nQ{i+1}: {q['question'][:80]}...")
                print(f"   Your answer: {answers[i]['user_answer']} ✗")
                print(f"   Correct: {answers[i]['correct_answer']} - {q['options'][answers[i]['correct_answer']]}")
                print(f"   → {q['explanation'][:150]}...")
    else:
        print("\n🎉 Perfect score! You got every question right!")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    run_quiz()