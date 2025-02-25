from firecrawl import FirecrawlApp

import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file (optional)

openai_api_key = os.getenv("OPENAI_API_KEY")
firecrawl_api_key = os.getenv("FCRAWL_API_KEY")

if not openai_api_key or not firecrawl_api_key:
    raise ValueError("Please set OPENAI_API_KEY and FIRECRAWL_API_KEY environment variables.")

# -----------------------------------------------------------------------------------------------------------

from utils import SectionContentSchema , AnalysisJSONschema , GraphState , EnhancedSectionContentSchema
import json
from typing_extensions import Dict , List 

# ----------------------------------------------------------------------------------------------------------------

# Initiate the firecrawl api and exrtract content from the webpage

def crawlWebsite(state : GraphState) -> GraphState:

    """
    Crawls a website and updates the given state with the retrieved content.
    Args:
        state (GraphState): The current state containing the website URL and other information.
    Returns:
        GraphState: The updated state with the retrieved HTML content, analysis JSON, and key learnings.
    Raises:
        Exception: If an error occurs during the crawling process, the exception is caught and logged, and the state is updated with None for raw_html.
    """
    
    try:
        url = state["website_url"]
        firecrawl = FirecrawlApp(api_key=firecrawl_api_key)

        page_content = firecrawl.scrape_url(url = url, params = {'formats': ['json','html'],
                                                                'jsonOptions': {
                                                                    'schema': AnalysisJSONschema.model_json_schema(),
                                                                }
        })
        json_page_content = json.dumps(page_content['json'] , indent=4)
        html_content = page_content['html']

        print(f"Page content for {url} retrieved successfully. \n {json_page_content}")
        
        if True:
            state["raw_html"] = html_content 
            state["analysis_json"] = page_content['json']
            state['key_learnings'] = page_content['json']['key_learnings']

    except Exception as e:
        print(f"Exception during crawling {url}: {e}")
        state["raw_html"] = None 

    return state 



# ----------------------------------------------------------------------------------------------------------------------

def analyze_content(state: GraphState) -> GraphState:
    """
    Analyzes the raw HTML content from the given GraphState and extracts key learnings.
    Args:
        state (GraphState): The state object containing the raw HTML to be analyzed.
    Returns:
        GraphState: The updated state object with analysis results, analysis JSON, and key learnings.
    The function performs the following steps:
    1. Retrieves the raw HTML content from the state.
    2. If no raw HTML is available, logs a message and returns the state unchanged.
    3. Initializes the ChatOpenAI model and PydanticOutputParser.
    4. Parses the HTML content using BeautifulSoup to extract structured text.
    5. Constructs a prompt for the language model to analyze the content.
    6. Invokes the language model and parser to obtain the analysis results.
    7. Updates the state with the analysis results, JSON, and key learnings.
    8. Handles any exceptions that occur during the analysis and logs an error message.
    Note:
        - The function assumes that `openai_api_key` and `AnalysisJSONschema` are defined elsewhere in the code.
        - The function uses BeautifulSoup with the 'lxml' parser to parse the HTML content.
    """
    
    raw_html = state.get("raw_html")
    if not raw_html:
        print("No raw HTML available for analysis.")
        return state

    llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0, openai_api_key=openai_api_key)

    parser = PydanticOutputParser(pydantic_object=AnalysisJSONschema)

    soup = BeautifulSoup(raw_html, 'lxml')
    structured_text = []

    for element in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'ul', 'ol']):
        if element.name.startswith('h'):
            structured_text.append(f"\n\n{element.get_text(strip=True)}\n")  # Add extra newlines for headings
        elif element.name == 'p':
            structured_text.append(f"{element.get_text(strip=True)}\n")
        elif element.name in ('ul', 'ol'):
            for li in element.find_all('li'):
                structured_text.append(f"- {li.get_text(strip=True)}\n") # Add bullet points for list items

    text_content = "".join(structured_text)

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert web content analyst. Extract key learnings and summarize the content."),
        ("human", "Analyze the following website content:\n\n{content}\n\n{format_instructions}"),
    ])

    chain = prompt | llm | parser

    try:
        analysis_output = chain.invoke({"content": text_content, "format_instructions": parser.get_format_instructions()})
        state["analysis_results"] = analysis_output
        state["analysis_json"] = analysis_output
        state["key_learnings"] = analysis_output.key_learnings

        print("Content analysis completed.")

    except Exception as e:
        error_message = f"Error during content analysis: {e}"
        print(error_message)
        state["analysis_json"] = AnalysisJSONschema(
            key_learnings=[],
            raw_output="Analysis failed due to error.",
            errors=error_message
        )
        state["key_learnings"] = []

    return state



# ----------------------------------------------------------------------------------------------------------------------

# All the data which is stored in the graph state is to be refined using an llm
# Extract key learnings from the webpage and generate content section-wise

from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from bs4 import BeautifulSoup

def create_section_content(state: GraphState) -> GraphState:
    """
    Collects section-wise content from raw HTML using a language model and a Pydantic output schema.
    Args:
        state (GraphState): The state object containing the raw HTML and other necessary information.
    Returns:
        GraphState: The updated state object with the extracted section content.
    The function performs the following steps:
    1. Retrieves raw HTML from the state object.
    2. Initializes a language model (LLM) with specified parameters.
    3. Sets up a Pydantic output parser with a predefined schema.
    4. Parses the raw HTML using BeautifulSoup to extract structured text.
    5. Constructs a prompt for the LLM to extract section content.
    6. Invokes the LLM with the constructed prompt and parses the output.
    7. Updates the state object with the extracted section content or an error message if extraction fails.
    Note:
        - The function expects the state object to have a "raw_html" key with the HTML content.
        - The extracted section content is stored in the "section_content" key of the state object.
        - If no raw HTML is available, the function returns the state object unchanged.
    """


    raw_html = state.get("raw_html")
    if not raw_html:
        print("No raw HTML available for sectioning.")
        return state

    llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0, openai_api_key=openai_api_key)

    parser = PydanticOutputParser(pydantic_object=SectionContentSchema)

    soup = BeautifulSoup(raw_html, 'lxml')
    structured_text = []

    for element in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'ul', 'ol']):
        if element.name.startswith('h'):
            structured_text.append(f"\n\n{element.get_text(strip=True)}\n")  # Add extra newlines for headings
        elif element.name == 'p':
            structured_text.append(f"{element.get_text(strip=True)}\n")
        elif element.name in ('ul', 'ol'):
            for li in element.find_all('li'):
                structured_text.append(f"- {li.get_text(strip=True)}\n") # Add bullet points for list items

    text_content = "".join(structured_text)

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert web content section extractor. ... Structure your output as a JSON object ... Ensure that the 'sections' field in the JSON is a dictionary where keys are the section titles and values are the corresponding content."),
        ("human", "Extract section content from the following Structured parsed html output:\n\n{html_content}\n\n{format_instructions}")
    ])

    chain = prompt | llm | parser

    try:
        section_output_schema = chain.invoke({"html_content": text_content, "format_instructions": parser.get_format_instructions()})
        state["section_content"] = section_output_schema 
        print("Section content extraction completed using LLM and Pydantic schema.")

    except Exception as e:
        error_message = f"Error during section content extraction: {e}"
        print(error_message)
        state["section_content"] = SectionContentSchema(sections=None, extraction_summary=error_message)

    return state

# ----------------------------------------------------------------------------------------------------------------------

# Concise summary of each learning point extracted from the sections

def create_learning_section(state : GraphState) -> GraphState:
    section_content_schema = state.get("section_content")
    key_learnings = state.get("key_learnings")

    if not section_content_schema or not section_content_schema.sections:
        print("No section content available for summarization.")
        return state
    if not key_learnings:
        print("No key learnings available to generate summaries.")
        return state
    

    llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0, openai_api_key=openai_api_key)
    learning_summaries: Dict[str, List[str]] = {}

    for learning in key_learnings:
        combined_section_text = ""
        for section_title, section_text in section_content_schema.sections.items():
            combined_section_text += f"\n\n## {section_title}\n{section_text}"

        prompt_text = (
            f"Summarize the following content, focusing on the key learning: '{learning}'.\n\n"
            f"{combined_section_text}\n\n"  # All sections combined
            f"Provide a concise summary, highlighting information from different sections relevant to the key learning."
        )
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful assistant that summarizes text with a focus on specific key learnings."),
            ("user", prompt_text)
        ])
        chain = prompt | llm

        try:
            summary = chain.invoke({})
            summary_text = summary.content
            summary_text = summary_text.strip()

            if summary_text:
                learning_summaries[learning].append(f"From '{section_title}': {summary_text}")

        except Exception as e:
            error_msg = f"Error summarizing section '{section_title}' for key learning '{learning}': {e}"
            print(error_msg)

    if section_content_schema:
        updated_section_content = EnhancedSectionContentSchema(
            sections=section_content_schema.sections,
            extraction_summary=section_content_schema.extraction_summary,
            learning_summaries=learning_summaries,
            learning_summary_extraction_summary="Key learning summaries extracted from sections."
        )
        state["section_content"] = updated_section_content

    return state