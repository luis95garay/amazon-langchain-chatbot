from .loaders import (
    SingleWebLoader, PDFloader, TXTloader,
    Docxloader, unstructured, SeleniumLoader
)


MAPPED_LOADERS_METHODS = {
    "web": SingleWebLoader,
    "uweb": unstructured,
    "sweb": SeleniumLoader,
    "pdf": PDFloader,
    "txt": TXTloader,
    "docx": Docxloader
}
