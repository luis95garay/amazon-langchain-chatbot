from bs4 import BeautifulSoup
from typing import List
from langchain.document_loaders import (
    PyMuPDFLoader, TextLoader, Docx2txtLoader, UnstructuredMarkdownLoader
    )
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema.document import Document
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re


class BaseLoader:
    def clean_load(
            self,
            documents,
            chunk_size: int = 4000,
            chunk_overlap: int = 200,
            is_folder: bool = False,
            ) -> List[Document]:
        """
        Loads documents from a web page, cleans the content, and splits
        into smaller chunks.

        Returns:
            List[Document]: A list of Document objects, each containing
            cleaned and split content.
        """

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )
        documents = text_splitter.split_documents(documents)

        return documents


class SeleniumLoader(BaseLoader):
    def __init__(self, web_path):
        self.web_path = web_path
        # Set up Chrome WebDriver in headless mode
        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless")  # Enable headless mode
        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--disable-dev-shm-usage')

    def load(self):
        driver = webdriver.Chrome(options=self.chrome_options)

        # Open the website
        driver.get(self.web_path)

        # Get the page source using Selenium
        page_source = driver.page_source

        # Parse the page source with BeautifulSoup
        soup = BeautifulSoup(page_source, 'html.parser')

        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.extract()

        # Remove list elements (ul and ol)
        elements_to_delete = ["nav", "address", "footer", "form",
                              "table", "tr", "td", "th", "video"]

        for element in soup.find_all(elements_to_delete):
            element.extract()

        # Regular expression pattern to match class names containing "hidden"
        pattern = re.compile(r"(.*hidden.*)")

        # Find and remove elements with matching class names
        for element in soup.find_all(class_=pattern):
            element.extract()

        # Add a newline character after each <h3> tag
        for h3 in soup.find_all("h3"):
            h3.insert_after("\n")

        text = soup.get_text().replace("\n\n\n\n", "\n")

        # Close the web driver
        driver.close()

        yield Document(page_content=text)


class PDFloader(PyMuPDFLoader, BaseLoader):
    """
    Class for loading text from pdf files and split them in chunks
    """
    def clean_load(
            self,
            documents: Document,
            chunk_size: int = 4000,
            chunk_overlap: int = 200
            ) -> List[Document]:
        """
        Loads text from pdf file, cleans the content, and splits
        into smaller chunks.

        Returns:
            List[Document]: A list of Document objects, each containing
            cleaned and split content.
        """

        documents = [
            Document(
                page_content="".join([doc.page_content for doc in documents]),
                metadata=documents[0].metadata
            )
        ]

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )
        documents = text_splitter.split_documents(documents)

        return documents


class TXTloader(TextLoader, BaseLoader):
    """
    Class for loading text from text files (.txt, .md) and split them in chunks
    """
    def __init__(self, file_path: str):
        super().__init__(file_path, encoding="utf-8")


class Docxloader(Docx2txtLoader, BaseLoader):
    """
    Class for loading text from docx files and split them in chunks
    """
    def __init__(self, file_path: str):
        super().__init__(file_path)



class MarkdwnLoader(UnstructuredMarkdownLoader, BaseLoader):
    """
    Class for loading text from md files and split them in chunks
    """
    def __init__(self, file_path: str):
        super().__init__(file_path, mode='single')