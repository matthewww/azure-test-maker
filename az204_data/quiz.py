import json
import random

def load_questions():
    questions = []
    with open('exam_questions.jsonl', 'r') as f:
        for line in f:
            questions.append(json.loads(line.strip()))
    return questions

def run_quiz():
    questions = load_questions()
    random.shuffle(questions)

    score = 0
    total = len(questions)

    print("=" * 50)
    print(f"Azure ML Quiz - {total} questions")
    print("=" * 50)

    for i, q in enumerate(questions, 1):
        print(f"\nQuestion {i}/{total}:")
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
            
        print("-" * 28)
        
        print(f"\nExplanation: {q['explanation']}")
        print(f"\nLearning Path: {q['learning_path']}")
        print(f"Module: {q['module']}")
        
        print()
        print("=" * 50)

        if i < total:
            input("\nPress Enter for next question...")

    print(f"Final Score: {score}/{total} ({score/total*100:.0f}%)")

if __name__ == "__main__":
    run_quiz()