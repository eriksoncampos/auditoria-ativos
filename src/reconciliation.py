import pandas as pd

def conciliar_sistemas(df_mestre: pd.DataFrame, dfs_sistemas: dict) -> pd.DataFrame:
    resultados = []
    
    # Indexa a base mestre pelo serial
    mestre_dict = df_mestre.set_index("serial").to_dict(orient="index")
    
    for nome_sistema, df_sis in dfs_sistemas.items():
        sis_dict = df_sis.set_index("serial").to_dict(orient="index")
        todos_seriais = set(mestre_dict.keys()).union(set(sis_dict.keys()))
        
        for serial in todos_seriais:
            item_mestre = mestre_dict.get(serial)
            item_sis = sis_dict.get(serial)
            
            status = "CONCILIADO"
            detalhes = []
            
            if item_mestre and not item_sis:
                status = "AUSENTE NO SISTEMA"
                detalhes.append(f"Existe na Mestre, mas não encontrado em {nome_sistema}")
            elif not item_mestre and item_sis:
                status = "NÃO CADASTRADO NA MESTRE"
                detalhes.append(f"Existe em {nome_sistema}, mas não na Mestre")
            else:
                # Ambos possuem o serial; verifica divergência de atributos
                if item_mestre["modelo"] != item_sis["modelo"]:
                    status = "DIVERGÊNCIA DE DADOS"
                    detalhes.append(f"Modelo: Mestre({item_mestre['modelo']}) != {nome_sistema}({item_sis['modelo']})")
                
                if item_mestre["unidade"] != item_sis["unidade"]:
                    status = "DIVERGÊNCIA DE DADOS"
                    detalhes.append(f"Unidade: Mestre({item_mestre['unidade']}) != {nome_sistema}({item_sis['unidade']})")
                    
                # Compara patrimônio apenas se o sistema externo possuir essa informação
                if item_sis.get("patrimonio") and item_mestre.get("patrimonio") != item_sis.get("patrimonio"):
                    status = "DIVERGÊNCIA DE DADOS"
                    detalhes.append(f"Patrimônio: Mestre({item_mestre['patrimonio']}) != {nome_sistema}({item_sis['patrimonio']})")

            resultados.append({
                "Sistema Comparado": nome_sistema,
                "Serial": serial,
                "Status": status,
                "Modelo (Mestre)": item_mestre["modelo"] if item_mestre else "-",
                "Modelo (Sistema)": item_sis["modelo"] if item_sis else "-",
                "Unidade (Mestre)": item_mestre["unidade"] if item_mestre else "-",
                "Unidade (Sistema)": item_sis["unidade"] if item_sis else "-",
                "Patrimônio (Mestre)": item_mestre.get("patrimonio") if item_mestre else "-",
                "Detalhes da Divergência": " | ".join(detalhes) if detalhes else "OK"
            })
            
    return pd.DataFrame(resultados)
