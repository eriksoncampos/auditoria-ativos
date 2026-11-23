# Auditoria de Ativos

Aplicação web em Streamlit para comparar a planilha mestre de ativos com planilhas de sistemas externos. A conciliação usa o número de série como identificador e destaca registros conciliados, divergências e ativos ausentes ou não cadastrados.

## Funcionalidades

- Upload de planilhas Excel nos formatos `.xlsx` e `.xlsm`.
- Mapeamento das colunas para modelo, serial, unidade e patrimônio, com sugestão automática baseada nos sinônimos configurados.
- Verificação de campos obrigatórios e identificação de seriais duplicados.
- Comparação entre a base mestre e cada sistema.
- Painel com indicadores, gráficos e detalhamento filtrável por status.
- Exportação de um relatório completo em Excel.

## Requisitos

- Python 3.
- Dependências listadas em [`requirements.txt`](requirements.txt).

## Instalação e execução

Execute os comandos abaixo no PowerShell, a partir da pasta raiz do projeto:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

O Streamlit abrirá a aplicação no navegador. Mantenha o terminal aberto enquanto estiver usando o painel.

## Como usar

1. Envie a planilha mestre na barra lateral.
2. Envie as planilhas dos sistemas que deseja comparar.
3. Confira o mapeamento das colunas para cada arquivo. A planilha mestre requer modelo, serial, unidade e patrimônio; nos sistemas externos, patrimônio é opcional.
4. Clique em **Executar Auditoria**.
5. Consulte os indicadores e gráficos e use **Filtrar Status** para escolher os registros exibidos no detalhamento. Os resultados permanecem no painel enquanto o filtro é alterado.
6. Clique em **Baixar Relatório Completo (.xlsx)** para exportar os resultados.

## Regras de conciliação

- O serial é usado para relacionar os registros entre as planilhas.
- Modelo e unidade são comparados quando o serial existe nas duas bases.
- Patrimônio é comparado quando o sistema externo informa esse campo.
- A aplicação identifica os status `CONCILIADO`, `DIVERGÊNCIA DE DADOS`, `AUSENTE NO SISTEMA` e `NÃO CADASTRADO NA MESTRE`.
- Registros incompletos são identificados e excluídos da base limpa. Seriais duplicados são listados; para a conciliação, a primeira ocorrência de cada serial é mantida.

## Relatório Excel

O arquivo exportado contém:

- `Divergencias_Cruzamento`: registros da conciliação cujo status não é `CONCILIADO`.
- `Base_Completa_Auditada`: todos os registros comparados.
- Abas de duplicados e incompletos para cada origem que apresentar esses problemas.

## Estrutura do projeto

```text
.
├── app.py
├── config/
│   └── mapeamento_colunas.yaml
├── planilhas/
├── requirements.txt
└── src/
    ├── exporter.py
    ├── ingestion.py
    ├── quality.py
    └── reconciliation.py
```

O arquivo `config/mapeamento_colunas.yaml` define os sinônimos usados para sugerir o mapeamento das colunas. Execute o comando `streamlit run app.py` a partir da raiz do projeto para que esse arquivo de configuração seja localizado.
