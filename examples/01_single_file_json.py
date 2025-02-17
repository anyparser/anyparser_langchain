"""Example: Process single file with JSON output."""

import asyncio
import os
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
    """Process single file with JSON output."""
    api_key = os.getenv("ANYPARSER_API_KEY")
    api_url = os.getenv("ANYPARSER_API_URL")

    loader = AnyparserLoader(
        file_path="docs/sample.pdf",
        anyparser_api_key=api_key,
        anyparser_api_url=api_url,
        format="json",
        model="text",
    )

    documents = await loader.aload()
    print_documents(documents)


if __name__ == "__main__":
    asyncio.run(main())
