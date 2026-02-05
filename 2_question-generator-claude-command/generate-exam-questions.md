# Generate Exam Questions

Generate scenario-based exam questions for Azure certification training materials.

## Task

You are tasked with generating high-quality, scenario-based exam questions for Azure certification learning paths. The questions should follow the exact format used in the existing `dp100_data/exam_questions.jsonl` file.

## Steps

1. **Identify the training data source**:
   - Look for `*_training.jsonl` files in the data directories
   - Ask the user which course/certification they want to generate questions for if multiple exist
   - Read the corresponding `*_summary.json` to understand the course structure

2. **Get user requirements**:
   - Ask which learning path(s) to generate questions for (show available options from the summary)
   - Ask how many questions to generate per learning path
   - Ask if they want questions distributed proportionally across modules or evenly

3. **Analyze existing format**:
   - Read `dp100_data/exam_questions.jsonl` to understand the exact format and quality standards
   - Each question must have: question, options (A-D), correct_answer, explanation, learning_path, module, additional_notes

4. **Read training content**:
   - Read the relevant sections from the `*_training.jsonl` file
   - Focus on the selected learning path(s)
   - Extract key concepts, technical details, and practical scenarios

5. **Generate questions**:
   - Create scenario-based questions (2-4 sentences describing a real-world situation)
   - Each question should have 4 plausible options with one clearly correct answer
   - Write detailed explanations (2-4 sentences) that explain WHY the answer is correct
   - Add additional_notes explaining why other options are incorrect
   - Ensure variety in question types:
     - Configuration/setup scenarios (40%)
     - Security and access control (20%)
     - Architecture and design decisions (20%)
     - Operational tasks (20%)
   - Mix difficulty levels: 30% easy, 50% medium, 20% hard

6. **Quality standards**:
   - Questions should be realistic and reflect actual Azure usage scenarios
   - Answers should be unambiguous and technically accurate
   - Wrong answers should be plausible to someone who hasn't studied
   - Test understanding and decision-making, not just memorization
   - Include specific versions, names, and requirements where appropriate
   - Reference Azure features and capabilities in explanations

7. **Write output**:
   - Determine the output file path (e.g., `az204_data/exam_questions.jsonl`)
   - If the file exists, ask whether to append or overwrite
   - Write in JSONL format (one JSON object per line, no array wrapper)
   - Ensure UTF-8 encoding

8. **Validate output**:
   - Verify the question count matches the request
   - Check that all questions have the required fields
   - Validate JSON format
   - Compare structure with dp100 format to ensure compatibility
   - Report statistics: total questions, breakdown by learning path/module

## Output Format (JSONL)

Each line is a complete JSON object with this structure:

```json
{
  "question": "Scenario-based question text describing a real-world situation...",
  "options": {
    "A": "First option text",
    "B": "Second option text",
    "C": "Third option text",
    "D": "Fourth option text"
  },
  "correct_answer": "B",
  "explanation": "Detailed explanation of why the correct answer is right...",
  "learning_path": "Name of the learning path",
  "module": "Name of the specific module",
  "additional_notes": "Optional notes explaining why other options are incorrect..."
}
```

## Example Questions

Reference the existing questions in `dp100_data/exam_questions.jsonl` for quality and style examples.

## Notes

- Questions should be challenging but fair
- Focus on practical application over theoretical knowledge
- Use current Azure terminology and service names
- Ensure explanations are educational and help reinforce learning
- Consider exam difficulty level appropriate for the certification (e.g., AZ-204 is associate level)
