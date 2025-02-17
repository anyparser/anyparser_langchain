from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from anyparser_core import (
    AnyparserCrawlDirective,
    AnyparserCrawlResult,
    AnyparserPdfPage,
    AnyparserPdfResult,
    AnyparserResultBase,
    AnyparserRobotsTxtDirective,
    AnyparserUrl,
    OcrLanguage,
    OCRPreset,
)
from langchain_core.documents import Document

from anyparser_langchain import AnyparserLoader


def mock_anyparser_result(result_type, format="json", **kwargs):
    if format in ["markdown", "html"]:
        return "mocked content in markdown/html format"
    if result_type == "base":
        return [AnyparserResultBase(**kwargs)]
    elif result_type == "pdf":
        return [AnyparserPdfResult(**kwargs)]
    elif result_type == "crawl":
        return [AnyparserCrawlResult(**kwargs)]
    return []


def mock_anyparser_url_result(**kwargs):
    default_kwargs = {
        "url": "http://example.com/page1",
        "status_code": 200,
        "status_message": "OK",
        "politeness_delay": 100,
        "total_characters": 100,
        "markdown": None,  # Default markdown to None
        "directive": MagicMock(spec=AnyparserCrawlDirective),  # Mock directive
        "title": "Page 1",
        "crawled_at": "now",
        "images": [],
        "text": "page 1 content",
    }
    updated_kwargs = default_kwargs.copy()
    updated_kwargs.update(kwargs)  # Update a copy to avoid modifying defaults
    return AnyparserUrl(**updated_kwargs)


def mock_anyparser_pdf_result(**kwargs):
    default_kwargs = {
        "rid": "test_rid",
        "original_filename": "test.pdf",
        "checksum": "test_checksum",
        "total_characters": 200,
        "total_items": 2,
        "markdown": "pdf result markdown",
        "items": [],  # Will be populated in tests
    }
    updated_kwargs = default_kwargs.copy()
    updated_kwargs.update(kwargs)
    return AnyparserPdfResult(**updated_kwargs)


def mock_anyparser_pdf_page_result(**kwargs):  # New mock for PDF page results
    default_kwargs = {
        "page_number": 1,
        "text": "pdf page content",
        "markdown": "pdf page content",
        "images": [],
    }
    updated_kwargs = default_kwargs.copy()
    updated_kwargs.update(kwargs)
    return AnyparserPdfPage(**updated_kwargs)  # Returns AnyparserPdfPage


def mock_anyparser_base_result(**kwargs):
    default_kwargs = {
        "rid": "test_rid",
        "original_filename": "test.pdf",
        "checksum": "test_checksum",
        "total_characters": 100,  # Added default value
        "markdown": "base content",  # Added default value
    }
    updated_kwargs = default_kwargs.copy()
    updated_kwargs.update(kwargs)
    return AnyparserResultBase(**updated_kwargs)


def mock_anyparser_crawl_result(**kwargs):
    default_kwargs = {
        "rid": "test_rid",
        "start_url": "http://example.com",
        "total_characters": 1000,
        "total_items": 2,  # Corrected to 2 for tests
        "markdown": "crawl result markdown",
        "robots_directive": MagicMock(
            spec=AnyparserRobotsTxtDirective
        ),  # Mock robots_directive
        "items": [],  # Will be populated in tests
    }
    updated_kwargs = default_kwargs.copy()
    updated_kwargs.update(kwargs)
    return AnyparserCrawlResult(**updated_kwargs)


@pytest.fixture
def mock_anyparser():
    with patch("anyparser_langchain.Anyparser") as MockAnyparser:
        yield MockAnyparser


class TestAnyparserLoader:
    def test_initialization_file_path(self):
        loader = AnyparserLoader(file_path="test.pdf")
        assert loader.file_path == "test.pdf"
        assert loader.options.url is None

    def test_initialization_url(self):
        loader = AnyparserLoader(url="http://example.com", model="crawler")
        assert loader.file_path == "http://example.com"
        assert loader.options.url == "http://example.com"

    def test_initialization_invalid_no_input(self):
        with pytest.raises(ValueError) as excinfo:
            AnyparserLoader()
        assert "Either file_path or url must be provided" in str(excinfo.value)

    def test_initialization_invalid_both_inputs(self):
        with pytest.raises(ValueError) as excinfo:
            AnyparserLoader(file_path="test.pdf", url="http://example.com")
        assert "Only one of file_path or url should be provided" in str(excinfo.value)

    def test_initialization_options_forwarding(self):
        loader = AnyparserLoader(
            file_path="test.pdf",
            anyparser_api_key="test_key",
            anyparser_api_url="http://test.com",
            format="html",
            model="ocr",
            encoding="latin1",
            image=True,
            table=False,
            ocr_language=[OcrLanguage.ENGLISH],  # Corrected OcrLanguage usage
            ocr_preset=OCRPreset.DOCUMENT,  # Corrected OCRPreset value
            max_depth=3,
            max_executions=100,
            strategy="FIFO",
            traversal_scope="domain",
        )
        options = loader.options
        assert options.api_key == "test_key"
        assert options.api_url == "http://test.com"
        assert options.format == "html"
        assert options.model == "ocr"
        assert options.encoding == "latin1"
        assert options.image is True
        assert options.table is False
        assert options.ocr_language == [OcrLanguage.ENGLISH]
        assert options.ocr_preset == OCRPreset.DOCUMENT
        assert options.max_depth == 3
        assert options.max_executions == 100
        assert options.strategy == "FIFO"
        assert options.traversal_scope == "domain"

    @pytest.mark.asyncio
    async def test_aload_markdown_format(self, mock_anyparser):
        mock_instance = mock_anyparser.return_value
        mock_instance.parse = AsyncMock(
            return_value="mocked markdown content"
        )  # AsyncMock
        loader = AnyparserLoader(file_path="test.pdf", format="markdown")
        docs = await loader.aload()
        mock_instance.parse.assert_called_once_with("test.pdf")
        assert len(docs) == 1
        assert docs[0].page_content == "mocked markdown content"
        assert docs[0].metadata["source"] == "test.pdf"
        assert docs[0].metadata["format"] == "markdown"

    @pytest.mark.asyncio
    async def test_aload_html_format(self, mock_anyparser):
        mock_instance = mock_anyparser.return_value
        mock_instance.parse = AsyncMock(return_value="mocked html content")  # AsyncMock
        loader = AnyparserLoader(file_path="test.pdf", format="html")
        docs = await loader.aload()
        mock_instance.parse.assert_called_once_with("test.pdf")
        assert len(docs) == 1
        assert docs[0].page_content == "mocked html content"
        assert docs[0].metadata["source"] == "test.pdf"
        assert docs[0].metadata["format"] == "html"

    @pytest.mark.asyncio
    async def test_aload_json_format_base_result(self, mock_anyparser):
        mock_instance = mock_anyparser.return_value
        mock_result = mock_anyparser_base_result(
            markdown="test markdown content",
        )
        mock_instance.parse = AsyncMock(return_value=[mock_result])  # AsyncMock
        loader = AnyparserLoader(file_path="test.pdf", format="json")
        docs = await loader.aload()
        mock_instance.parse.assert_called_once_with("test.pdf")
        assert len(docs) == 1
        doc = docs[0]
        assert doc.page_content == "test markdown content"
        assert doc.metadata["source"] == "test.pdf"
        assert doc.metadata["format"] == "json"
        assert doc.metadata["rid"] == "test_rid"
        assert doc.metadata["checksum"] == "test_checksum"
        assert doc.metadata["total_characters"] == 100
        assert doc.metadata["original_filename"] == "test.pdf"

    @pytest.mark.asyncio
    async def test_aload_json_format_pdf_result(self, mock_anyparser):
        mock_instance = mock_anyparser.return_value
        mock_result = mock_anyparser_pdf_result(
            items=[
                mock_anyparser_pdf_page_result(
                    markdown="page 1 content", page_number=1
                ),  # Using pdf page mock, page_number added
                mock_anyparser_pdf_page_result(
                    markdown="page 2 content", page_number=2
                ),  # Using pdf page mock, page_number added
            ],
        )
        mock_instance.parse = AsyncMock(return_value=[mock_result])  # AsyncMock
        loader = AnyparserLoader(file_path="test.pdf", format="json")
        docs = await loader.aload()
        mock_instance.parse.assert_called_once_with("test.pdf")
        assert len(docs) == 2
        doc1 = docs[0]
        assert doc1.page_content == "page 1 content"
        assert doc1.metadata["source"] == "test.pdf"
        assert doc1.metadata["format"] == "json"
        assert doc1.metadata["page_number"] == 1
        assert doc1.metadata["total_pages"] == 2
        assert (
            doc1.metadata["rid"] == "test_rid"
        )  # default from mock_anyparser_pdf_result
        assert (
            doc1.metadata["checksum"] == "test_checksum"
        )  # default from mock_anyparser_pdf_result
        assert (
            doc1.metadata["total_characters"] == 200
        )  # default from mock_anyparser_pdf_result
        assert (
            doc1.metadata["original_filename"] == "test.pdf"
        )  # default from mock_anyparser_pdf_result

        doc2 = docs[1]
        assert doc2.page_content == "page 2 content"
        assert doc2.metadata["page_number"] == 2

    @pytest.mark.asyncio
    async def test_aload_json_format_crawl_result(self, mock_anyparser):
        mock_instance = mock_anyparser.return_value
        mock_result = mock_anyparser_crawl_result(
            items=[
                mock_anyparser_url_result(
                    url="http://example.com/page1",
                    markdown="page 1 content",
                    title="Page 1",
                    status_message="OK",
                    status_code=200,
                    politeness_delay=100,
                    total_characters=100,
                    crawled_at="now",
                ),
                mock_anyparser_url_result(
                    url="http://example.com/page2",
                    markdown="page 2 content",
                    title="Page 2",
                    status_message="OK",
                    status_code=200,
                    politeness_delay=100,
                    total_characters=100,
                    crawled_at="now",
                ),
            ]
        )
        mock_instance.parse = AsyncMock(return_value=[mock_result])  # AsyncMock
        loader = AnyparserLoader(
            url="http://example.com", model="crawler", format="json"
        )
        docs = await loader.aload()
        mock_instance.parse.assert_called_once_with("http://example.com")
        assert len(docs) == 2
        doc1 = docs[0]
        assert doc1.page_content == "page 1 content"
        assert doc1.metadata["source"] == "http://example.com/page1"
        assert doc1.metadata["format"] == "json"
        assert doc1.metadata["page_number"] == 1
        assert doc1.metadata["total_pages"] == 2
        assert doc1.metadata["url"] == "http://example.com/page1"
        assert doc1.metadata["title"] == "Page 1"
        assert doc1.metadata["status_message"] == "OK"
        assert doc1.metadata["status_code"] == 200
        assert doc1.metadata["politeness_delay"] == 100
        assert doc1.metadata["total_characters"] == 100
        assert doc1.metadata["crawled_at"] == "now"

        doc2 = docs[1]
        assert doc2.page_content == "page 2 content"
        assert doc2.metadata["page_number"] == 2
        assert doc2.metadata["url"] == "http://example.com/page2"

    def test_load_sync(self, mock_anyparser):
        mock_instance = mock_anyparser.return_value
        mock_instance.parse = AsyncMock(
            return_value="mocked markdown content"
        )  # AsyncMock
        loader = AnyparserLoader(file_path="test.pdf", format="markdown")
        docs = loader.load()
        mock_instance.parse.assert_called_once_with("test.pdf")
        assert len(docs) == 1
        assert docs[0].page_content == "mocked markdown content"

    @pytest.mark.asyncio
    async def test_aload_parser_exception(self, mock_anyparser):
        mock_instance = mock_anyparser.return_value
        mock_instance.parse = AsyncMock(
            side_effect=Exception("Parser error")
        )  # AsyncMock
        loader = AnyparserLoader(file_path="test.pdf")
        with pytest.raises(ValueError) as excinfo:
            await loader.aload()
        assert "Error parsing document with Anyparser: Parser error" in str(
            excinfo.value
        )

    @pytest.mark.asyncio
    async def test_aload_invalid_markdown_html_result_type(self, mock_anyparser):
        mock_instance = mock_anyparser.return_value
        mock_instance.parse = AsyncMock(
            return_value=["not a string"]
        )  # AsyncMock, returns invalid type
        loader = AnyparserLoader(file_path="test.pdf", format="markdown")
        with pytest.raises(ValueError) as excinfo:
            await loader.aload()
        assert "Expected string for markdown format, got: <class 'list'>" in str(
            excinfo.value
        )

        loader_html = AnyparserLoader(file_path="test.pdf", format="html")
        with pytest.raises(ValueError) as excinfo:
            await loader_html.aload()
        assert "Expected string for html format, got: <class 'list'>" in str(
            excinfo.value
        )

    @pytest.mark.asyncio
    async def test_aload_invalid_json_result_type(self, mock_anyparser):
        mock_instance = mock_anyparser.return_value
        mock_instance.parse = AsyncMock(
            return_value="not a list"
        )  # AsyncMock, returns invalid type
        loader = AnyparserLoader(file_path="test.pdf", format="json")
        with pytest.raises(ValueError) as excinfo:
            await loader.aload()
        assert "Expected list for JSON format, got: <class 'str'>" in str(excinfo.value)

    def test__create_document_from_url(self):
        url_result = mock_anyparser_url_result(
            url="http://example.com/test",
            markdown="url content",
            title="URL Title",
            status_message="OK",
            status_code=200,
            politeness_delay=100,
            total_characters=100,
            crawled_at="now",
        )
        loader = AnyparserLoader(url="http://example.com", model="crawler")
        doc = loader._create_document_from_url(url_result)
        assert doc.page_content == "url content"
        assert doc.metadata["source"] == "http://example.com/test"
        assert doc.metadata["url"] == "http://example.com/test"
        assert doc.metadata["title"] == "URL Title"

        url_result_no_markdown = mock_anyparser_url_result(
            url="http://example.com/test",
            text="url text content",
            title="URL Title",
            status_message="OK",
            status_code=200,
            politeness_delay=100,
            total_characters=100,
            crawled_at="now",
        )
        doc_no_markdown = loader._create_document_from_url(url_result_no_markdown)
        assert doc_no_markdown.page_content == "url text content"

        url_result_empty = mock_anyparser_url_result(
            url="http://example.com/test",
            markdown=None,  # explicitly set markdown to None
            text=None,  # explicitly set text to None
            title="URL Title",
            status_message="OK",
            status_code=200,
            politeness_delay=100,
            total_characters=100,
            crawled_at="now",
        )
        doc_empty = loader._create_document_from_url(url_result_empty)
        assert doc_empty.page_content == ""

    def test__create_document_from_result_base(self):
        base_result = mock_anyparser_base_result(
            markdown="base content",
        )
        loader = AnyparserLoader(file_path="test.pdf")
        docs = loader._create_document_from_result(base_result)
        assert len(docs) == 1
        doc = docs[0]
        assert doc.page_content == "base content"
        assert doc.metadata["source"] == "test.pdf"
        assert doc.metadata["rid"] == "test_rid"

    def test__create_document_from_result_pdf(self):
        pdf_result = mock_anyparser_pdf_result(
            items=[
                mock_anyparser_pdf_page_result(
                    markdown="pdf page 1 content", page_number=1
                ),
                mock_anyparser_pdf_page_result(
                    markdown="pdf page 2 content", page_number=2
                ),
            ],
        )
        loader = AnyparserLoader(file_path="test.pdf")
        docs = loader._create_document_from_result(pdf_result)
        assert len(docs) == 2
        doc1 = docs[0]
        assert doc1.page_content == "pdf page 1 content"
        assert doc1.metadata["source"] == "test.pdf"
        assert doc1.metadata["page_number"] == 1
        assert doc1.metadata["total_pages"] == 2

        doc2 = docs[1]
        assert doc2.page_content == "pdf page 2 content"
        assert doc2.metadata["page_number"] == 2

    def test__create_document_from_result_crawl(self):
        crawl_result = mock_anyparser_crawl_result(
            items=[
                mock_anyparser_url_result(
                    url="http://example.com/page1", markdown="crawl page 1 content"
                ),
                mock_anyparser_url_result(
                    url="http://example.com/page2", markdown="crawl page 2 content"
                ),
            ]
        )
        loader = AnyparserLoader(url="http://example.com", model="crawler")
        docs = loader._create_document_from_result(crawl_result)
        assert len(docs) == 2
        doc1 = docs[0]
        assert doc1.page_content == "crawl page 1 content"
        assert doc1.metadata["source"] == "http://example.com/page1"
        assert doc1.metadata["page_number"] == 1
        assert doc1.metadata["total_pages"] == 2
        assert doc1.metadata["url"] == "http://example.com/page1"

        doc2 = docs[1]
        assert doc2.page_content == "crawl page 2 content"
        assert doc2.metadata["page_number"] == 2
        assert doc2.metadata["url"] == "http://example.com/page2"
