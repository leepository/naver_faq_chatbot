import chromadb
import os
import pickle
import tiktoken

from chromadb.utils.embedding_functions.openai_embedding_function import OpenAIEmbeddingFunction
from dotenv import load_dotenv
from openai import OpenAI
from tqdm import tqdm

def load_pickle_file(file_path):
    """
    주어진 경로에서 pickle 파일을 로드
    :param file_path:
    :return:
    """
    try:
        with open(file_path, 'rb') as fp:
            data = pickle.load(fp)
        return data
    except Exception as ex:
        print(f"[Error] Cannot load pickle file : {ex}")
        return None

def get_or_create_chroma_collection(collection_name):
    """
    ChromaDB client와 collection을 조회 혹은 생성
    :param collection_name:
    :return:
    """
    client = chromadb.PersistentClient('./chromadb')

    embedding_function = OpenAIEmbeddingFunction(
        api_key=os.getenv('OPENAI_API_KEY', ""),
        model_name='text-embedding-3-large'
    )

    collection = client.get_or_create_collection(
        name='naver_faq',
        embedding_function=embedding_function,
        metadata={"hnsw:space": "cosine"}
    )

    return collection

def process_for_embedding(data):
    """
    데이터를 Chromadb에 적합한 형식으로 변환
    :param data:
    :return:
    """
    documents = []
    documents_append = documents.append
    metadatas = []
    metadatas_append = metadatas.append
    ids = []
    ids_append = ids.append

    for key, value in data.items():
        if isinstance(value, str):
            documents_append(value)
            metadatas_append({
                "source": "pickle",
                "key": str(key)
            })
            ids_append(f"id_{len(ids)}")

    return  documents, metadatas, ids

def embed_data(collection, documents, metadatas, ids, batch_size=100):
    """
    데이터를 Chromadb에 embedding
    :param collection:
    :param documents:
    :param metadatas:
    :param ids:
    :param batch_size:
    :return:
    """
    total_batches = (len(documents) + batch_size -1) // batch_size

    for i in tqdm(range(0, len(documents), batch_size), desc="임베딩 중", total=total_batches):
        batch_docs = documents[i:i+batch_size]
        batch_meta = metadatas[i:i+batch_size]
        batch_ids = ids[i:i+batch_size]

        # 빈 문서 필터링
        valid_indices = [j for j, doc in enumerate(batch_docs) if doc.strip()]
        if not valid_indices:
            continue

        filtered_docs = [batch_docs[j] for j in valid_indices]
        filtered_meta = [batch_meta[j] for j in valid_indices]
        filtered_ids = [batch_ids[j] for j in valid_indices]

        try:
            collection.add(
                documents=filtered_docs,
                metadatas=filtered_meta,
                ids=filtered_ids
            )

        except Exception as ex:
            print(f'일부 데이터 임베딩 실패: {ex}')


def split_document(full_text, chunk_size):
    encoder = tiktoken.encoding_for_model('gpt-4o')
    encoding = encoder.encode(full_text)
    total_token_count = len(encoding)
    text_list = []
    for i in range(0, total_token_count, chunk_size):
        chunk = encoding[1: 1+chunk_size]
        decoded = encoder.decode(chunk)
        text_list.append(decoded)
    return text_list

def run():
    load_dotenv()
    file_path = './final_result.pkl'
    chroma_client = chromadb.Client()
    collection_name = 'naver_faq'

    # Load pickle data
    data = load_pickle_file(file_path=file_path)

    # Get or create collection
    naver_faq_collection = get_or_create_chroma_collection(collection_name=collection_name)

    # Processing data
    documents, metas, ids = process_for_embedding(data=data)

    # Embedding to chromadb
    embed_data(
        collection=naver_faq_collection,
        documents=documents,
        metadatas=metas,
        ids=ids
    )

    print("##### TEST")
    # test
    query = "베스트 상품의 랭킹 기준은 무엇인가요?"

    retrieved_doc = naver_faq_collection.query(query_texts=query, n_results=5)
    openai_client = OpenAI()
    response = openai_client.chat.completions.create(
        model='gpt-4o',
        messages=[
            {
                'role': 'system',
                'content': f"""당신은 CS처리 전문가입니다. 아래 내용을 참고하여 질문에 답변하세요.
                
                {retrieved_doc['documents'][0]}"""
            },
            {
                'role': 'user',
                'content': query
            }
        ]
    )
    print("query : ", query)
    print("response : ", response.choices[0].message.content)

    print("##### Chromadb ready~!")

if __name__ == "__main__":
    run()
