import streamlit as st
import pandas as pd
import requests
from dotenv import load_dotenv
import os
from pandasai.llm.openai import OpenAI
from pandasai import PandasAI
import re

# Carrega as variáveis de ambiente do arquivo .env para o script.
load_dotenv()

# Obtém a chave de API da OpenAI a partir das variáveis de ambiente.
openai_api_key = os.getenv("OPENAI_API_KEY")

def chat_with_data(df, prompt):
    
    # Lista de expressões que indicam uma pergunta sobre o nome do assistente
    nome_keywords = ["nome", "quem", "com quem", "falo", "estou falando", "estou conversando", "se chama"]
    
    # Verifica se alguma das palavras-chave está na pergunta
    if any(keyword in prompt.lower() for keyword in nome_keywords):
        # Responde diretamente com o nome do assistente se a pergunta estiver relacionada
        return "Olá, meu nome é Carlos! Sou a Inteligência Artificial da Unimarka, Como posso te ajudar?"
    
    if df.empty or df.isnull().all().any():
        return "Não há dados suficientes para responder à consulta."
    try:
        prompt_in_portuguese = "Responda em português: " + prompt
        llm = OpenAI(api_token=openai_api_key)
        pandas_ai = PandasAI(llm)
        result = pandas_ai.run(df, prompt=prompt_in_portuguese)
        result_str = str(result).strip()
        if result_str == 'nan' or result_str.lower() == 'none':
            return "Não foi possível encontrar uma resposta adequada com os dados fornecidos."
        if result_str == "":
            return "Desculpe, não consegui encontrar uma resposta."
        
        # Novo código para detectar URLs e torná-los clicáveis
        url_pattern = r'(https?://[^\s]+)'
        result_str = re.sub(url_pattern, r'<a href="\1" target="_blank">\1</a>', result_str)
        
        return result_str
    except Exception as e:
        return f"Ocorreu um erro ao processar a consulta: {str(e)}"

def fetch_data(api_url1, api_url2):
    dfs = []
    for api_url in [api_url1, api_url2]:
        try:
            response = requests.get(api_url)
            response.raise_for_status()
            data = response.json().get('dados')
            if data:
                dfs.append(pd.DataFrame(data))
        except requests.RequestException:
            pass
    return dfs

def display_chat_message(sender, message):
    if sender == "Você":
        st.markdown(f"<div style='text-align: right; border-radius: 25px; background-color: #DCF8C6; padding: 10px; margin: 10px 0px 10px 40%; display: inline-block; max-width: 60%;'>{message}</div>", unsafe_allow_html=True)
    else:  # Mensagens do Siad.AI
        st.markdown(f"""<div style='text-align: left; border-radius: 25px; background-color: #ECECEC; padding: 10px; margin: 10px 40% 10px 0px; display: flex; align-items: center; max-width: 60%;'>
                            <img src='https://lifeapps.com.br/wp-content/uploads/2021/07/unimarka.png' style='width: 40px; height: 40px; border-radius: 50%; margin-right: 10px;'>
                            {message}
                        </div>""", unsafe_allow_html=True)

def on_text_enter():
    input_text = st.session_state.query_input
    if not data_list:
        st.session_state.conversation.append(("Você", input_text))
        st.session_state.conversation.append(("Siad.AI", "Não foi possível carregar dados das APIs. Tente novamente mais tarde."))
    else:
        combined_data = pd.concat(data_list, ignore_index=True)
        response = chat_with_data(combined_data, input_text)
        st.session_state.conversation.append(("Você", input_text))
        st.session_state.conversation.append(("Siad.AI", response))
    # Limpa o campo de entrada após o envio
    st.session_state.query_input = ""

# Configuração da página do Streamlit
st.set_page_config(page_title="Siad.AI Chat", layout='wide')
st.title("Bem-vindo ao Siad.AI Chat")

# URLs das APIs
api_url1 = "https://fjinfor.ddns.net/fvendas/api/api_sitpedido.php?funcao=get_sitpedido&cliente=1010"
api_url2 = "https://fjinfor.ddns.net/fvendas/api/api_sit_boleto.php?funcao=get_sitboleto&cliente=1010"

# Carregando dados das APIs
data_list = fetch_data(api_url1, api_url2)

# Armazenando conversa
if 'conversation' not in st.session_state:
    st.session_state.conversation = []

# Interface de chat
st.subheader("Como posso ajudar?")
# A função on_change é chamada automaticamente ao pressionar Enter ou ao alterar o texto
st.text_input("Digite sua consulta aqui...", key="query_input", on_change=on_text_enter, args=())

# Exibindo conversa
for sender, message in st.session_state.conversation:
    display_chat_message(sender, message)
