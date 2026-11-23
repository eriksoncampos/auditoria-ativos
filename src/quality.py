import pandas as pd

def verificar_qualidade(df: pd.DataFrame, campos_obrigatorios: list) -> dict:
    # 1. Verifica incompletude (valores nulos nos campos obrigatórios)
    mask_incompletos = df[campos_obrigatorios].isna().any(axis=1)
    df_incompletos = df[mask_incompletos].copy()
    
    # 2. Verifica duplicidades baseadas no Serial (ignorando seriais vazios)
    df_com_serial = df[df["serial"].notna()]
    mask_duplicados = df_com_serial.duplicated(subset=["serial"], keep=False)
    df_duplicados = df_com_serial[mask_duplicados].sort_values(by="serial").copy()
    
    # 3. Base limpa (apenas registros válidos e únicos para cruzamento)
    df_limpo = df[~mask_incompletos].drop_duplicates(subset=["serial"], keep="first").copy()
    
    return {
        "incompletos": df_incompletos,
        "duplicados": df_duplicados,
        "limpo": df_limpo
    }
