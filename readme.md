# Naver smartstore FAQ Chatbot
Naver의 스마트 스토어 FAQ 기반의 챗봇. FAQ 기반의 내용으로 사용자의 질문에 답변한다. 챗봇은 다음과 같은 기준으로 작성되었다.
 - FAQ 기반의 정보를 바탕으로 RAG를 활용하여 답변을 제공한다.
 - 사용자의 이전 질문과 상황을 토대로 적절한 내요으로 답변을 제공한다.
 - 사용자의 질문에 대한 답변 이후에 사용자가 궁금해할만한 다른 내용의 질문을 예시로 제공한다.
 - 관련이 없는 질문에는 답변하지 않는다. 
 - LLM과 Embbeding 모델은 OpenAI를 사용한다.
 - LangChain 등과 같은 LLM 오케스트레이션 프레임워크는 사용하지 않는다.

## Requirements
Naver smartstore FAQ Chatbot 구동을 위해서는 다음과 같은 정보가 필요하다.
 - OPENAI_API_KEY
 상기 내용은 .env 파일로 저장한다. 
 

## Packages

게시판 구현에 사용된 python version은 3.11.9이며 사용되는 python package는 다음과 같다.
      
	chromadb==0.6.3  
	openai==1.68.2  
	tiktoken==0.9.0  
	dotenv==0.9.9  
	fastapi==0.115.12  
	dependency-injector==4.46.0  
	email-validator==2.2.0  
	ujson==5.10.0  
	streamlit==1.43.2  
	sseclient==0.0.27  
	pytest==8.3.5  
	pytest-mock==3.14.0  
	httpx==0.28.1 

## Prepare data
RAG를 활용하기 위한 Vector DB는 Chroma를 사용하며, Application 구동 전에 VectorDB에 다음과 같이 데이터를 임베딩하여 저장한다. (Virtualenv 활성화 필수)

    $ (.venv) python prepare_data.py
데이터가 VectorDB에 정상적으로 저장되면 Project root directory 하단에 'chromadb' 라는 디렉토리가 생성된다. VectorDB에 데이터를 적재하는 작업은 Application 구동 전 1회만 진행하면 되며, 한번 저장된 데이터는 'chromadb' 디렉토리를 삭제하지 않는 이상 지속된다. (두번째 application 구동부터는 데이터를 적재할 필요가 없다.)

## Run application

API Server는 다음과 같이 구동한다. (Virtualenv 활성화 필수)

    $ (.venv) python run_server.py

테스트용 Client는 다음과 같이 구동한다. (Virtualenv 활성화 필수)

    $ (.venv) streamlit run client.py

 - API Server를 구동시켜 놓은 상태에서 다른 터미널을 열어 구동하도록 한다. 
