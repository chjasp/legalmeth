from langchain.memory import ConversationTokenBufferMemory


memory = ConversationTokenBufferMemory(llm=llm, memory_key="chat_history", return_messages=True, input_key='question', max_token_limit=1000)
question_generator = LLMChain(llm=llm, prompt=CONDENSE_QUESTION_PROMPT, verbose=True)
answer_chain = load_qa_with_sources_chain(llm, chain_type="stuff", verbose=True,prompt=chat_prompt)

chain = ConversationalRetrievalChain(
            retriever=reranker,
            question_generator=question_generator,
            combine_docs_chain=answer_chain,
            verbose=True,
            memory=memory,
            rephrase_question=False
)