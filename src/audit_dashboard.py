import streamlit as st
import pandas as pd
import sqlite3
import os
import json
from dotenv import load_dotenv

# Setup page configuration
st.set_page_config(page_title="ROA Chat Audit Log", page_icon="🕵️", layout="wide")
st.title("🕵️ ROA Chat Audit Dashboard")
st.markdown("Bem-vindo ao painel de auditoria do ROA. Aqui você pode verificar o histórico de conversas, métricas de respostas e modelos de linguagem utilizados.")

# Localizar o banco de dados (dentro de src/ conforme solicitado)
DB_PATH = os.path.join(os.path.dirname(__file__), "test.db")

st.sidebar.info(f"Conectado ao banco: `{os.path.basename(DB_PATH)}`")

@st.cache_data(ttl=5)
def load_data(query):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# Buscar resumos gerais
try: # Verifica se tudo existe
    users_df = load_data("SELECT id, name, email, role FROM users")
    conversations_df = load_data("SELECT id, user_id, title, created_at FROM conversations")
    messages_df = load_data("SELECT id, conversation_id, role, content, model_used, metrics, created_at FROM messages")
except Exception as e:
    st.error(f"Erro ao ler banco de dados: {e}")
    st.stop()

# --- ABA DE MÉTRICAS GERAIS ---
st.header("KPIs Principais")
col1, col2, col3, col4 = st.columns(4)

col1.metric("Usuários Registrados", len(users_df))
col2.metric("Total de Conversas", len(conversations_df))
col3.metric("Mensagens Trocadas", len(messages_df))

# Agrupar uso de modelos
if len(messages_df) > 0 and 'model_used' in messages_df.columns:
    model_count = messages_df[messages_df['model_used'].notnull()]['model_used'].value_counts()
    most_used = model_count.index[0] if len(model_count) > 0 else "Nenhum"
    col4.metric("Modelo Favorito", most_used)
else:
    col4.metric("Modelo Favorito", "N/A")


st.divider()

# --- NAVEGAÇÃO ENTRE CONVERSAS ---
st.header("Histórico de Conversas")

if len(conversations_df) > 0:
    # Sidebar Filters
    st.sidebar.header("Filtros")
    selected_user = st.sidebar.selectbox("Filtrar por Usuário", ["Todos"] + list(users_df['name'].unique()))
    
    # Merge for easier filtering (how='left' ensures conversations are kept even if user record is missing)
    merged_convs = conversations_df.merge(users_df, left_on="user_id", right_on="id", how="left", suffixes=('_conv', '_user'))
    
    # Preencher nomes de usuários nulos (ex: vini_mock_id)
    merged_convs['name'] = merged_convs['name'].fillna("Usuário Mock")
    
    if selected_user != "Todos":
        merged_convs = merged_convs[merged_convs['name'] == selected_user]
        
    if len(merged_convs) == 0:
        st.info("Nenhuma conversa encontrada para o filtro selecionado.")
    else:
        # User selects a conversation
        conv_options = {row['id_conv']: f"{row['title']} (por {row['name']})" for _, row in merged_convs.iterrows()}
        selected_conv_id = st.selectbox("Selecione a Conversa", list(conv_options.keys()), format_func=lambda x: conv_options[x])
        
        # Obter mensagens daquela conversa
        conv_msgs = messages_df[messages_df['conversation_id'] == selected_conv_id].sort_values(by="created_at")
        
        st.subheader(f"Mensagens na conversa: {conv_options[selected_conv_id]}")
        
        for _, msg in conv_msgs.iterrows():
            with st.container():
                if msg['role'] == 'user':
                    st.chat_message("user").markdown(msg['content'])
                else:
                    with st.chat_message("assistant"):
                        st.markdown(msg['content'])
                        
                        # Show technical metrics for the bot's response
                        metrics_str = msg.get('metrics')
                        model_str = msg.get('model_used')
                        
                        bot_tags = []
                        if model_str:
                            bot_tags.append(f"🧠 **Model**: `{model_str}`")
                            
                        if metrics_str:
                            try:
                                m = json.loads(metrics_str)
                                bot_tags.append(f"📏 **Lens**: `{m.get('response_length', 0)} chars`")
                                bot_tags.append(f"📚 **Context Length**: `{m.get('history_length', 0)} msgs`")
                            except:
                                bot_tags.append("📊 Métricas não estruturadas.")
                                
                        if bot_tags:
                            st.caption(" | ".join(bot_tags))
else:
    st.info("O banco de dados de conversações ainda está vazio. Faça uma pergunta no chatbot e recarregue a página.")
