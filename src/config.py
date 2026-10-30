import os

from dotenv import load_dotenv

load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY") or None
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "agentic-rag")

NEO4J_URI = os.getenv("NEO4J_URI") or None
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME") or None
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD") or None

USING_REAL_PINECONE = PINECONE_API_KEY is not None
USING_REAL_NEO4J = all([NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD])
