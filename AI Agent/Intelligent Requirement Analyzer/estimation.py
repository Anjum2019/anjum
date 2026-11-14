from langchain_core.prompts import ChatPromptTemplate

def estimate_effort(context,llm):

    prompt = ChatPromptTemplate.from_template("""
    
    Estimate development effort.

    Categorize:
    Small
    Medium
    Large

    Also provide Story Points.

    Context:
    {context}

    """)

    chain = prompt | llm

    result = chain.invoke(
        {"context":context}
    )

    return result.content