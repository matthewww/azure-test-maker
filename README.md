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

## Future Enhancements

- JavaScript rendering for dynamic content
- Parallel processing for faster scraping
- Additional output formats (CSV, XML)
- Image and diagram extraction
- Assessment question extraction