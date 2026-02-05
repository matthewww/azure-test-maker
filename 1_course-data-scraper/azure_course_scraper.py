"""
Azure Learning Course Scraper - Metadata Only Version
Extracts training content from Microsoft Learn courses for agent grounding.
Image metadata extracted but no downloads (based on investigation showing 0% success rate).

Usage examples:
1. DP-100 (Data Scientist): https://learn.microsoft.com/en-us/training/courses/dp-100t01
2. AZ-900 (Azure Fundamentals): https://learn.microsoft.com/en-us/training/courses/az-900t00
3. AI-100 (AI Engineer): https://learn.microsoft.com/en-us/training/courses/ai-100t01

Structure: Course -> Learning Path -> Module -> Unit
"""
import requests
import json
import time
import re
import argparse
import os
from pathlib import Path
from datetime import datetime
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Optional

class AzureCourseScraper:
    def __init__(self, max_paths=None, max_modules_per_path=None, max_units_per_module=None, extract_content=True):
        self.base_url = "https://learn.microsoft.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })

        # Limits for large courses
        self.max_paths = max_paths
        self.max_modules_per_path = max_modules_per_path
        self.max_units_per_module = max_units_per_module
        self.extract_content = extract_content

    def fetch_page(self, url: str) -> Optional[str]:
        """Fetch a web page with error handling"""
        try:
            print(f"  Fetching: {url}")
            response = self.session.get(url, timeout=30)
            if response.status_code == 200:
                return response.text
            else:
                print(f"  HTTP {response.status_code} for {url}")
                return None
        except Exception as e:
            print(f"  Error fetching {url}: {e}")
            return None

    def parse_course_page(self, course_url: str) -> Dict:
        """Parse course overview page to extract learning paths"""
        html = self.fetch_page(course_url)
        if not html:
            return {}

        soup = BeautifulSoup(html, 'html.parser')

        # Extract course metadata
        course_info = {
            'url': course_url,
            'title': '',
            'description': '',
            'learning_paths': []
        }

        # Try to find course title
        title_elem = soup.find('h1')
        if title_elem:
            course_info['title'] = title_elem.get_text(strip=True)

        # Look for learning path articles with data-learn-uid attributes
        learning_path_articles = soup.find_all('article', attrs={'data-learn-uid': True})

        for article in learning_path_articles:
            learn_uid = article.get('data-learn-uid')
            if learn_uid and learn_uid.startswith('learn.'):
                # Convert UID to URL
                # learn.wwl.explore-azure-machine-learning-workspace -> /training/paths/explore-azure-machine-learning-workspace/
                path_slug = learn_uid.split('.')[-1]  # Get the last part after the dots
                path_url = f"{self.base_url}/en-us/training/paths/{path_slug}/"

                # Try to get the title from the article content (when it loads)
                # For now, we'll generate it from the slug
                path_title = path_slug.replace('-', ' ').title()

                course_info['learning_paths'].append({
                    'title': path_title,
                    'url': path_url,
                    'learn_uid': learn_uid
                })

        print(f"Found {len(course_info['learning_paths'])} learning paths")

        return course_info

    def parse_learning_path(self, path_url: str) -> Dict:
        """Parse learning path page to extract modules"""
        html = self.fetch_page(path_url)
        if not html:
            return {}

        soup = BeautifulSoup(html, 'html.parser')

        path_info = {
            'url': path_url,
            'title': '',
            'modules': []
        }

        # Try to extract title from page
        title_elem = soup.find('h1')
        if title_elem:
            path_info['title'] = title_elem.get_text(strip=True)

        # Find module links - look for relative paths that contain 'modules'
        module_links = soup.find_all('a', href=lambda href: href and 'modules' in href)

        seen_modules = set()
        for link in module_links:
            href = link.get('href')
            module_title = link.get_text(strip=True)

            # Convert relative URL to absolute
            if href.startswith('../../modules/'):
                # From /en-us/training/paths/xyz/, ../../modules/ should go to /en-us/training/modules/
                module_url = href.replace('../../modules/', f'{self.base_url}/en-us/training/modules/')
            elif href.startswith('/modules/'):
                module_url = self.base_url + '/en-us/training' + href
            elif href.startswith('/training/modules/'):
                module_url = self.base_url + href
            else:
                module_url = urljoin(path_url, href)

            # Ensure it ends with /
            if not module_url.endswith('/'):
                module_url += '/'

            # Only add if we have a title and haven't seen this module
            if module_title and module_url not in seen_modules:
                seen_modules.add(module_url)
                path_info['modules'].append({
                    'title': module_title,
                    'url': module_url
                })

        print(f"Found {len(path_info['modules'])} modules")
        return path_info

    def parse_module_page(self, module_url: str) -> Dict:
        """Parse module page to extract units"""
        html = self.fetch_page(module_url)
        if not html:
            return {}

        soup = BeautifulSoup(html, 'html.parser')

        module_info = {
            'url': module_url,
            'title': '',
            'description': '',
            'learning_objectives': [],
            'prerequisites': [],
            'units': []
        }

        # Extract title
        title_elem = soup.find('h1')
        if title_elem:
            module_info['title'] = title_elem.get_text(strip=True)

        # Find unit links - look for relative links with numbered patterns
        all_links = soup.find_all('a', href=True)
        unit_links = []

        for link in all_links:
            href = link.get('href', '')
            unit_title = link.get_text(strip=True)

            # Look for unit patterns like "1-introduction", "2-provision", etc.
            if (href and unit_title and
                any(keyword in href for keyword in ['introduction', 'summary', 'assessment', 'exercise']) or
                any(href.startswith(f'{i}-') for i in range(1, 20))):  # Check for numbered units 1-19

                # Convert relative URL to absolute
                unit_url = urljoin(module_url, href)

                # Try to extract unit number from URL or title
                unit_number = self.extract_unit_number(unit_url, unit_title)

                unit_links.append({
                    'number': unit_number,
                    'title': unit_title,
                    'url': unit_url,
                    'href': href
                })

        # Remove duplicates and sort by number
        seen_urls = set()
        for unit in unit_links:
            if unit['url'] not in seen_urls:
                seen_urls.add(unit['url'])
                module_info['units'].append(unit)

        # Sort by unit number
        module_info['units'].sort(key=lambda x: x['number'])

        print(f"  Found {len(module_info['units'])} units")
        return module_info

    def extract_unit_number(self, unit_url: str, unit_title: str) -> int:
        """Extract unit number from URL or title"""
        # Try to extract from URL like .../1-introduction/ or .../2-provision/
        url_match = re.search(r'/(\d+)-', unit_url)
        if url_match:
            return int(url_match.group(1))

        # Try to extract from title
        title_match = re.search(r'^(\d+)[\.\s]', unit_title)
        if title_match:
            return int(title_match.group(1))

        # Default ordering for common unit types
        unit_order = {
            'introduction': 1,
            'summary': 999,
            'assessment': 998,
            'knowledge-check': 998,
            'exercise': 900
        }

        unit_lower = unit_title.lower()
        for key, order in unit_order.items():
            if key in unit_lower:
                return order

        return 500  # Default middle value

    def classify_image_type(self, src: str, alt_text: str) -> str:
        """Classify image type based on filename and alt text"""
        src_lower = src.lower()
        alt_lower = alt_text.lower()

        # Check filename patterns
        if any(pattern in src_lower for pattern in ['diagram', 'architecture', 'flowchart', 'workflow']):
            return 'diagram'
        elif any(pattern in src_lower for pattern in ['screenshot', 'screen', 'ui', 'interface']):
            return 'screenshot'
        elif any(pattern in src_lower for pattern in ['chart', 'graph', 'plot']):
            return 'chart'
        elif any(pattern in src_lower for pattern in ['code', 'snippet', 'example']):
            return 'code_example'
        elif any(pattern in src_lower for pattern in ['icon', 'logo', 'badge']):
            return 'icon'

        # Check alt text patterns
        if any(pattern in alt_lower for pattern in ['diagram', 'architecture', 'flowchart', 'workflow', 'hierarchy']):
            return 'diagram'
        elif any(pattern in alt_lower for pattern in ['screenshot', 'screen', 'interface', 'portal', 'page', 'window']):
            return 'screenshot'
        elif any(pattern in alt_lower for pattern in ['chart', 'graph', 'plot', 'visualization']):
            return 'chart'
        elif any(pattern in alt_lower for pattern in ['code', 'snippet', 'example', 'syntax']):
            return 'code_example'
        elif any(pattern in alt_lower for pattern in ['icon', 'logo', 'badge', 'button']):
            return 'icon'

        return 'illustration'  # Default type

    def extract_image_context(self, img_elem) -> Dict:
        """Extract contextual information around the image"""
        context = {
            'preceding_heading': '',
            'following_text': '',
            'figure_caption': '',
            'parent_section': ''
        }

        # Find preceding heading
        current = img_elem
        while current:
            current = current.find_previous(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            if current:
                context['preceding_heading'] = current.get_text(strip=True)
                break

        # Check if image is in a figure with caption
        figure_parent = img_elem.find_parent('figure')
        if figure_parent:
            caption = figure_parent.find('figcaption')
            if caption:
                context['figure_caption'] = caption.get_text(strip=True)

        # Get following text (next paragraph or text node)
        next_elem = img_elem.find_next('p')
        if next_elem:
            text = next_elem.get_text(strip=True)
            if len(text) > 10:  # Only meaningful text
                context['following_text'] = text[:200]  # Limit to 200 chars

        return context

    def parse_unit_content(self, unit_url: str, output_dir: str = "output",
                          course_title: str = "", learning_path: str = "",
                          module_title: str = "") -> Dict:
        """Parse individual unit content"""
        if not self.extract_content:
            return {'content_skipped': True}

        html = self.fetch_page(unit_url)
        if not html:
            return {}

        soup = BeautifulSoup(html, 'html.parser')

        unit_info = {
            'content': '',
            'headings': [],
            'code_blocks': [],
            'images': [],
            'links': []
        }

        # Find the main content area
        content_elem = soup.find('main') or soup.find('article') or soup

        if content_elem:
            # Extract clean text content
            # Remove script and style elements
            for script in content_elem(["script", "style", "nav", "footer", "header"]):
                script.decompose()

            # Get text with some structure
            unit_info['content'] = content_elem.get_text(separator='\n', strip=True)

            # Extract headings
            for heading in content_elem.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
                level = int(heading.name[1])
                text = heading.get_text(strip=True)
                unit_info['headings'].append({
                    'level': level,
                    'text': text
                })

            # Extract code blocks
            for code_elem in content_elem.find_all(['code', 'pre']):
                code_text = code_elem.get_text(strip=True)
                if len(code_text) > 10:  # Only meaningful code blocks
                    unit_info['code_blocks'].append(code_text)

            # Extract images with metadata only
            for img in content_elem.find_all('img'):
                src = img.get('src', '')
                alt = img.get('alt', '')
                title = img.get('title', '')

                if src:
                    # Convert relative URLs to absolute
                    if src.startswith('../../'):
                        # Handle relative paths like ../../wwl-azure/module/media/image.png
                        absolute_src = f"https://learn.microsoft.com/en-us/{src[6:]}"
                    elif src.startswith('/'):
                        absolute_src = f"https://learn.microsoft.com{src}"
                    elif not src.startswith('http'):
                        absolute_src = urljoin(unit_url, src)
                    else:
                        absolute_src = src

                    # Classify image type based on alt text and filename
                    image_type = self.classify_image_type(src, alt)

                    # Extract contextual information
                    context = self.extract_image_context(img)

                    # Get image filename and extension
                    filename = os.path.basename(absolute_src)
                    if '?' in filename:
                        filename = filename.split('?')[0]

                    image_info = {
                        'src': src,
                        'absolute_url': absolute_src,
                        'alt_text': alt,
                        'title': title,
                        'filename': filename,
                        'image_type': image_type,
                        'context': context
                    }

                    unit_info['images'].append(image_info)

            # Extract links
            for link in content_elem.find_all('a', href=True):
                href = link.get('href')
                link_text = link.get_text(strip=True)
                if href and link_text:
                    unit_info['links'].append({
                        'url': href,
                        'text': link_text
                    })

        return unit_info

    def scrape_course(self, course_url: str, output_dir: str = "output", resume: bool = True) -> Dict:
        """Main method to scrape entire course"""
        print(f"Starting course scrape: {course_url}")

        # Check for existing data to resume from
        existing_data = None
        if resume:
            existing_data = self.load_existing_data(course_url, output_dir)
            if existing_data:
                print("Found existing data - resuming from previous run")

        # Parse course overview (or use existing data)
        if existing_data:
            course_data = existing_data
            print(f"Loaded existing course: {course_data.get('title', 'Unknown')}")
        else:
            course_data = self.parse_course_page(course_url)
            if not course_data['learning_paths']:
                print("No learning paths found!")
                return {}

        # Apply path limit
        paths_to_process = course_data['learning_paths']
        if self.max_paths:
            paths_to_process = paths_to_process[:self.max_paths]

        # Process each learning path
        for path_idx, path_info in enumerate(paths_to_process):
            print(f"\n--- Learning Path {path_idx + 1}: {path_info['title']} ---")

            # Parse learning path
            path_data = self.parse_learning_path(path_info['url'])
            path_info.update(path_data)

            # Check if path_data was successfully parsed
            if not path_data or 'modules' not in path_info:
                print(f"  Skipping {path_info['title']} - failed to parse or no modules found")
                continue

            # Apply module limit
            modules_to_process = path_info['modules']
            if self.max_modules_per_path:
                modules_to_process = modules_to_process[:self.max_modules_per_path]

            # Process each module
            for module_idx, module_info in enumerate(modules_to_process):
                print(f"  Module {module_idx + 1}: {module_info['title']}")

                # Parse module
                module_data = self.parse_module_page(module_info['url'])
                module_info.update(module_data)

                # Apply unit limit
                units_to_process = module_info['units']
                if self.max_units_per_module:
                    units_to_process = units_to_process[:self.max_units_per_module]

                # Process each unit
                for unit_idx, unit_info in enumerate(units_to_process):
                    print(f"    Unit {unit_idx + 1}: {unit_info['title']}")

                    # Check if we should skip this unit (already scraped)
                    if existing_data:
                        existing_unit_content = self.get_existing_unit_content(existing_data, path_info['title'], module_info['title'], unit_info['title'])
                        if existing_unit_content:
                            print(f"      Skipping - already scraped")
                            unit_info.update(existing_unit_content)
                            continue

                    # Parse unit content
                    if self.extract_content:
                        unit_content = self.parse_unit_content(
                            unit_info['url'], output_dir,
                            course_data['title'], path_info['title'], module_info['title']
                        )
                        unit_info.update(unit_content)

                    # Small delay to be respectful
                    time.sleep(0.5)

                # Small delay between modules
                time.sleep(0.5)

            # Small delay between learning paths
            time.sleep(0.5)

        return course_data

    def generate_training_jsonl(self, course_data: Dict, output_file: str):
        """Generate JSONL format for training - one record per unit"""
        with open(output_file, 'w', encoding='utf-8') as f:
            for path in course_data.get('learning_paths', []):
                for module in path.get('modules', []):
                    for unit in module.get('units', []):
                        if unit.get('content'):
                            record = {
                                'course_title': course_data.get('title', ''),
                                'learning_path': path.get('title', ''),
                                'module_title': module.get('title', ''),
                                'unit_title': unit.get('title', ''),
                                'unit_url': unit.get('url', ''),
                                'content': unit.get('content', ''),
                                'headings': unit.get('headings', []),
                                'code_blocks': unit.get('code_blocks', []),
                                'images': unit.get('images', []),
                                'scraped_at': datetime.now().isoformat()
                            }
                            f.write(json.dumps(record) + '\n')

    def load_existing_data(self, course_url: str, output_dir: str) -> Dict:
        """Load existing scraped data if available"""
        # Generate the same filename that would be used for this course
        course_data = self.parse_course_page(course_url)
        if not course_data:
            return None

        course_title = course_data.get('title', 'unknown-course')
        safe_title = re.sub(r'[^\w\s-]', '', course_title).strip()
        safe_title = re.sub(r'[-\s]+', '-', safe_title).lower()

        json_filename = os.path.join(output_dir, f"{safe_title}_complete.json")

        if os.path.exists(json_filename):
            try:
                with open(json_filename, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading existing data: {e}")
                return None
        return None

    def should_skip_unit(self, existing_data: Dict, path_title: str, module_title: str, unit_title: str) -> bool:
        """Check if a unit already has content in existing data"""
        if not existing_data or 'learning_paths' not in existing_data:
            return False

        for path in existing_data.get('learning_paths', []):
            if path.get('title') == path_title:
                for module in path.get('modules', []):
                    if module.get('title') == module_title:
                        for unit in module.get('units', []):
                            if unit.get('title') == unit_title and unit.get('content'):
                                return True
        return False

    def get_existing_unit_content(self, existing_data: Dict, path_title: str, module_title: str, unit_title: str) -> Dict:
        """Get existing unit content if available"""
        if not existing_data or 'learning_paths' not in existing_data:
            return None

        for path in existing_data.get('learning_paths', []):
            if path.get('title') == path_title:
                for module in path.get('modules', []):
                    if module.get('title') == module_title:
                        for unit in module.get('units', []):
                            if unit.get('title') == unit_title and unit.get('content'):
                                # Return the content fields from the existing unit
                                return {
                                    'content': unit.get('content'),
                                    'headings': unit.get('headings', []),
                                    'code_blocks': unit.get('code_blocks', []),
                                    'images': unit.get('images', []),
                                    'links': unit.get('links', [])
                                }
        return None

def main():
    parser = argparse.ArgumentParser(description='Scrape Azure Learning courses for training data')
    parser.add_argument('course_url', help='Course URL (e.g., https://learn.microsoft.com/en-us/training/courses/dp-100t01)')
    parser.add_argument('--max-paths', type=int, help='Maximum number of learning paths to process')
    parser.add_argument('--max-modules', type=int, help='Maximum number of modules per learning path')
    parser.add_argument('--max-units', type=int, help='Maximum number of units per module')
    parser.add_argument('--no-content', action='store_true', help='Skip content extraction (structure only)')
    parser.add_argument('--no-resume', action='store_true', help='Start from scratch (ignore existing data)')
    parser.add_argument('--output-dir', default='output', help='Output directory for files')

    args = parser.parse_args()

    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)

    # Initialize scraper
    scraper = AzureCourseScraper(
        max_paths=args.max_paths,
        max_modules_per_path=args.max_modules,
        max_units_per_module=args.max_units,
        extract_content=not args.no_content
    )

    print("Azure Course Scraper - Metadata Only Version")
    print(f"Target: {args.course_url}")
    print(f"Extract content: {not args.no_content}")
    if args.max_paths:
        print(f"Max learning paths: {args.max_paths}")
    if args.max_modules:
        print(f"Max modules per path: {args.max_modules}")
    if args.max_units:
        print(f"Max units per module: {args.max_units}")

    start_time = datetime.now()
    print(f"Started at: {start_time}")

    try:
        # Scrape the course
        course_data = scraper.scrape_course(args.course_url, args.output_dir, resume=not args.no_resume)

        if course_data:
            # Generate output files
            course_title = course_data.get('title', 'unknown-course')
            safe_title = re.sub(r'[^\w\s-]', '', course_title).strip()
            safe_title = re.sub(r'[-\s]+', '-', safe_title).lower()

            # Complete JSON file
            json_filename = os.path.join(args.output_dir, f"{safe_title}_complete.json")
            with open(json_filename, 'w', encoding='utf-8') as f:
                json.dump(course_data, f, indent=2, ensure_ascii=False)

            # Training JSONL file
            if not args.no_content:
                jsonl_filename = os.path.join(args.output_dir, f"{safe_title}_training.jsonl")
                scraper.generate_training_jsonl(course_data, jsonl_filename)

            # Summary file
            summary = {
                'course_title': course_data.get('title', ''),
                'course_url': args.course_url,
                'scraped_at': start_time.isoformat(),
                'learning_paths_count': len(course_data.get('learning_paths', [])),
                'total_modules': sum(len(path.get('modules', [])) for path in course_data.get('learning_paths', [])),
                'total_units': sum(len(module.get('units', [])) for path in course_data.get('learning_paths', []) for module in path.get('modules', [])),
                'content_extracted': not args.no_content,
                'limits_applied': {
                    'max_paths': args.max_paths,
                    'max_modules_per_path': args.max_modules,
                    'max_units_per_module': args.max_units
                },
                'files_created': [
                    os.path.basename(json_filename),
                    os.path.basename(jsonl_filename) if not args.no_content else None
                ]
            }

            summary_filename = os.path.join(args.output_dir, f"{safe_title}_summary.json")
            with open(summary_filename, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2)

            print("\n=== SCRAPING COMPLETE ===")
            print(f"Learning paths: {len(course_data.get('learning_paths', []))}")
            print(f"Total modules: {sum(len(path.get('modules', [])) for path in course_data.get('learning_paths', []))}")
            print(f"Total units: {sum(len(module.get('units', [])) for path in course_data.get('learning_paths', []) for module in path.get('modules', []))}")
            print(f"Content extracted: {not args.no_content}")
            print(f"JSON file: {json_filename}")
            if not args.no_content:
                print(f"Training JSONL: {jsonl_filename}")
            print(f"Summary: {summary_filename}")

        else:
            print("Failed to scrape course - no data extracted")

    except Exception as e:
        print(f"Error during scraping: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()