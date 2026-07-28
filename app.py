import streamlit as st
from chatbot import responder

st.set_page_config(
    page_title="Vida Plena AI",
    page_icon="assets/favicon.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>

.block-container{
    max-width:1100px;
    padding-top:2rem;
}

[data-testid="stHeader"]{
    background:transparent;
}

section[data-testid="stSidebar"]{
    background:#1A102C;
}

.sidebar-title{
    font-size:1.4rem;
    font-weight:700;
    color:white;
}

.small{
    color:#B9B5C8;
    font-size:.95rem;
}

.hero h1{
    font-size:3rem;
    margin-bottom:0;
    color:white;
}

.hero p{
    color:#B9B5C8;
    font-size:1.05rem;
}

.stButton>button{
    width:100%;
    border:none;
    border-radius:12px;
    background:#7C3AED;
    color:white;
    font-weight:600;
}

.stButton>button:hover{
    background:#8B5CF6;
}

</style>
""", unsafe_allow_html=True)



# SIDEBAR

with st.sidebar:

    st.image("assets/favicon.png", width=70)

    st.markdown(
        '<div class="sidebar-title">Vida Plena AI</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="small">Assistente Corporativo</div>',
        unsafe_allow_html=True
    )

    st.divider()

    st.subheader("📚 Áreas")

    st.markdown("""
👥 Recursos Humanos

💰 Financeiro

🛡️ Compliance

💻 TI

📈 Comercial

📣 Comunicação
""")

    st.divider()

    st.subheader("⚙️ Tecnologias")

    st.markdown("""
- Gemini 2.5 Flash
- Google Embeddings
- FAISS
- LangChain
- Streamlit
""")

    st.divider()

    if st.button("🗑️ Limpar conversa", use_container_width=True):
        st.session_state.messages = [{
            "role": "assistant",
            "content": (
                "Olá! Sou o **Vida Plena AI**.\n\n"
                "Posso ajudar com dúvidas sobre políticas, "
                "procedimentos e documentos internos da empresa.\n\n"
                "Como posso ajudar hoje?"
            )
        }]
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role":"assistant",
        "content":"Olá! Sou o **Vida Plena AI**.\n\nPosso responder perguntas sobre Recursos Humanos, Financeiro, TI, Compliance, Comercial e Comunicação.\n\nComo posso ajudar hoje?"
    }]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Pergunte sobre políticas, processos ou procedimentos..."):
    st.session_state.messages.append({"role":"user","content":prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Analisando a documentação..."):
            try:
                resposta = responder(prompt)
            except Exception:
                resposta = ("Desculpe, ocorreu um problema ao consultar a documentação interna. "
                            "Tente novamente em alguns instantes.")
            st.markdown(resposta)

    st.session_state.messages.append(
        {"role":"assistant","content":resposta}
    )
