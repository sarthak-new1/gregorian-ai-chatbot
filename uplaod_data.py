import re
from src.data_extractor import DataExtractor
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dependancies.pinecone_operations import PineconeOperations

pdf_path = "D:/georgian-chatbot/data/Labour_Code_Georgian_Version.pdf"

def split_by_article(full_text: str):
    # Split but keep "მუხლი XX" at the start of each chunk
    parts = re.split(r'(?=\n?მუხლი\s+\d+\.?)', full_text)
    parts = [p.strip() for p in parts if p.strip()]
    return parts

def get_documents_from_articles(articles):
    """
    For each article block:
    - extract article_number and article_title from the first line
    - chunk the article with RecursiveCharacterTextSplitter
    - attach article metadata to every chunk
    """

    docs = []

    # Chunker: inside each article
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,      # smaller than 1000, more precise
        chunk_overlap=120,   # enough context overlap
        separators=["\n\n", "\n", " "],
    )

    for block in articles:
        lines = block.splitlines()
        first_line = lines[0].strip() if lines else ""

        # Match: მუხლი 10. Title...
        # Use ^ to anchor at the start of the line, more robust
        m = re.match(r'^მუხლი\s+(\d+)\.?\s*(.*)$', first_line)

        # Base metadata – always safe
        metadata = {
            "source": "Georgian Labour Code",
        }

        if m:
            article_number = m.group(1)
            article_title = m.group(2).strip()

            # Pinecone wants strings / numbers / bool / list[str]
            metadata["article_number"] = str(article_number)

            if article_title:
                metadata["article_title"] = article_title

        # Now split this article into smaller chunks
        chunks = text_splitter.split_text(block)

        for ch in chunks:
            docs.append(
                Document(
                    page_content=ch,
                    metadata=dict(metadata),  # copy so we don't accidentally mutate
                )
            )

    return docs

def upload_data(pdf_path):
    pinecone_ops = PineconeOperations()
    extractor = DataExtractor(pdf_path)
    text = extractor.extract_text()

    articles = split_by_article(text)
    documents = get_documents_from_articles(articles)
    pinecone_ops.upload_documents(documents)
    return len(documents)

if __name__ == "__main__":
    docs = upload_data(pdf_path)
    print(f"Uplaoded {docs} documents to Pinecone.")
