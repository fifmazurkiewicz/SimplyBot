from qdrant_client import QdrantClient

client = QdrantClient(url="http://localhost:6333")

response = client.retrieve(
    collection_name="simplybot_docs",
    ids=[0, 1],
)
print(response)