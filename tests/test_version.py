"""
Test version information
"""

from anyparser_langchain import __version__


def test_version():
    """Test version is a string."""
    assert isinstance(__version__, str)
    assert __version__ == "0.0.2"
