from langchain_community.vectorstores.chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter

import data

if __name__ == "__main__":
    data = data.Data(data.Data.XLSX_PATH)
    data.load_from_pickle()

    documents = []
    text_splitter = CharacterTextSplitter(
        separator='.', chunk_size=1000, chunk_overlap=200)

    for datapoint in data.yield_datapoints():
        documents.extend(text_splitter.split_documents(datapoint.load()))

    vectordb = Chroma.from_documents(
        documents,
        persist_directory='data/vectordb',
        embedding=OpenAIEmbeddings(model='text-embedding-3-small'),
    )
    vectordb.persist()
