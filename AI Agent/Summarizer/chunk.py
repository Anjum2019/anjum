from langchain_text_splitters import RecursiveCharacterTextSplitter 

#Why using RecursiveCharacterTextSplitter?
#Preserves paragraphs and sentences
#Supports chunk overlap
#Avoids cutting words unnecessarily
#Produces better embeddings
#Improves retrieval accuracy in RAG systems
#Works well for PDFs, websites, Word files, and text documents

your_long_document = """ John joined Microsoft in 2020. He worked as a Data Engineer. In 2023, he became an AI Architect."""
splitter = RecursiveCharacterTextSplitter(
    chunk_size=40,
    chunk_overlap=10, # got last 100 character in Overlap
)
chunks = splitter.split_text(your_long_document)
print(len(chunks))
print(chunks)


# With Overlap chunking example

# Chunk size = 8 words
# Chunk Overlap = 3 words
# Original text:
# "John joined Microsoft in 2020. He worked as a Data Engineer. In 2023, he became an AI Architect."

# Chunk 1
# John joined Microsoft in 2020. He worked as

# Chunk 2
# He worked as a Data Engineer. In 2023,

# Chunk 3
# In 2023, he became an AI Architect.