import gradio as gr
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.vectorstores   import Chroma
from langchain_community import embeddings
from langchain_community.chat_models import ChatOllama
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain.text_splitter import CharacterTextSplitter

def process_input(urls,question):
    model_local = ChatOllama(model="mistral")
    urls_list = urls.split("\n")
    # 1. Split data into chunks
    """urls = [
        "https://ollama.com",
        "https://ollama.com/blog/windows-preview",
        "https://ollama.com/blog/openai-compatibility",
    ]"""
    docs = [WebBaseLoader(url).load() for url in urls_list]
    docs_list = [item for sublist in docs for item in sublist]
    text_splitter = CharacterTextSplitter.from_tiktoken_encoder(chunk_size=7500, chunk_overlap=100)
    doc_splits = text_splitter.split_documents(docs_list)

    # 2. Convert documetns to Embeddings and store them

    vectorstore = Chroma.from_documents(
            documents = doc_splits,
            collection_name = "rag-chroma",        
            embedding=embeddings.ollama.OllamaEmbeddings(model='nomic-embed-text'),
    )

    retreiver = vectorstore.as_retriever()

    #3. Before RAG

    print("Before RAG")

    before_rag_template = "What is {topic}"
    before_rag_prompt = ChatPromptTemplate.from_template(before_rag_template)
    before_rag_chain = before_rag_prompt | model_local | StrOutputParser()

    print(before_rag_chain.invoke({"topic" : "Ollama"}))

    #4 After RAG

    print("\n#######3\nAfter RAG\n#######")
    after_rag_template = """Answer the question based only on the following context:
    {context}
    Question: {question}
    """

    after_rag_prompt = ChatPromptTemplate.from_template(after_rag_template)
    after_rag_chain = (
        {"context": retreiver, "question": RunnablePassthrough()}
        | after_rag_prompt
        | model_local
        | StrOutputParser()
    )
    return after_rag_chain.invoke(question)

#define Gradio interface
iface = gr.Interface(fn=process_input,
                     inputs = [gr.TextArea(label="Enter Urls separated by newlines"),gr.Textbox(label="question")],
                     outputs="text",
                     title="Document query with Ollama",   
                     description="Enter Urls and a query");

iface.launch()                     

print(after_rag_chain.invoke("What is Ollama?"))