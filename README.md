# Azure Learning Course Scraper

A Python scraper to extract training content from Microsoft Learn courses for agent grounding and training data generation.

## Features

- Extracts complete course hierarchy: Course → Learning Paths → Modules → Units
- **Image metadata extraction**: Diagrams, screenshots, charts with classification and context
- Supports all Azure certification courses (DP-100, AZ-900, AI-100, etc.)
- Configurable limits for large courses
- Multiple output formats (JSON, JSONL) with multimodal data
- Respectful scraping with delays
- Content-only mode for structure extraction

## Why This Approach?

**60-80x more efficient** than raw HTML scraping:
- **Structured data**: Clean, organized hierarchy ready for AI training
- **Minimal size**: ~250KB vs 15-20MB of raw HTML per course
- **AI-optimized**: JSONL format with clean text, no HTML noise
- **NotebookLM ready**: Perfect for knowledge grounding without preprocessing
- **Multimodal**: Image context and metadata extracted (no downloads - investigation showed 0% success rate)

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

```bash
# Scrape DP-100 (Data Scientist) course
python azure_course_scraper.py "https://learn.microsoft.com/en-us/training/courses/dp-100t01"

# Scrape AZ-900 (Azure Fundamentals) course
python azure_course_scraper.py "https://learn.microsoft.com/en-us/training/courses/az-900t00"
```

### Advanced Usage

```bash
# Structure only (no content extraction) - faster
python azure_course_scraper.py "https://learn.microsoft.com/en-us/training/courses/dp-100t01" --no-content

# Extract content and image metadata
python azure_course_scraper.py "https://learn.microsoft.com/en-us/training/courses/dp-100t01"

# Limit scope for testing
python azure_course_scraper.py "https://learn.microsoft.com/en-us/training/courses/dp-100t01" --max-paths 2 --max-modules 3

# Custom output directory
python azure_course_scraper.py "https://learn.microsoft.com/en-us/training/courses/dp-100t01" --output-dir "dp100_data"
```

### Command Line Options

- `--max-paths N`: Limit to N learning paths (useful for testing)
- `--max-modules N`: Limit to N modules per learning path
- `--max-units N`: Limit to N units per module
- `--no-content`: Skip content extraction (structure only)
- `--output-dir DIR`: Specify output directory (default: output)

## Output Files

The scraper generates these files:

1. **`{course}_complete.json`** - Complete hierarchical structure with all metadata
2. **`{course}_training.jsonl`** - Flattened format for training (one record per unit)
3. **`{course}_summary.json`** - Summary statistics and metadata

### Training JSONL Format

Each line contains:
```json
{
  "course_title": "Designing and implementing a data science solution on Azure",
  "learning_path": "Explore Azure Machine Learning Workspace",
  "module_title": "Explore Azure Machine Learning workspace resources and assets",
  "unit_title": "Introduction",
  "unit_url": "https://learn.microsoft.com/...",
  "content": "Azure Machine Learning provides a platform...",
  "headings": [{"level": 2, "text": "Learning objectives"}],
  "code_blocks": ["# Python code example"],
  "images": [{"src": "../../media/diagram.png", "image_type": "diagram", "alt_text": "Architecture overview"}],
  "scraped_at": "2025-09-17T16:45:37.123456"
}
```

## Supported Courses

The scraper works with any Microsoft Learn course that follows the standard structure:

- **Data & AI**: DP-100, DP-900, AI-102, AI-900
- **Azure Fundamentals**: AZ-900, AZ-104, AZ-204, AZ-303, AZ-304
- **Security**: SC-900, SC-200, SC-300
- **Power Platform**: PL-900, PL-100, PL-200, PL-300

## Course Structure

```
Course (e.g., DP-100)
├── Learning Path 1: "Explore Azure Machine Learning workspace"
│   ├── Module 1: "Explore Azure Machine Learning workspace resources"
│   │   ├── Unit 1: Introduction
│   │   ├── Unit 2: Create workspace
│   │   └── Unit 8: Summary
│   └── Module 5: "Work with environments"
└── Learning Path 6: "Create custom copilots"
```

## Rate Limiting

The scraper includes built-in delays:
- 0.5 seconds between units
- 0.5 seconds between modules
- 0.5 seconds between learning paths

## Example Output Statistics

```
=== SCRAPING COMPLETE ===
Learning paths: 6
Total modules: 25
Total units: 180
Content extracted: true
JSON file: output/designing-and-implementing-a-data-science-solution-on-azure_complete.json
Training JSONL: output/designing-and-implementing-a-data-science-solution-on-azure_training.jsonl
Summary: output/designing-and-implementing-a-data-science-solution-on-azure_summary.json
```

## Error Handling

- HTTP errors are logged but don't stop the scraper
- Missing content is handled gracefully
- Progress is shown throughout the scraping process
- Failed units are skipped rather than crashing

## Best Practices

1. **Start with structure-only** (`--no-content`) to validate the course before full scraping
2. **Use limits for testing** (`--max-paths 1 --max-modules 2`)
3. **Be respectful** - built-in delays prevent overwhelming the servers
4. **Check course URLs** - ensure you're using the correct course URL format

## Troubleshooting

### Common Issues

1. **No learning paths found**: Verify the course URL is correct and includes `#course-syllabus`
2. **404 errors**: Some older courses may have different URL structures
3. **Empty content**: Some units may be assessment-only without text content

### Debug Mode

For troubleshooting, check the generated files:
- JSON file shows the complete structure
- Summary file shows counts and metadata
- Console output shows progress and any errors

## Generating Exam Questions

This repository includes a Claude Code Command for generating scenario-based exam questions from the scraped training data.

### Quick Start

```bash
# In Claude Code, run:
/generate-exam-questions
```

The command guides you through an interactive process to generate questions for any available learning path.

### How It Works

#### 1. Data Source Detection
The command automatically scans your repository for available training data:
- Looks for `*_training.jsonl` files (e.g., `az204_data/develop-solutions-for-microsoft-azure_training.jsonl`)
- Reads `*_summary.json` files to understand course structure
- Shows you available courses and learning paths

#### 2. Interactive Configuration
You'll be asked:
- Which course to generate questions for (if multiple available)
- Which learning path(s) to target
- How many questions to generate per learning path
- Whether to distribute questions proportionally across modules or evenly

#### 3. Question Generation Process
The command:
- Reads training content from the selected learning paths
- Analyzes existing questions in `dp100_data/exam_questions.jsonl` for format and quality standards
- Generates scenario-based questions with realistic Azure use cases
- Ensures proper distribution of question types and difficulty levels
- Validates format and quality

#### 4. Output
Questions are saved to `{course}_data/exam_questions.jsonl` in JSONL format, ready to use with quiz applications.

### Question Quality Standards

#### Question Structure
Each question includes:
- **Question**: 2-4 sentence scenario describing a real-world situation
- **Options**: 4 plausible answers (A, B, C, D) with one correct answer
- **Explanation**: 2-4 sentences explaining why the correct answer is right
- **Additional Notes**: Explanation of why other options are incorrect
- **Metadata**: Learning path and module references

#### Question Types (Distribution)
- **Configuration/Setup** (40%): "You need to configure/deploy/implement X..."
- **Security & Access Control** (20%): RBAC, authentication, authorization
- **Architecture & Design** (20%): When to use which service, comparing options
- **Operational Tasks** (20%): Monitoring, scaling, troubleshooting

#### Difficulty Levels
- **Easy** (30%): Straightforward scenarios, basic concepts
- **Medium** (50%): Requires understanding of multiple concepts
- **Hard** (20%): Complex scenarios, edge cases, trade-offs

#### Quality Characteristics
- ✅ Realistic scenarios reflecting actual Azure usage
- ✅ Technically accurate with current Azure features
- ✅ Clear, unambiguous correct answers
- ✅ Plausible wrong answers (not obviously incorrect)
- ✅ Tests understanding and decision-making (not memorization)
- ✅ Includes specific versions, names, and requirements

### Example Question

```json
{
  "question": "You are deploying a web application to Azure App Service that requires .NET 8.0 and must run continuously without any downtime. The application experiences variable traffic patterns with peak loads during business hours. You need to ensure the application can scale automatically based on CPU usage while maintaining at least two instances for high availability.\n\nWhich App Service plan tier should you choose?",
  "options": {
    "A": "Free tier with manual scaling",
    "B": "Shared tier with autoscale enabled",
    "C": "Basic tier (B2) with manual scale-out to 2 instances",
    "D": "Standard tier (S1) with autoscale rules configured"
  },
  "correct_answer": "D",
  "explanation": "The Standard tier is the minimum tier that supports autoscaling capabilities. It runs on dedicated compute instances and allows you to configure autoscale rules based on metrics like CPU usage. The Standard tier also supports multiple instances for high availability and runs apps continuously without the limitations of Free and Shared tiers.",
  "learning_path": "Implement Azure App Service web apps",
  "module": "Explore Azure App Service",
  "additional_notes": "Free and Shared tiers run on shared resources with CPU quotas and cannot scale out. Basic tier supports manual scale-out up to 3 instances but does not support autoscaling. Only Standard tier and above support autoscale rules."
}
```

### File Format: JSONL

Questions are stored in JSONL (JSON Lines) format:
- One complete JSON object per line
- No array wrapper
- UTF-8 encoding
- Compatible with streaming processors and line-by-line reading

### Using Generated Questions

#### With Python Quiz Application
```python
# Example: Load and quiz from generated questions
import json

with open('az204_data/exam_questions.jsonl', 'r', encoding='utf-8') as f:
    questions = [json.loads(line) for line in f]

# Use with your quiz application
for q in questions:
    print(q['question'])
    for key, value in q['options'].items():
        print(f"{key}. {value}")
```

#### Filtering by Learning Path
```python
import json

# Load only specific learning path questions
learning_path = "Implement Azure Functions"
questions = []

with open('az204_data/exam_questions.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        q = json.loads(line)
        if q['learning_path'] == learning_path:
            questions.append(q)

print(f"Found {len(questions)} questions for {learning_path}")
```

### Tips for Best Results

1. **Generate Questions in Batches**: Generate 10-20 questions at a time for better quality control. Large batches (50+) can lead to repetitive patterns.

2. **Review and Refine**: After generation, review questions for technical accuracy, realistic scenarios, and proper difficulty distribution.

3. **Module Coverage**: Generate questions proportionally across modules to ensure key concepts from each module are tested.

4. **Iterative Approach**: Generate initial set (20 questions), review quality, generate remaining questions in batches, then merge and deduplicate if necessary.

### Extending the System

#### Custom Question Types
Modify `.claude/commands/generate-exam-questions.md` to add new question types, update percentage distributions, or provide examples.

#### Custom Quality Standards
Adjust quality standards in the command file: change difficulty level distributions, modify question type ratios, or add certification-specific requirements.

#### Integration with Quiz Systems
The JSONL format is designed for easy integration:
- Import into quiz applications
- Convert to other formats (CSV, JSON arrays)
- Use with learning management systems (LMS)

### Troubleshooting

#### No Training Data Found
**Problem**: Command can't find `*_training.jsonl` files

**Solution**:
1. Run the scraper first: `python azure_course_scraper.py <course_url>`
2. Ensure files are in `{course}_data/` directories

#### Format Mismatch
**Problem**: Generated questions don't match expected format

**Solution**:
- Check `dp100_data/exam_questions.jsonl` for reference format
- Ensure all required fields are present
- Validate JSON syntax

#### Low Quality Questions
**Problem**: Generated questions are too easy/hard or not realistic

**Solution**:
- Regenerate with different instructions
- Specify difficulty level explicitly
- Review training data quality (ensure content is comprehensive)

#### Duplicate Questions
**Problem**: Similar questions appear multiple times

**Solution**:
- Generate smaller batches
- Review existing questions before adding more
- Manually deduplicate using question text comparison

### Best Practices

1. **Start Small**: Generate 10 questions first, review quality, then scale up
2. **Balance Coverage**: Ensure all important topics are covered
3. **Realistic Scenarios**: Use actual Azure use cases, not theoretical examples
4. **Clear Language**: Questions should be unambiguous and professional
5. **Technical Accuracy**: Verify service names, features, and limitations are current
6. **Educational Value**: Explanations should teach, not just justify the answer

### Examples by Certification

#### AZ-204 (Associate)
- Focus on practical implementation
- Cover common development scenarios
- Include integration patterns
- Test service configuration knowledge

#### DP-100 (Associate)
- Emphasize data science workflows
- Include ML model development scenarios
- Test Azure ML service understanding
- Cover data preparation and deployment

#### AZ-900 (Fundamentals)
- Keep scenarios simple and conceptual
- Focus on "what" and "why" over "how"
- Test service identification
- Cover cloud concepts basics

### Resources

- [Example Questions (DP-100)](dp100_data/exam_questions.jsonl)
- [Example Questions (AZ-204)](az204_data/exam_questions.jsonl)
- [Claude Code Command Source](.claude/commands/generate-exam-questions.md)
- [Microsoft Learn Courses](https://learn.microsoft.com/en-us/training/)

## Future Enhancements

- JavaScript rendering for dynamic content
- Parallel processing for faster scraping
- Additional output formats (CSV, XML)
- Image and diagram extraction
- Interactive quiz application