# Código: app.py
# Autor: Rafhael Martins
# Descrição: Código principal do WebApp de Escala de Som e Projeção da ICm Taguatinga Centro.
# Histórico de versões:
# Data       | Versão     | Descrição
# 10/01/2026 | V1.0       | Versão inicial apenas com cadastro de disponibilidade.

# Importa Bibliotecas
import streamlit as st
from datetime import datetime
from zoneinfo import ZoneInfo
import time
from dotenv import load_dotenv
import os
from googlesheets import abrir_aba

# ----------------------
# CONFIGURAÇÃO
# ----------------------
# Carrega variáveis do .env
load_dotenv()
ABA_REF_ESCALA = st.secrets["ABA_REF_ESCALA"]
ABA_REF_DIAS_SEMANA = st.secrets["ABA_REF_DIAS_SEMANA"]
ABA_DISPONIBILIDADE = st.secrets["ABA_DISPONIBILIDADE"]

sheet_ref_escalas = abrir_aba(aba_planilha=ABA_REF_ESCALA)  # já retorna a aba de referência de escalas
sheet_ref_dias_semana = abrir_aba(aba_planilha=ABA_REF_DIAS_SEMANA)  # já retorna a aba de referência de dias da semana
sheet_disponibilidade = abrir_aba(aba_planilha=ABA_DISPONIBILIDADE)  # já retorna a aba de disponibilidades

# Configuração da página e ocultar menu lateral/rodapé
st.set_page_config(page_title="Escala de Som e Projeção", layout="centered")
st.markdown(
    """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True
)

# =============================
# Início do WebApp
# =============================
st.title("🔊 Escala de Som e Projeção 💻", text_alignment="center")
st.header("Cadastro de Disponibilidade")

st.write("Preencha abaixo suas informações e escolha os dias que possui disponibilidade.")

# =============================
# Busca Escalas Ativas
# =============================
@st.cache_data(ttl=300)
def carregar_ref_escalas():
    return sheet_ref_escalas.get_all_records()

dados_ref_escala = carregar_ref_escalas()

escalas_ativas = [
    row["ref_escala"]
    for row in dados_ref_escala
    if row["flg_situacao"].upper() == "ATIVO"
]

# =============================
# Busca Dias Semana
# =============================
@st.cache_data(ttl=300)
def carregar_dias_semana():
    return sheet_ref_dias_semana.get_all_records()

dias_ref = carregar_dias_semana()

dias_semana = {d["nm_dia"]: d["cd_dia"] for d in dias_ref}

# =============================
# Formulário
# =============================
with st.form("form_disponibilidade"):
    referencia = st.selectbox("Referência da escala:", escalas_ativas)
    
    nome = st.text_input("Primeiro nome:")

    st.write("Dias disponíveis:")
    # Dicionário para armazenar os checkboxes
    checks = {}
    for dia in dias_semana.keys():
        checks[dia] = st.checkbox(dia)
    
    submitted = st.form_submit_button("Enviar")

# =============================
# Resultado
# =============================
if submitted:
    # Filtra apenas os dias marcados
    disponibilidade = [dia for dia, marcado in checks.items() if marcado]

    # Veriica se preencheu todos os campos antes de enviar
    if not referencia or not nome or not disponibilidade:
        st.warning("**Atenção!**\n\nPor favor, preencha todos os campos antes de enviar.", icon="⚠️")
    elif "Não possuo disponibilidade" in disponibilidade and len(disponibilidade) > 1:
        st.error("Se você marcar **'Não possuo disponibilidade'**, não pode selecionar outros dias.", icon="❌")
    else:
        # Verifica se nome já foi inserido anteriormente

        # =============================
        # Busca disponibilidades já enviadas
        # =============================
        @st.cache_data(ttl=300)
        def carregar_disponibilidades():
            return sheet_disponibilidade.get_all_records()

        registros = carregar_disponibilidades()

        nome_normalizado = nome.strip().lower()
        ref_normalizada = referencia.strip().lower()

        ja_existe = any(
            r["ref_escala"].strip().lower() == ref_normalizada and
            r["nm_user"].strip().lower() == nome_normalizado
            for r in registros
        )

        if ja_existe:
            # st.warning("Você já enviou sua disponibilidade para este mês.\n\nSe precisar alterar, procure o responsável da equipe.", icon="⚠️")
            st.warning(
                    "**⚠️ Atenção!**\n\n"
                    "Você já enviou sua disponibilidade para este mês.\n\n"
                    "Se precisar alterar, procure o responsável da equipe."
                )

            if st.button("Nova resposta"):
                st.session_state.clear()
                st.rerun()
        else:
            st.success("Dados enviados com sucesso!", icon="✅")
            st.balloons()

            # Pega a data e hora atual para preencher campo data de criação
            dt_agora = datetime.now(ZoneInfo("America/Sao_Paulo")).strftime("%Y-%m-%d %H:%M:%S")

            # Converte nomes em códigos para normalização dos dados na planilha
            codigos_disponibilidade = [dias_semana[d] for d in disponibilidade]
            codigos_disponibilidade_str = ", ".join(codigos_disponibilidade)

            # adiciona linha na planilha
            sheet_disponibilidade.append_row([referencia, nome.strip().lower(), codigos_disponibilidade_str, dt_agora])
            
            # Limpa cache após salvar para ler os novos dados
            carregar_disponibilidades.clear()

            # Prepara a lista de dias em linhas separadas com marcadores
            dias_formatados = "\n".join(f"- {dia}" for dia in disponibilidade)

            # informa ao usuário no front-end os dados enviados
            st.info(
                f"**Dados cadastrados:**\n\n\n"
                f"**Referência:** {referencia}\n\n"
                f"**Nome:** {nome.strip().title()}\n\n"
                f"**Dias disponíveis:**\n{dias_formatados}",
                icon="ℹ️"
            )

            st.divider()

            # Reseta o WebApp para um novo envio/cadastro
            with st.spinner("A tela será reiniciada em 10 segundos...", show_time=False):
                time.sleep(10)

            st.session_state.clear()
            st.rerun()