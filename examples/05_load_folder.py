"""Example: Load all files from a folder."""

import asyncio
import os
from pathlib import Path
from typing import List

from langchain_core.documents import Document

from anyparser_langchain import AnyparserLoader


def print_documents(documents: List[Document]) -> None:
    """Print documents and their metadata."""
    print(f"\nTotal documents: {len(documents)}")
    print("=" * 50)

    for i, doc in enumerate(documents, 1):
        print(f"\nDocument {i}:")
        print("=" * 50)

        # Print URL info if available
        if "url" in doc.metadata:
            print(f"URL: {doc.metadata['url']}")
        if "title" in doc.metadata:
            print(f"Title: {doc.metadata['title']}")
        if "status_message" in doc.metadata:
            print(f"Status: {doc.metadata['status_message']}")

        # Print content preview
        print(f"\nContent (first 500 characters):\n{doc.page_content[:500]}")

        # Print other metadata
        print("\nMetadata:")
        for key, value in doc.metadata.items():
            if key not in ["url", "title", "status_message"]:
                print(f"{key}: {value}")
        print("=" * 50)


async def main():
    """Load all files from a folder (max 5 files)."""
    api_key = os.getenv("ANYPARSER_API_KEY")
    api_url = os.getenv("ANYPARSER_API_URL")

    # Get all files from docs directory
    docs_dir = Path("docs")
    files = list(docs_dir.glob("*"))[:5]  # Limit to 5 files
    all_documents = []

    for file_path in files:
        loader = AnyparserLoader(
            file_path=str(file_path),
            anyparser_api_key=api_key,
            anyparser_api_url=api_url,
            format="markdown",
            model="text",
        )
        documents = await loader.aload()
        all_documents.extend(documents)

    print_documents(all_documents)


if __name__ == "__main__":
    asyncio.run(main())
