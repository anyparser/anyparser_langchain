"""
Anyparser LangChain Integration
"""

__version__ = "0.0.1"

import asyncio
from typing import List, Literal, Optional, Union

from anyparser_core import (
    Anyparser,
    AnyparserCrawlResult,
    AnyparserOption,
    AnyparserPdfResult,
    AnyparserResultBase,
    AnyparserUrl,
    OcrLanguage,
    OCRPreset,
)
from langchain_core.documents import Document


class AnyparserLoader:
    """Load documents from files using Anyparser API."""

    def __init__(
        self,
        file_path: Optional[str] = None,
        anyparser_api_key: Optional[str] = None,
        anyparser_api_url: Optional[str] = None,
        format: Literal["json", "markdown", "html"] = "markdown",
        model: Literal["text", "ocr", "vlm", "lam", "crawler"] = "text",
        encoding: Literal["utf-8", "latin1"] = "utf-8",
        image: Optional[bool] = None,
        table: Optional[bool] = None,
        ocr_language: Optional[List[OcrLanguage]] = None,
        ocr_preset: Optional[OCRPreset] = None,
        # Crawler options
        url: Optional[str] = None,
        max_depth: Optional[int] = None,
        max_executions: Optional[int] = None,
        strategy: Optional[Literal["LIFO", "FIFO"]] = None,
        traversal_scope: Optional[Literal["subtree", "domain"]] = None,
        **kwargs,
    ) -> None:
        """Initialize the AnyparserLoader.

        Args:
            file_path (Optional[str], optional): Path to the local file to be parsed. Required for file processing.
            anyparser_api_key (Optional[str], optional): Your Anyparser API key. Defaults to None.
            anyparser_api_url (Optional[str], optional): Your Anyparser API URL. Defaults to None.
            format (str, optional): Output format. Defaults to "markdown".
            model (str, optional): Processing model. Defaults to "text".
            encoding (str, optional): Text encoding. Defaults to "utf-8".
            image (Optional[bool], optional): Enable image extraction. Defaults to None.
            table (Optional[bool], optional): Enable table extraction. Defaults to None.
            ocr_language (Optional[List[OcrLanguage]], optional): OCR language settings. Defaults to None.
            ocr_preset (Optional[OCRPreset], optional): OCR preset configuration. Defaults to None.
            url (Optional[str], optional): Starting URL for crawler. Required for web crawling.
            max_depth (Optional[int], optional): Maximum crawl depth. Defaults to None.
            max_executions (Optional[int], optional): Maximum pages to crawl. Defaults to None.
            strategy (Optional[Literal["LIFO", "FIFO"]], optional): Crawling strategy. Defaults to None.
            traversal_scope (Optional[Literal["subtree", "domain"]], optional): Crawling scope. Defaults to None.
            **kwargs: Additional arguments to pass to Anyparser

        Raises:
            ValueError: If neither file_path nor url is provided, or if both are provided
        """
        # Validate input
        if file_path is None and url is None:
            raise ValueError("Either file_path or url must be provided")
        if file_path is not None and url is not None:
            raise ValueError("Only one of file_path or url should be provided")

        # For crawling, use url as file_path
        self.file_path = url if model == "crawler" else file_path
        self.format = format
        self.model = model

        # Initialize Anyparser options
        self.options = AnyparserOption(
            api_key=anyparser_api_key,
            api_url=anyparser_api_url,
            format=format,
            model=model,
            encoding=encoding,
            image=image,
            table=table,
            ocr_language=ocr_language,
            ocr_preset=ocr_preset,
            # Crawler options
            url=url,
            max_depth=max_depth,
            max_executions=max_executions,
            strategy=strategy,
            traversal_scope=traversal_scope,
            **kwargs,
        )

        # Initialize parser
        self.parser = Anyparser(options=self.options)

    def _create_document_from_url(
        self, url_result: AnyparserUrl, page_number: int = 1, total_pages: int = 1
    ) -> Document:
        """Create a Document from an AnyparserUrl result.

        Args:
            url_result (AnyparserUrl): The URL result from crawler
            page_number (int, optional): Page number. Defaults to 1.
            total_pages (int, optional): Total pages. Defaults to 1.

        Returns:
            Document: A LangChain Document with content and metadata
        """
        return Document(
            page_content=url_result.markdown or url_result.text or "",
            metadata={
                "source": url_result.url,
                "format": self.format,
                "page_number": page_number,
                "total_pages": total_pages,
                "url": url_result.url,
                "title": url_result.title,
                "status_message": url_result.status_message,
                "status_code": url_result.status_code,
                "politeness_delay": url_result.politeness_delay,
                "total_characters": url_result.total_characters,
                "crawled_at": url_result.crawled_at,
                "images": (
                    [
                        {
                            "name": img.display_name,
                            "index": img.image_index,
                            "page": img.page,
                        }
                        for img in url_result.images
                    ]
                    if url_result.images
                    else []
                ),
            },
        )

    def _create_document_from_result(
        self,
        result: Union[AnyparserResultBase, AnyparserPdfResult, AnyparserCrawlResult],
    ) -> List[Document]:
        """Create Documents from an Anyparser result.

        Args:
            result: The result from Anyparser (any type)

        Returns:
            List[Document]: List of LangChain Documents
        """
        documents = []

        if isinstance(result, AnyparserCrawlResult):
            # Handle crawler results
            total_pages = len(result.items)
            for i, item in enumerate(result.items, 1):
                documents.append(self._create_document_from_url(item, i, total_pages))
        elif isinstance(result, AnyparserPdfResult):
            # Handle PDF results
            total_pages = len(result.items)
            for i, page in enumerate(result.items, 1):
                documents.append(
                    Document(
                        page_content=page.markdown or page.text or "",
                        metadata={
                            "source": self.file_path,
                            "format": self.format,
                            "page_number": page.page_number,
                            "total_pages": total_pages,
                            "rid": result.rid,
                            "checksum": result.checksum,
                            "total_characters": result.total_characters,
                            "original_filename": result.original_filename,
                            "images": page.images if page.images else [],
                        },
                    )
                )
        else:
            # Handle basic results
            documents.append(
                Document(
                    page_content=result.markdown or "",
                    metadata={
                        "source": self.file_path,
                        "format": self.format,
                        "rid": result.rid,
                        "checksum": result.checksum,
                        "total_characters": result.total_characters,
                        "original_filename": result.original_filename,
                    },
                )
            )

        return documents

    async def aload(self) -> List[Document]:
        """Asynchronously load and parse the file with Anyparser.

        Returns:
            List[Document]: List of parsed documents with their metadata
        """
        try:
            # Parse the document
            result = await self.parser.parse(self.file_path)

            # For markdown/html format, result is a string
            if self.format in ["markdown", "html"]:
                if not isinstance(result, str):
                    raise ValueError(
                        f"Expected string for {self.format} format, got: {type(result)}"
                    )
                return [
                    Document(
                        page_content=result,
                        metadata={"source": self.file_path, "format": self.format},
                    )
                ]

            # For JSON format, result is a list of AnyparserResult
            if not isinstance(result, list):
                raise ValueError(f"Expected list for JSON format, got: {type(result)}")

            documents = []
            for item in result:
                documents.extend(self._create_document_from_result(item))
            return documents

        except Exception as e:
            raise ValueError(f"Error parsing document with Anyparser: {str(e)}")

    def load(self) -> List[Document]:
        """Synchronously load and parse the file with Anyparser.
        This is a convenience wrapper around aload() for synchronous usage.

        Returns:
            List[Document]: List of parsed documents with their metadata
        """
        loop = asyncio.get_event_loop()

        return loop.run_until_complete(self.aload())
