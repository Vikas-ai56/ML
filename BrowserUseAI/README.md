# BrowserUse - Web Content Analyzer

This module implements a workflow to crawl, analyze, and extract section content from a webpage using LangGraph. It leverages the Firecrawl API to retrieve webpage content and LangChain components to process and summarize the data.

## Features

- **Web Crawling:**  
  Crawls a specified URL to retrieve HTML and JSON data via the Firecrawl API.  
  See the [`crawlWebsite`](https://github.com/Vikas-ai56/ML/blob/main/BrowserUse/node_logic.py#L25) function in [`BrowserUse/node_logic.py`](https://github.com/Vikas-ai56/ML/blob/main/BrowserUseAI/node_logic.py).

- **Content Analysis:**  
  Processes the retrieved webpage content, extracts key learnings, and structures it into sections.

- **Graph Workflow:**  
  Uses a multi-step pipeline built with LangGraph. The workflow is defined in [`BrowserUse/browser_use.py`](https://github.com/Vikas-ai56/ML/blob/main/BrowserUse/browser_use.py#L11).

## Folder Structure
```
BrowserUse/ 
    ├── browser_use.py # Initializes and runs the LangGraph workflow. 
    ├── node_logic.py # Contains functions for crawling, analyzing, and processing website content. 
    └── .gitignore
```

## Setup

1. **Clone the Repository**
    ```git clone https://github.com/Vikas-ai56/ML/tree/main/BrowserUseAI```

2. **Environment Variables:**  
   Create a `.env` file in the project root with the following keys:
   - `OPENAI_API_KEY`
   - `FCRAWL_API_KEY`

1. **Install Dependencies:**  
   Ensure that required Python packages (e.g., Firecrawl, LangChain, LangGraph) are installed. Use:
   ```sh
   pip install -r requirements.txt