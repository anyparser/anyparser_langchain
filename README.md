# Anyparser LangChain: Seamless Integration of Anyparser with LangChain

https://anyparser.com

**Integrate Anyparser's powerful content extraction capabilities with LangChain for enhanced AI workflows.** This integration package enables seamless use of Anyparser's document processing and data extraction features within your LangChain applications, making it easier than ever to build sophisticated AI pipelines.

## Installation

```bash
pip install anyparser-langchain
```

## Setup

Before running the examples, make sure to set your Anyparser API credentials as environment variables:

```bash
export ANYPARSER_API_KEY="your-api-key"
export ANYPARSER_API_URL="https://anyparserapi.com"
```

## Anyparser LangChain Examples

This `examples` directory contains examples demonstrating different ways to use the Anyparser LangChain integration.

```bash
python examples/01_single_file_json.py
python examples/02_single_file_markdown.py
python examples/03_multiple_files_json.py
python examples/04_multiple_files_markdown.py
python examples/05_load_folder.py
python examples/06_ocr_markdown.py
python examples/07_ocr_json.py
python examples/08_crawler.py
```

## Examples

### 1. Single File Processing
- `01_single_file_json.py`: Process a single file with JSON output
- `02_single_file_markdown.py`: Process a single file with markdown output

### 2. Multiple File Processing
- `03_multiple_files_json.py`: Process multiple files with JSON output
- `04_multiple_files_markdown.py`: Process multiple files with markdown output
- `05_load_folder.py`: Load and process all files from a folder (max 5 files)

### 3. OCR Processing
- `06_ocr_markdown.py`: Process images/scans with OCR (markdown output)
- `07_ocr_json.py`: Process images/scans with OCR (JSON output)

### 4. Web Crawling
- `08_crawler_basic.py`: Basic web crawling with essential settings

## Features Demonstrated

### Document Processing
- Different output formats (markdown, JSON)
- Multiple file handling
- Folder processing
- Metadata handling

### Web Crawling
- Basic crawling with depth and scope control
- Advanced URL and content filtering
- Crawling strategies (BFS, LIFO)
- Rate limiting and robots.txt respect

## Notes

- All examples use async/await for better performance
- Error handling is included in all examples
- Each example includes detailed comments explaining the options used
- OCR examples support multiple languages
- Crawler examples demonstrate various filtering and control options

## Features Demonstrated

- Different output formats (markdown, JSON)
- OCR capabilities with language support
- OCR performance presets
- Image extraction
- Table extraction
- Metadata handling
- Error handling
- Async/await usage

## License

Apache-2.0
