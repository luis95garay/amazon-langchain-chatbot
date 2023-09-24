from .loaders import (
    PDFloader, TXTloader,
    Docxloader, SeleniumLoader,
    MarkdwnLoader
)


MAPPED_LOADERS_METHODS = {
    "web": SeleniumLoader,
    "pdf": PDFloader,
    "txt": TXTloader,
    "docx": Docxloader,
    "md": MarkdwnLoader
}
