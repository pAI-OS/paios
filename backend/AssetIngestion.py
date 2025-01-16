from sklearn.metrics.pairwise import cosine_similarity
# from langchain_community.embeddings import HuggingFaceEmbeddings
from llama_index.readers.file import PyMuPDFReader
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.schema import TextNode
import pymupdf
from llama_index.core import Document, VectorStoreIndex
#from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from langchain.embeddings import HuggingFaceEmbeddings
from llama_index.embeddings.langchain import LangchainEmbedding
# build index
# index = VectorStoreIndex.from_documents(documents)

# def write_pdf_into_txt(pdf_filename="test_chunking.pdf", txt_filename="test_chunking.txt"):
#     doc = pymupdf.open(str(pdf_filename))  # open a document
#     out = open(str(txt_filename), "wb")  # create a text output
#     for page in doc:  # iterate the document pages
#         text = page.get_text().encode("utf8")  # get plain text (is in UTF-8)
#         out.write(text)  # write text of page
#         out.write(bytes((12,)))  # write page delimiter (form feed 0x0C)
#     out.close()
#
#
# def read_txt_file(filename='test_chunking.txt'):
#     with open(filename, encoding="utf8") as file:
#         essay = file.read()
#     return essay


# create chunks from PDF
def chunk_pdf():
    loader = PyMuPDFReader()
    documents = loader.load(file_path="test_chunking.pdf")

    text_parser = SentenceSplitter(
        chunk_size=1024,
        # separator=" ",
    )
    text_chunks = []
    doc_idxs = []
    for doc_idx, doc in enumerate(documents):
        cur_text_chunks = text_parser.split_text(doc.text)
        text_chunks.extend(cur_text_chunks)
        # for node metadata
        doc_idxs.extend([doc_idx] * len(cur_text_chunks))
    return text_chunks, doc_idxs, documents


# building an index by creating for each chunk of text a Textnode
def create_nodes(text_chunks,documents,doc_idxs):
    nodes = []
    for idx, text_chunk in enumerate(text_chunks):
        node = TextNode(
            text=text_chunk,
        )
        src_doc = documents[doc_idxs[idx]]
        node.metadata = src_doc.metadata
        nodes.append(node)
    return nodes




def get_nodes_embedding(nodes):
    for node in nodes:
        node_embedding = embed_model.get_text_embedding(
            node.get_content(metadata_mode="all")
        )
        node.embedding = node_embedding
    return nodes


# write_pdf_into_txt()


def calculate_cosine_distances(embedding_parent, embedding_child):
    similarity = cosine_similarity(embedding_parent, embedding_child)[0][0]
    return similarity


def compute_child_nodes_similarity(nodes):
    for node in nodes:
        node_embedding = embed_model.get_text_embedding(
            node.get_content(metadata_mode="all")
        )

        for idx, child_node in enumerate(node.child_nodes):
            child_embedding = embed_model.get_text_embedding(
                child_node.get_content(metadata_mode="all")
            )
            similarity = calculate_cosine_distances(node_embedding, child_embedding)
            # print similarities
            print("similarity between node"+str(node.node_id)+" and node "+str(child_node.node_id)+" is "+similarity)
            node.node_info.update({"related_node_similarity " + str(idx): float(similarity)})
    return nodes


if __name__ == "__main__":
    #embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
    lc_embed_model  = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en-v1.5")
    embed_model = LangchainEmbedding(lc_embed_model)
    text_chunks, doc_idx, documents = chunk_pdf()
    nodes = create_nodes(text_chunks,documents,doc_idx)
    nodes = get_nodes_embedding(nodes)
    compute_child_nodes_similarity(nodes)
