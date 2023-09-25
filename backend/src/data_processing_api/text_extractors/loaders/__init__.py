from .loaders import (
    PDFloader, TXTloader,
    Docxloader, MarkdwnLoader
)


MAPPED_LOADERS_METHODS = {
    "pdf": PDFloader,
    "txt": TXTloader,
    "docx": Docxloader,
    "md": MarkdwnLoader
}
