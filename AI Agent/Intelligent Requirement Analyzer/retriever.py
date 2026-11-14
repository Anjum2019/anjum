def retrieve_context(question, db):

    docs = db.similarity_search(
        question,
        k=5
    )

    context = "\n\n".join(
        doc.page_content for doc in docs
    )

    return context

# Only relevant content goes to LLM.