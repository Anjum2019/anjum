from langchain_core.prompts import ChatPromptTemplate

def generate_test_cases(context,llm):

    prompt = ChatPromptTemplate.from_template("""
    
    Create detailed test cases.

    Include:
    Test Case ID
    Scenario
    Steps
    Expected Result

    Context:
    {context}

    """)

    chain = prompt | llm

    result = chain.invoke(
        {"context":context}
    )

    return result.content