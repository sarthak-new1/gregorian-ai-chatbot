import os
from uuid import uuid4
from langchain_pinecone import PineconeVectorStore
from pinecone import ServerlessSpec
from pinecone import Pinecone
from dependancies.embeddings import Embeddings

index_name = "georgian-labour-code-test-index"  # change if desired
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

if not pc.has_index(index_name):
    pc.create_index(
        name=index_name,
        dimension=3072,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1"),
    )

index = pc.Index(index_name)

class PineconeOperations:

    def get_vector_store(self):
        return PineconeVectorStore(
            index=index,
            embedding=Embeddings.get_embeddings()
        )
    
    def upload_documents(self, documents):
        vector_store = self.get_vector_store()
        # uuids = [str(uuid4()) for _ in range(len(documents))]
        vector_store.add_documents(documents=documents)
