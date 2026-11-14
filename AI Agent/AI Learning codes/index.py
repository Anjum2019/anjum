from langchain_text_splitters import RecursiveCharacterTextSplitter #Splits large documents into smaller chunks.
from langchain_huggingface import HuggingFaceEmbeddings #Converts text chunks into numerical vectors (embeddings).
from langchain_chroma import Chroma  #Stores and searches those vectors.

# Step 1 load document (adding text for now)
docs = {
    "Customers may return eligible products within 30 days of delivery provided the items are unused, in their original condition, and accompanied by proof of purchase. Refunds are processed to the original payment method after the returned item has been inspected and approved. Customized products, digital downloads, gift cards, and perishable goods are generally non-returnable. If an item is received damaged, defective, or incorrect, customers should contact support promptly for a replacement, exchange, or refund. Return shipping charges may apply unless the return is due to an error on our part."
}

# step 2 Split into chunks
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50) #Configure how the document will be broken into chunks.
chunks = splitter.create_documents(docs) #Actually split the document into smaller chunks.

# Step 3 pick an embedding model
embedder = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2") #Initializes a Hugging Face embedding model that converts text chunks into vector embeddings for semantic search and storage in a vector database.

# Step 4 build a vector tore form chunks + embedding
db = Chroma.from_documents(   #Creates a Chroma vector database from your document chunks.
    documents=chunks,  #Sends all document chunks to Chroma for storage.
    embedding=embedder,   #Uses the Hugging Face embedding model to convert chunks into vectors.
    persist_directory="./chroma_db")  #Stores the vector database locally in the chroma_db folder.

print(f"indexed{len(chunks)} chunks")  #Prints how many chunks were added to the vector database.