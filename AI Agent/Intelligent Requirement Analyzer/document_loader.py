from langchain_community.document_loaders import PyPDFLoader

def load_document(file_path):

    # Loads PDF and extracts text
    loader = PyPDFLoader(file_path)

    documents = loader. load ()

    return documents

# LangChain converts PDF into Document objects.
    