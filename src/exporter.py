import io
import pandas as pd

def gerar_excel_auditoria(df_conciliacao: pd.DataFrame, erros_qualidade: dict) -> bytes:
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        # Aba 1: Resumo de Divergências
        df_divergencias = df_conciliacao[df_conciliacao["Status"] != "CONCILIADO"]
        df_divergencias.to_excel(writer, sheet_name="Divergencias_Cruzamento", index=False)
        
        # Aba 2: Tudo Conciliado
        df_conciliacao.to_excel(writer, sheet_name="Base_Completa_Auditada", index=False)
        
        # Abas de Qualidade de Dados (Duplicados e Incompletos)
        for origem, dados in erros_qualidade.items():
            if not dados["duplicados"].empty:
                dados["duplicados"].to_excel(writer, sheet_name=f"Duplicados_{origem[:15]}", index=False)
            if not dados["incompletos"].empty:
                dados["incompletos"].to_excel(writer, sheet_name=f"Incompletos_{origem[:15]}", index=False)
                
    return output.getvalue()
