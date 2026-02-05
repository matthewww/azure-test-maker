# Claude Code Commands

This directory contains custom Claude Code commands for the Azure Test Maker project.

## Available Commands

### `/generate-exam-questions`

Generates scenario-based exam questions from Azure training content.

**Usage:**
```bash
/generate-exam-questions
```

**What it does:**
1. Detects available training data in the repository
2. Asks which learning paths you want to generate questions for
3. Asks how many questions per learning path
4. Generates high-quality exam questions in JSONL format
5. Validates format and provides statistics

**Output:**
- Questions saved to `{course}_data/exam_questions.jsonl`
- JSONL format (one JSON object per line)
- Compatible with quiz applications

**Example workflow:**
```bash
# 1. First, scrape a course (if not already done)
python azure_course_scraper.py "https://learn.microsoft.com/en-us/training/courses/az-204t00"

# 2. Generate questions using Claude Code
/generate-exam-questions

# 3. Answer the prompts:
#    - Select AZ-204 course
#    - Select "Implement Azure App Service web apps"
#    - Enter "20" for number of questions
#    - Select "proportional" distribution

# 4. Questions are generated and saved!
```

**Features:**
- Interactive question selection
- Multiple question types (configuration, security, architecture, operations)
- Difficulty level mixing (easy, medium, hard)
- Realistic scenarios based on actual Azure usage
- Detailed explanations and additional notes

**Quality Standards:**
- Scenario-based questions (2-4 sentences)
- 4 plausible options with one correct answer
- Technical accuracy with current Azure features
- Educational explanations
- Tests understanding, not memorization

## Creating New Commands

To create a new command:

1. Create a markdown file in this directory: `my-command.md`
2. Add a title (# Command Name) at the top
3. Write the command instructions
4. Use the command: `/my-command`

**Command file structure:**
```markdown
# My Command Name

Brief description of what the command does.

## Task

Detailed instructions for Claude Code to follow...

## Steps

1. First step...
2. Second step...

## Output

Expected output format...
```

**Tips:**
- Be specific and clear in instructions
- Include examples where helpful
- Use markdown for formatting
- Test the command with small examples first
