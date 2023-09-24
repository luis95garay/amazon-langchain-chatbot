from pathlib import Path
import pickle

from langchain.document_loaders import UnstructuredMarkdownLoader
from langchain.text_splitter import MarkdownTextSplitter
from dotenv import load_dotenv
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores.faiss import FAISS
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.chains.chat_vector_db.prompts import QA_PROMPT


load_dotenv("credentials.env")
markdown_path = Path('data/sagemaker_documentation')

data = []
for idx, file in enumerate(markdown_path.glob('*.md')):
    print(idx)
    loader = UnstructuredMarkdownLoader(str(file), mode='single')
    data += loader.load()
    

text_splitter = MarkdownTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
)
data = text_splitter.split_documents(data)
print(len(data))
# for val in data:
#     print(val.page_content)

embeddings = OpenAIEmbeddings()
current_vectorstore = FAISS.from_documents(data, embeddings)

# Save vectorstore
with open("vectorstore.pkl", "wb") as f:
    pickle.dump(current_vectorstore, f)


streaming_llm = ChatOpenAI(
    model_name="gpt-3.5-turbo",
    verbose=False
)

qa = RetrievalQA.from_llm(
    streaming_llm,
    retriever=current_vectorstore.as_retriever(k=3),
    verbose=False,
    prompt=QA_PROMPT
)

print(qa.run("What do you know about AWS regions? is AWS SageMaker available on them?"))
