from typing import List, Iterator, Optional
import re
import os
import json
from datetime import date

import pandas as pd
import sharepy
from bs4 import BeautifulSoup
from langchain.document_loaders import (
    PyMuPDFLoader, TextLoader, Docx2txtLoader,
    DataFrameLoader, CSVLoader
    )
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema.document import Document
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class BaseLoader:
    def clean_load(
            self,
            chunk_size: int = 4000,
            chunk_overlap: int = 200,
            mode: Optional[str] = None,
            from_date: Optional[date] = None
            ) -> List[Document]:
        """
        Loads documents from a web page, cleans the content, and splits
        into smaller chunks.

        Returns:
            List[Document]: A list of Document objects, each containing
            cleaned and split content.
        """
        documents = self.load()
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
            chunk_size: int = 4000,
            chunk_overlap: int = 200,
            mode: Optional[str] = None,
            from_date: Optional[date] = None
            ) -> List[Document]:
        """
        Loads text from pdf file, cleans the content, and splits
        into smaller chunks.

        Returns:
            List[Document]: A list of Document objects, each containing
            cleaned and split content.
        """
        documents = self.load()

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


class ExcelLoader(DataFrameLoader, BaseLoader):
    """
    Class for loading text from excel files thought pandas dataframe
    """
    def __init__(self, data_path: str):
        """Read excel file with pandas and init DataFrameLoader"""
        self.data_path = data_path
        data_frame = pd.read_excel(data_path)
        super().__init__(data_frame)

    def lazy_load(self) -> Iterator[Document]:
        """Lazy load records from dataframe."""

        for idx, row in self.data_frame.iterrows():
            text = "\n".join([f"{key}: {values}"
                              for key, values in row.to_dict().items()])
            metadata = {"source": self.data_path, "row": idx}
            yield Document(page_content=text, metadata=metadata)


class CSVCloader(CSVLoader, BaseLoader):
    """
    Class for loading text from csv files
    """
    def __init__(self, file_path: str):
        super().__init__(file_path)


class sharepointloader:
    """
    Class for loading text from sharepoint sites
    """
    def __init__(self, url: str):
        self.url = url
        self.session = sharepy.connect(
            "asistenciaglobal.sharepoint.com",
            username=os.getenv("SHAREPOINT_USER"),
            password=os.getenv("SHAREPOINT_SECRET")
        )

    @classmethod
    def get_text(cls, html):
        """
        Extracts text from HTML content.

        Args:
            html (str): HTML content.

        Returns:
            str: Extracted text.
        """
        soup = BeautifulSoup(html, 'html.parser')

        # Extract text from the HTML
        return soup.get_text()

    def extract_text(self, url):
        """
        Extracts text from a SharePoint page.

        Args:
            url (str): URL of the SharePoint page.

        Returns:
            str: Extracted text from the page.
        """
        r = self.session.get(url)
        response = json.loads(r.text)

        # Parse the HTML content
        response_str = f"INFORMACION SOBRE {response['item']['Title']}\n\n"

        for val in json.loads(response['page']['Content']['CanvasContent1']):

            if 'zoneGroupMetadata' in val and 'innerHTML' in val:
                if 'displayName' in val['zoneGroupMetadata']:
                    response_str += \
                        val['zoneGroupMetadata']['displayName'] + "\n\n"
            if 'innerHTML' in val:
                response_str += self.get_text(val['innerHTML']) + "\n\n"

        return response_str

    def clean_load(
        self,
        chunk_size: Optional[int] = 5000,
        chunk_overlap: Optional[int] = 200,
        mode: Optional[str] = "single",
        from_date: date = date.today()
    ):
        """
        Cleans and loads SharePoint content into documents.

        Args:
            chunk_size (int, optional): Chunk size for loading content.
            chunk_overlap (int, optional): Chunk overlap for loading content.
            mode (str, optional): Load mode ('single' or 'consolidated').
            from_date (date, optional): Starting date for content filtering.

        Returns:
            list of Document: List of Document objects containing cleaned
            content.
        """

        if mode == "single":
            return [
                Document(
                    page_content=self.extract_text(self.url),
                    metadata={"source": self.url}
                )
            ]

        elif mode == "consolidated":
            consolidated_url = \
                f"{self.url}/_api/web/GetFolderByServerRelativeUrl('SitePages')/Files"
            r = self.session.get(consolidated_url)
            pages_list = json.loads(r.text)['d']['results']

            documents = []
            for page in pages_list:
                current_date = date.fromisoformat(
                    page['TimeLastModified'][:10]
                    )
                if current_date > from_date:
                    complete_url = f"{self.url}/SitePages/{page['Name']}"
                    try:
                        url_content = self.extract_text(complete_url)
                        documents.append(Document(
                            page_content=url_content,
                            metadata={"source": complete_url}
                            )
                        )
                    except TypeError:
                        print(complete_url)
                        continue
                    except json.decoder.JSONDecodeError:
                        print(complete_url)
                        continue

            return documents
