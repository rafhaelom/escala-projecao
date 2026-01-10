# Código: googlesheets.py
# Autor: Rafhael Martins
# Descrição: Código para autenticação e interação com a planilha de Escala de Som e Projeção da ICM Taguatinga Centro.
# Histórico de versões:
# Data       | Versão     | Descrição
# 10/01/2026 | V1.0       | Versão inicial com autenticação no Google Cloud e leitura, escrita no google sheets.

# Importa Bibliotecas
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv
import os

# ----------------------
# CONFIGURAÇÃO
# ----------------------
# Carrega variáveis do .env
load_dotenv()

CREDENCIAIS_ARQUIVO = os.getenv("CREDENCIAIS_ARQUIVO")
SPREADSHEET_KEY = os.getenv("SPREADSHEET_KEY")

# ----------------------
# AUTENTICAÇÃO
# ----------------------
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# Cria o cliente autenticado
credentials = Credentials.from_service_account_file(
    CREDENCIAIS_ARQUIVO,
    scopes=SCOPES
)
client = gspread.authorize(credentials)

# ----------------------
# FUNÇÃO PARA ABRIR ABA
# ----------------------
def abrir_aba(aba_planilha):
    """
    Retorna a aba de usuários da planilha
    """
    try:
        sheet = client.open_by_key(SPREADSHEET_KEY).worksheet(aba_planilha)
        return sheet
    except Exception as e:
        print("Erro ao abrir aba:", e)
        return None