import os
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_groq import ChatGroq
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain.schema import Document
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv

load_dotenv()

class RAGSystem:
    def __init__(self, google_api_key=None, groq_api_key=None):
        self.google_api_key = google_api_key or os.getenv("GOOGLE_API_KEY")
        self.groq_api_key = groq_api_key or os.getenv("GROQ_API_KEY")
        
        if not self.google_api_key:
            raise ValueError("Google API Key is missing (for Embeddings). Please set GOOGLE_API_KEY in .env.")
        
        if not self.groq_api_key:
            raise ValueError("Groq API Key is missing (for LLM). Please set GROQ_API_KEY in .env.")
        
        # Using Google for Embeddings (Robust & Free tier available)
        self.embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004", google_api_key=self.google_api_key)
        
        # Using Groq for LLM (Fast inference)
        self.llm = ChatGroq(
            temperature=0.3, 
            model_name="llama-3.3-70b-versatile", 
            groq_api_key=self.groq_api_key
        )
        
        self.vector_store = None
        self.qa_chain = None

    def ingest_data(self, text_data):
        """
        Ingests text data, splits it, embeds it, and creates a vector store.
        """
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", " ", ""]
        )
        
        texts = text_splitter.split_text(text_data)
        if not texts:
            print("Warning: No text found to ingest.")
            return

        docs = [Document(page_content=t) for t in texts]
        
        print(f"Creating embeddings for {len(docs)} documents (using Google GenAI Embeddings)...")
        # Retry logic or robust creation could be added here
        self.vector_store = FAISS.from_documents(docs, self.embeddings)
        print("Vector store created successfully.")

    def setup_chain(self):
        if not self.vector_store:
            raise ValueError("Vector store not initialized. Call ingest_data first.")
            
        retriever = self.vector_store.as_retriever(search_kwargs={"k": 5})
        
        prompt_template = """You are a helpful AI assistant analyzing a WhatsApp chat history. 
        Use the provided context to answer the question.
        
        If the answer is not in the context, say "I don't see that information in the chat log."
        Do not hallucinate facts not present in the chat.
        
        Context:
        {context}

        Question: {question}
        Answer:"""
        
        PROMPT = PromptTemplate(
            template=prompt_template, input_variables=["context", "question"]
        )

        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=True,
            chain_type_kwargs={"prompt": PROMPT}
        )

    def query(self, query_text):
        if not self.qa_chain:
            self.setup_chain()
            
        result = self.qa_chain.invoke({"query": query_text})
        return result["result"]
