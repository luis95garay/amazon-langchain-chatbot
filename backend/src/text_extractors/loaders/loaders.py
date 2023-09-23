from bs4 import BeautifulSoup
from typing import Union, Any, List
from langchain.document_loaders import (
    WebBaseLoader, PyMuPDFLoader, TextLoader, Docx2txtLoader,
    PlaywrightURLLoader, SeleniumURLLoader, UnstructuredURLLoader
    )
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema.document import Document


class SingleWebLoader(WebBaseLoader):
    """
    This is a custom WebBaseLoader class for extracting text from a web page
    """
    def __init__(self, web_path: str):
        super().__init__(web_path=web_path, verify_ssl=False)

    def _scrape(self, url: str, parser: Union[str, None] = None) -> Any:
        """
        Scrapes the content of a web page and returns it as a
        BeautifulSoup object.

        Args:
            url (str): The URL of the web page to scrape.
            parser (Union[str, None], optional): The parser to use for
            BeautifulSoup. If None, it automatically determines the parser
            based on the URL's extension. Defaults to None.

        Returns:
            Any: A BeautifulSoup object containing the parsed HTML content
            of the web page.
        """

        if parser is None:
            if url.endswith(".xml"):
                parser = "xml"
            else:
                parser = self.default_parser

        self._check_parser(parser)

        html_doc = self.session.get(url, **self.requests_kwargs)
        if self.raise_for_status:
            html_doc.raise_for_status()
        html_doc.encoding = html_doc.apparent_encoding

        soup = BeautifulSoup(html_doc.text, parser)

        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.extract()

        # Remove list elements (ul and ol)
        elements_to_delete = ["ul", "ol", "li", "nav", "address",
                              "span", "svg", "footer"]
        for element in soup.find_all(elements_to_delete):
            element.extract()

        return soup

    def clean_load(
            self,
            chunk_size: int = 4000,
            chunk_overlap: int = 200
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

        for doc in documents:
            doc.page_content = doc.page_content \
                .replace("\n\n\n", "").replace("\t", "")
        return documents


# class PlaywrightWebLoader(PlaywrightURLLoader):
#     def __init__(self, web_path):
#         super().__init__([web_path])

#     def load(self) -> List[Document]:
#         """Load the specified URLs using Playwright and create Document instances.

#         Returns:
#             List[Document]: A list of Document instances with loaded content.
#         """
#         from playwright.sync_api import sync_playwright

#         docs: List[Document] = list()
#         excluded_selectors = ["ol", "nav", "address", "svg", "footer"]
#         with sync_playwright() as p:
#             browser = p.chromium.launch(headless=self.headless)
#             for url in self.urls:
#                 try:
#                     page = browser.new_page()
#                     response = page.goto(url)
#                     if response is None:
#                         raise ValueError(f"page.goto() returned None for url {url}")

#                     # text = self.evaluator.evaluate(page, browser, response)
#                     for selector in excluded_selectors:
#                         page.evaluate(f'document.querySelectorAll("{selector}").forEach(el => el.remove())')

#                     text = page.evaluate('() => document.body.innerText')
#                     metadata = {"source": url}
#                     docs.append(Document(page_content=text, metadata=metadata))
#                 except Exception as e:
#                     if self.continue_on_failure:
#                         print(f"Error fetching or processing {url}, exception: {e}")
#                     else:
#                         raise e
#             browser.close()
#         return docs
    
#     def clean_load(
#             self,
#             chunk_size: int = 4000,
#             chunk_overlap: int = 200
#             ) -> List[Document]:
#         """
#         Loads documents from a web page, cleans the content, and splits
#         into smaller chunks.

#         Returns:
#             List[Document]: A list of Document objects, each containing
#             cleaned and split content.
#         """
        
#         documents = self.load()
#         text_splitter = RecursiveCharacterTextSplitter(
#             chunk_size=chunk_size,
#             chunk_overlap=chunk_overlap,
#         )
#         documents = text_splitter.split_documents(documents)

#         return documents

class unstructured(UnstructuredURLLoader):
    def __init__(self, web_path):
        super().__init__([web_path], ssl_verify=False)

    def clean_load(
        self,
        chunk_size: int = 4000,
        chunk_overlap: int = 200
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

class SeleniumLoader(SeleniumURLLoader):
    def __init__(self, web_path):
        super().__init__([web_path])

    # def load(self) -> List[Document]:
    #     """Load the specified URLs using Selenium and create Document instances.

    #     Returns:
    #         List[Document]: A list of Document instances with loaded content.
    #     """
    #     print("before import")
    #     from unstructured.partition.html import partition_html
    #     print("after import")
    #     docs: List[Document] = list()
    #     driver = self._get_driver()

    #     for url in self.urls:
    #         try:
    #             driver.get(url)
    #             driver.implicitly_wait(10)
    #             body_element = driver.find_element_by_name('body')
    #             # Extract all visible text from the body element
    #             text = body_element.text
    #             # page_content = driver.page_source
    #             print("before partition")
    #             # elements = partition_html(text=page_content)
    #             print("after partition")
    #             # text = "\n\n".join([str(el) for el in elements])
    #             metadata = {"source": url}
    #             docs.append(Document(page_content=text, metadata=metadata))
    #         except Exception as e:
    #             if self.continue_on_failure:
    #                 print(f"Error fetching or processing {url}, exception: {e}")
    #             else:
    #                 raise e

    #     driver.quit()
    #     return docs

    def clean_load(
        self,
        chunk_size: int = 4000,
        chunk_overlap: int = 200
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


class PDFloader(PyMuPDFLoader):
    """
    Class for loading text from pdf files and split them in chunks
    """
    def clean_load(
            self,
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


class TXTloader(TextLoader):
    """
    Class for loading text from text files (.txt, .md) and split them in chunks
    """
    def clean_load(
            self,
            chunk_size: int = 4000,
            chunk_overlap: int = 200
            ) -> List[Document]:
        """
        Loads text from text file (.txt, .md), cleans the content, and splits
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


class Docxloader(Docx2txtLoader):
    """
    Class for loading text from docx files and split them in chunks
    """
    def clean_load(
            self,
            chunk_size: int = 4000,
            chunk_overlap: int = 200
            ) -> List[Document]:
        """
        Loads text from docx file, cleans the content, and splits
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


# class PDFloaderUnstructured(UnstructuredPDFLoader):
#     """
#     Class for loading text from pdf files and split them in chunks
#     """
#     def clean_load(self) -> List[Document]:
#         """
#         Loads text from pdf file, cleans the content, and splits
#         into smaller chunks.

#         Returns:
#             List[Document]: A list of Document objects, each containing
#             cleaned and split content.
#         """
#         documents = self.load()
#         new_documents = []
#         count = 0
#         new_text = ""
#         for doc in documents:
#             # print(len(doc.page_content)/4)
#             count += len(doc.page_content)/4
#             if count <= 1000:
#                 new_text += doc.page_content + "\n"
#             else:
#                 new_documents.append(
#                     Document(
#                         page_content=new_text,
#                         metadata=doc.metadata
#                     )
#                 )
#                 new_text = doc.page_content + "\n"
#                 count = 0

#         return new_documents


# class BaseDataFrameLoader(DataFrameLoader):
#     """
#     Custom base class for loading text from dataframes
#     with modified text extraction
#     """
#     def lazy_load(self) -> Iterator[Document]:
#         """Lazy load records from dataframe."""

#         for idx, row in self.data_frame.iterrows():
#             text = "\n".join([f"{key}: {values}"
#                               for key, values in row.to_dict().items()])
#             metadata = {"source": self.data_path, "row": idx}
#             yield Document(page_content=text, metadata=metadata)


# class ExcelLoader(BaseDataFrameLoader):
#     """
#     Class for loading text from excel files thought pandas dataframe
#     """
#     def __init__(self, data_path: str):
#         """Read excel file with pandas and init DataFrameLoader"""
#         self.data_path = data_path
#         data_frame = pd.read_excel(data_path)
#         super().__init__(data_frame)

#     def clean_load(
#             self,
#             chunk_size: int = 4000,
#             chunk_overlap: int = 200
#             ) -> List[Document]:
#         """Load dataframe into Documents"""
#         return self.load()
