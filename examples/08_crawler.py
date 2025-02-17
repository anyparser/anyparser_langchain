"""Example: Web crawling with JSON output."""

import asyncio
import os
import traceback
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
    """Crawl website with JSON output to get multiple pages."""
    try:
        api_key = os.getenv("ANYPARSER_API_KEY")
        api_url = os.getenv("ANYPARSER_API_URL")

        loader = AnyparserLoader(
            url="https://anyparser.com/docs",
            anyparser_api_key=api_key,
            anyparser_api_url=api_url,
            format="json",  # Use JSON format to get multiple results
            model="crawler",
            max_depth=2,
            max_executions=10,
            strategy="LIFO",
            traversal_scope="subtree",
        )

        documents = await loader.aload()
        print_documents(documents)

    except Exception as e:
        print("\nError occurred:")
        print("=" * 50)
        traceback.print_exc()
        print("\nError message:", str(e))
        print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
