from langchain_core.prompts import ChatPromptTemplate

def generate_user_stories(context, llm):

    prompt = ChatPromptTemplate.from_template("""
    
    You are a Senior Business Analyst.

    Based on the BRD below generate User Stories.

    Context:
    {context}

    Format:

    As a <user>
    I want <action>
    So that <benefit>

    """)

    chain = prompt | llm

    result = chain.invoke({
        "context": context
    })

    return result.content