from langchain_core.prompts import ChatPromptTemplate

def generate_risks(context,llm):

    prompt = ChatPromptTemplate.from_template("""
    
    Analyze requirements and identify:

    Business Risks
    Technical Risks
    Dependency Risks
    Security Risks

    Context:
    {context}

    """)

    chain = prompt | llm

    result = chain.invoke(
        {"context":context}
    )

    return result.content