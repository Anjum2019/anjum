from langchain_core.prompts import ChatPromptTemplate

def generate_acceptance(context,llm):

    prompt = ChatPromptTemplate.from_template("""
    
    Generate Acceptance Criteria in Given When Then format.

    Context:
    {context}
    
    """)

    chain = prompt | llm

    result = chain.invoke(
        {"context":context}
    )

    return result.content