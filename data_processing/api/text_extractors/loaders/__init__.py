from .loaders import (
    PDFloader, TXTloader,
    Docxloader, SeleniumLoader, sharepointloader,
    ExcelLoader, CSVCloader
)


MAPPED_LOADERS_METHODS = {
    "web": SeleniumLoader,
    "sharepoint": sharepointloader,
    "pdf": PDFloader,
    "txt": TXTloader,
    "docx": Docxloader,
    "xlsx": ExcelLoader,
    "csv": CSVCloader
}
