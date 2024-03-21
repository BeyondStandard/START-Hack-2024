import data

if __name__ == '__main__':
    data = data.Data(data.Data.XLSX_PATH)
    # data.load_from_pickle()
    #
    # documents = []
    # text_splitter = CharacterTextSplitter(
    #     separator='.', chunk_size=1000, chunk_overlap=200)
    #
    # for datapoint in data.yield_datapoints():
    #     documents.extend(text_splitter.split_documents(datapoint.load()))
    #
    # vectordb = Chroma.from_documents(
    #     documents,
    #     persist_directory='./vectordb',
    #     embedding=OpenAIEmbeddings(model='text-embedding-3-small'),
    # )
    # vectordb.persist()

    # chain = load_qa_chain(llm=OpenAI(), verbose=True)
    # query = 'Was muss ich beachten wenn ich Baugesuch einreichen will?'
    # response = chain.invoke({"input_documents": document.load(), "question": query})
    # print(response["output_text"])
