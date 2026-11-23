import streamlit as st
import pandas as pd
import plotly.express as px
from src.ingestion import ler_e_padronizar_excel, carregar_config_mapeamento
from src.quality import verificar_qualidade
from src.reconciliation import conciliar_sistemas
from src.exporter import gerar_excel_auditoria

st.set_page_config(page_title="Auditoria de Ativos", layout="wide")
st.title("📊 Sistema de Conciliação e Auditoria de Ativos")

config = carregar_config_mapeamento()

def limpar_resultado_auditoria():
    st.session_state.pop("resultado_auditoria", None)

def renderizar_mapeador(arquivo, chave_prefixo: str, exigir_patrimonio: bool = False):
    df_preview = pd.read_excel(arquivo, nrows=1)
    colunas_arquivo = [""] + list(df_preview.columns)
    
    st.markdown(f"**Mapeamento de Colunas ({chave_prefixo}):**")
    cols = st.columns(4)
    mapeamento = {}
    
    campos = ["modelo", "serial", "unidade", "patrimonio"]
    for idx, campo in enumerate(campos):
        # Tenta auto-selecionar com base no YAML
        sinonimos = config["sinonimos"].get(campo, [])
        indice_padrao = 0
        for i, col_arq in enumerate(colunas_arquivo):
            if str(col_arq).strip().lower() in sinonimos:
                indice_padrao = i
                break
                
        label = f"{campo.capitalize()} {'*' if (campo != 'patrimonio' or exigir_patrimonio) else '(Opcional)'}"
        mapeamento[campo] = cols[idx].selectbox(
            label,
            colunas_arquivo,
            index=indice_padrao,
            key=f"{chave_prefixo}_{campo}",
            on_change=limpar_resultado_auditoria,
        )
    
    arquivo.seek(0)  # Reseta ponteiro do arquivo após preview
    return mapeamento

# --- SIDEBAR: UPLOAD DOS ARQUIVOS ---
with st.sidebar:
    st.header("1. Upload de Planilhas")
    arq_mestre = st.file_uploader(
        "Planilha Mestre (Base Oficial)",
        type=["xlsx", "xlsm"],
        on_change=limpar_resultado_auditoria,
    )
    arqs_sistemas = st.file_uploader(
        "Planilhas dos Sistemas (3 ou mais)",
        type=["xlsx", "xlsm"],
        accept_multiple_files=True,
        on_change=limpar_resultado_auditoria,
    )

if arq_mestre and arqs_sistemas:
    st.subheader("2. Configuração de Colunas")
    with st.expander("Ajustar mapeamento de colunas das planilhas", expanded=True):
        map_mestre = renderizar_mapeador(arq_mestre, "Mestre", exigir_patrimonio=True)
        maps_sistemas = {}
        for arq in arqs_sistemas:
            st.divider()
            maps_sistemas[arq.name] = renderizar_mapeador(arq, arq.name, exigir_patrimonio=False)

    if st.button("🚀 Executar Auditoria", type="primary"):
        with st.spinner("Processando planilhas e cruzando dados..."):
            erros_qualidade = {}
            
            # Processa Mestre
            df_mestre_raw = ler_e_padronizar_excel(arq_mestre, "Mestre", map_mestre)
            qual_mestre = verificar_qualidade(df_mestre_raw, ["modelo", "serial", "unidade", "patrimonio"])
            erros_qualidade["Mestre"] = qual_mestre
            
            # Processa Sistemas Externos
            dfs_sistemas_limpos = {}
            for arq in arqs_sistemas:
                nome_sis = arq.name.rsplit(".", 1)[0]
                df_sis_raw = ler_e_padronizar_excel(arq, nome_sis, maps_sistemas[arq.name])
                qual_sis = verificar_qualidade(df_sis_raw, ["modelo", "serial", "unidade"])
                erros_qualidade[nome_sis] = qual_sis
                dfs_sistemas_limpos[nome_sis] = qual_sis["limpo"]
                
            # Conciliação
            df_resultado = conciliar_sistemas(qual_mestre["limpo"], dfs_sistemas_limpos)
        # O Streamlit reexecuta o script ao alterar filtros; preserve os dados na sessão.
        st.session_state["resultado_auditoria"] = {
            "df": df_resultado,
            "erros_qualidade": erros_qualidade,
        }

    if "resultado_auditoria" in st.session_state:
        auditoria = st.session_state["resultado_auditoria"]
        df_resultado = auditoria["df"]
        erros_qualidade = auditoria["erros_qualidade"]

        # --- DASHBOARD ---
        st.divider()
        st.subheader("3. Resultados da Auditoria")

        total_registros = len(df_resultado)
        conciliados = len(df_resultado[df_resultado["Status"] == "CONCILIADO"])
        divergentes = total_registros - conciliados
        total_duplicados = sum(len(v["duplicados"]) for v in erros_qualidade.values())
        total_incompletos = sum(len(v["incompletos"]) for v in erros_qualidade.values())

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Total Cruzado", total_registros)
        k2.metric("Conciliados (OK)", conciliados, f"{(conciliados/total_registros*100):.1f}%" if total_registros else "0%")
        k3.metric("Divergências / Ausências", divergentes, delta_color="inverse")
        k4.metric("Erros de Base (Duplicados/Nulos)", total_duplicados + total_incompletos, delta_color="inverse")

        # Gráficos
        c1, c2 = st.columns(2)
        with c1:
            fig_status = px.pie(df_resultado, names="Status", title="Distribuição Geral de Status", hole=0.4)
            st.plotly_chart(fig_status, use_container_width=True)
        with c2:
            fig_sis = px.histogram(df_resultado, x="Sistema Comparado", color="Status", barmode="group", title="Status por Sistema")
            st.plotly_chart(fig_sis, use_container_width=True)

        # Tabela Interativa e Download
        st.subheader("Detalhamento dos Registros")
        filtro_status = st.multiselect("Filtrar Status:", df_resultado["Status"].unique(), default=df_resultado["Status"].unique())
        st.dataframe(df_resultado[df_resultado["Status"].isin(filtro_status)], use_container_width=True)

        excel_bytes = gerar_excel_auditoria(df_resultado, erros_qualidade)
        st.download_button(
            label="📥 Baixar Relatório Completo (.xlsx)",
            data=excel_bytes,
            file_name="Relatorio_Auditoria_Ativos.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
else:
    st.info("👈 Faça o upload da Planilha Mestre e das Planilhas dos Sistemas na barra lateral para começar.")
