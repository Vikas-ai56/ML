from node_logic import crawlWebsite, analyze_content, create_section_content , create_learning_section 
from utils import GraphState , SectionContentSchema , AnalysisJSONschema

# ----------------------------------------------------------------------------------------------------------------------

# Langgraph workflow to crawl, analyze, and extract section content from a webpage

from langgraph.graph import MessageGraph , START , END , StateGraph
from langgraph.checkpoint.memory import MemorySaver
from IPython.display import display , Image

def build_graph():
    builder = StateGraph(GraphState)
    builder.add_node("crawl", crawlWebsite)
    builder.add_node("analyze", analyze_content)
    builder.add_node("section", create_section_content)
    builder.add_node('writer',create_learning_section)

    builder.set_entry_point("crawl")
    builder.add_edge("crawl", "analyze")
    builder.add_edge("analyze", "section")
    builder.add_edge("section", 'writer')
    builder.add_edge("writer", END)

    graph = builder.compile(checkpointer=MemorySaver())

    display(Image(graph.get_graph().draw_mermaid_png()))

    return graph

# ----------------------------------------------------------------------------------------------------------------------

graph = build_graph()

thread = {'configurable':{'thread_id':'1'}}
messages = graph.invoke({"website_url": "https://en.wikipedia.org/wiki/Economy_of_India#:~:text=The%20economy%20of%20India%20is,119th%20by%20GDP%20(PPP)."},config=thread)

print(messages.keys())
