import pandas as pd
import yaml
import re

def carregar_config_mapeamento(caminho_yaml: str = "config/mapeamento_colunas.yaml") -> dict:
    with open(caminho_yaml, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)

def normalizar_texto(texto: str) -> str:
    if pd.isna(texto):
        return ""
    return re.sub(r'\s+', ' ', str(texto)).strip().upper()

def ler_e_padronizar_excel(arquivo, nome_origem: str, mapeamento_usuario: dict = None) -> pd.DataFrame:
    df = pd.read_excel(arquivo, dtype=str)
    df.columns = [normalizar_texto(col).lower() for col in df.columns]
    
    if mapeamento_usuario:
        # Renomeia com base na seleção feita no dashboard
        df = df.rename(columns={v.lower(): k for k, v in mapeamento_usuario.items() if v})
    
    colunas_esperadas = ["modelo", "serial", "unidade", "patrimonio"]
    for col in colunas_esperadas:
        if col not in df.columns:
            df[col] = None  # Cria coluna vazia caso o sistema externo não tenha (ex: patrimonio)
            
    df = df[colunas_esperadas].copy()
    
    # Limpeza e normalização dos valores
    for col in colunas_esperadas:
        df[col] = df[col].apply(lambda x: normalizar_texto(x) if pd.notna(x) and str(x).strip() != "" else None)
        
    df["origem"] = nome_origem
    df["linha_excel"] = df.index + 2  # +2 considerando cabeçalho e índice 0
    return df
