from pydantic import BaseModel , Field 
from typing_extensions import TypedDict , Any , List , Optional , Dict 
from langchain.schema.runnable import RunnableLambda 

class SectionContentSchema(BaseModel): # Defined above
    """Schema for section-wise content."""
    sections: Optional[Dict[str, Any]] = Field(default=None, description='''Content of the website organized by sections, 
                                               with section titles as keys and content as values.''')
    extraction_summary: Optional[str] = Field(default=None, description='''Optional summary of the section extraction process
                                               or any issues encountered.''')

class EnhancedSectionContentSchema(BaseModel):
    sections: Optional[Dict[str, Any]] = Field(default=None, description="Content of the website organized by sections, with section titles as keys and content as values.")
    extraction_summary: Optional[str] = Field(default=None, description="Optional summary of the section extraction process or any issues encountered.")
    learning_summaries: Optional[Dict[str, List[str]]] = Field(default=None, description="Summaries related to each key learning, extracted from different sections.")
    learning_summary_extraction_summary: Optional[str] = Field(default=None, description="Summary of the learning summary extraction.")

class AnalysisJSONschema(BaseModel):
    key_learnings : List[str] = Field(title="Key Learning" , description="Stores Key Learning's and insights from the webpage")
    raw_output: str = Field(description="Raw output from the analysis process (e.g., summarization output).")
    errors: Optional[str] = Field(default=None, description="Any errors encountered during analysis.")

class GraphState(TypedDict):
    website_url : str
    raw_html: Optional[str] = Field(description='Stores the raw html output of the webpage')
    analysis_results : Optional[Any]
    analysis_json: Optional[AnalysisJSONschema]  = Field(default=None, description='''Stores the analysis results in JSON format, 
                                                            including key learnings and raw output from the analysis process''')
    section_content: Optional[EnhancedSectionContentSchema] = Field(default=None, description='''Stores the section-wise content extracted from the webpage,
                                                            with section titles as keys and content as values.''')
    key_learnings: Optional[List[str]]