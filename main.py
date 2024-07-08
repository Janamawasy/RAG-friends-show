from RAG import RAG

rag = RAG()
response = rag.submit_question("did Phoebe believe in evolution?")
# did Phoebe believe in evolution?
# What is moo point according to Joe?
# How many times did Ross Geller get married?
# what is the iconic song of  Phoebe Buffay, with lyrics?
# how was Phoebe's childhood?
# What is Chandler Bing's job?

print(response)