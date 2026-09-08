# TP3 - Desenvolvimento de Interfaces com Streamlit

- **Aluno:** Ruan Luiz Fernandes da Silva Lima
- **Disciplina:** Desenvolvimento Front-End com Python
- **Instituto:** Infnet

Aplicação em Streamlit para visualização de dados de turismo do Município do Rio de Janeiro, com dados do portal Data.Rio.

Arquivo da aplicação: `app_tp3_ruan_lima.py`

---

## 1. Escolha dos Datasets e Explicação do Objetivo e Motivação

**Enunciado:** Escolha um ou mais datasets do portal Data Rio. Explique o objetivo e a motivação por trás da escolha dos dados e quais funcionalidades e visualizações serão implementadas.

Escolhi dois datasets da seção de turismo do Data.Rio: a Tabela 1635, com o fluxo médio diário de passageiros e aeronaves nos aeroportos do município entre 1994 e 2025, e a Tabela 3098, com a taxa de ocupação dos hotéis por área da cidade entre 2009 e 2017. A motivação é que os dois mostram lados diferentes do mesmo assunto: um mede quanta gente chega no Rio, e o outro mede se essa gente fica hospedada na cidade. Como as duas séries são longas, dá pra ver bem os efeitos das Olimpíadas de 2016 e da pandemia em 2020, que é o tipo de coisa que aparece na hora de plotar.

Escolhi eles também porque são tabelas pequenas e com estrutura simples depois de tratadas: cada uma tem uma coluna de ano, uma coluna de texto para agrupar (o aeroporto ou o bairro) e colunas numéricas. Isso encaixa direto no que o trabalho pede, porque a coluna de texto vira os filtros de radio, checkbox e dropdown, o ano serve para os gráficos de linha e as colunas numéricas alimentam o histograma, o scatter plot e as métricas. Na aplicação vou implementar upload do arquivo, filtros, tabela interativa, download dos dados filtrados, color picker, cache, session state, gráficos simples e avançados, e um painel de métricas.

## 2. Realizar Upload de Arquivo XLS

**Enunciado:** Crie uma interface em Streamlit que permita ao usuário fazer o upload de um arquivo XLS contendo dados de turismo do portal Data.Rio.

Usei o `st.file_uploader` limitado a `.xls` e `.xlsx`. O arquivo enviado vai direto para o `pd.read_excel`, sem caminho fixo, então funciona em qualquer máquina. Enquanto nada é enviado a aplicação mostra uma mensagem pedindo o upload.

## 3. Filtro de Dados e Seleção

**Enunciado:** Exiba o dataset para o usuário e implemente três seletores diferentes (radio, checkbox, dropdowns) na interface que permitam ao usuário filtrar os dados carregados e selecionar as colunas ou linhas que deseja visualizar.

São três seletores na barra lateral: um radio para escolher entre ver tudo ou filtrar por um grupo, um selectbox com os valores da coluna de texto e um checkbox para cada coluna. Também coloquei um slider de período. Os filtros são montados a partir das colunas do arquivo enviado, então funcionam tanto com o de aeroportos quanto com o de hotéis.

## 4. Criar Visualizações de Dados - Tabelas

**Enunciado:** Crie uma tabela interativa que exiba os dados filtrados de acordo com os seletores carregados e permita ao usuário ordenar e filtrar as colunas diretamente pela interface.

O `st.dataframe` já permite ordenar clicando no cabeçalho e buscar pela lupa. Usei o `column_config` para formatar o ano como inteiro e os demais números com duas casas.

## 5. Desenvolver Serviço de Download de Arquivos

**Enunciado:** Implemente um serviço que permita ao usuário fazer o download dos dados filtrados em formato XLS diretamente pela interface da aplicação.

O arquivo é gerado na memória com `io.BytesIO` e `ExcelWriter`, e entregue pelo `st.download_button`. O download usa a tabela já filtrada, então respeita o grupo escolhido, o período e as colunas marcadas.

## 6. Utilizar Barra de Progresso e Spinners

**Enunciado:** Adicione uma barra de progresso e um spinner para indicar o carregamento dos dados enquanto o arquivo XLS é processado e exibido na interface.

Coloquei um `st.progress` em três etapas junto de um `st.spinner` em volta da leitura da planilha. Como os arquivos são pequenos e carregam quase instantaneamente, adicionei pausas curtas para o indicador ficar visível.

## 7. Utilizar Color Picker

**Enunciado:** Adicione um color picker à interface que permita ao usuário personalizar a cor de fundo do painel e das fontes exibidas na aplicação.

São dois `st.color_picker`, um para o fundo e outro para a fonte. As cores escolhidas entram num bloco de CSS aplicado com `st.markdown` e `unsafe_allow_html`, atingindo o painel principal e a barra lateral.

## 8. Utilizar Funcionalidade de Cache

**Enunciado:** Utilize a funcionalidade de cache do Streamlit para armazenar os dados carregados dos arquivos XLS, evitando a necessidade de recarregá-los a cada nova interação.

A leitura ficou dentro de uma função com `@st.cache_data`. O efeito é visível na prática: antes do cache a barra de progresso aparecia a cada clique num filtro, e depois ela só aparece na primeira vez que o arquivo é enviado.

## 9. Persistir Dados Usando Session State

**Enunciado:** Implemente a persistência de dados na aplicação utilizando Session State para manter as preferências do usuário (seleções e filtros escolhidos) durante a navegação.

Cada seletor recebeu um `key`, o que faz o Streamlit guardar a escolha no `st.session_state`. Adicionei um contador de interações na barra lateral e um botão para limpar os filtros. Se o usuário trocar de planilha, os filtros antigos são apagados, já que as colunas mudam.

## 10. Criar Visualizações de Dados - Gráficos Simples

**Enunciado:** Desenvolva gráficos simples (barras, linhas, e pie charts) para visualização dos dados carregados, utilizando o Streamlit.

São três gráficos: linha com a evolução por ano, barras horizontais com o total por grupo e pizza com a participação de cada um. Como o Jacarepaguá tem valores muito menores que os outros dois aeroportos, incluí uma opção de escala logarítmica para que ele fique visível nos gráficos.

## 11. Criar Visualizações de Dados - Gráficos Avançados

**Enunciado:** Adicione gráficos avançados (histograma e scatter plot) para fornecer insights mais profundos sobre os dados.

O histograma tem um slider para ajustar o número de faixas e mostra onde os registros se concentram. O scatter plot permite escolher as colunas dos eixos X e Y e separa os pontos por cor de acordo com o grupo. Abaixo dele coloquei a matriz de correlação: no dataset de aeroportos, passageiros e aeronaves têm correlação de 0,82, e no scatter dá para ver que cada aeroporto forma uma nuvem separada de pontos.

## 12. Exibir Métricas Básicas

**Enunciado:** Implemente a exibição de métricas básicas (como contagem de registros, médias, somas) diretamente na interface para fornecer um resumo rápido dos dados carregados.

Quatro cartões com `st.metric` no topo mostram a contagem de registros, o período selecionado, o número de grupos e a média. Logo abaixo há uma tabela com soma, média, mínimo e máximo de cada coluna numérica. Tudo é recalculado conforme os filtros mudam.

---

## Fonte dos dados

| Arquivo | Tabela original | Link |
|---|---|---|
| `aeroportos.xlsx` | Tabela 1635 - Fluxo médio diário de passageiros e de aeronaves nos aeroportos no Município do Rio de Janeiro entre 1994-2025 | https://www.data.rio/documents/1d4d9c6b90944a86b81fdaa4e66bc644 |
| `hoteis.xlsx` | Tabela 3098 - Taxa de ocupação dos hotéis, segundo a área selecionada da cidade no Município do Rio de Janeiro entre 2009-2017 | https://www.data.rio/datasets/4eb756b5018d439f84b331663ef8e415 |

## Tratamento dos dados

As planilhas do Data.Rio vêm em formato de relatório e não de tabela, então precisei reorganizar antes de usar. As duas tinham linhas de título no topo, notas de rodapé embaixo e cabeçalho dividido em vários níveis com células mescladas. Na de aeroportos os dados indisponíveis vinham marcados com `...` no lugar do número, e na de hotéis cada ano era uma coluna diferente.

O que fiz foi tirar os títulos e rodapés, montar um cabeçalho único, transformar as colunas de ano em linhas e padronizar os nomes das colunas em minúsculo e sem acento. Nenhum valor foi alterado.

## Como rodar

1. Criar o ambiente: `py -m venv venv`
2. Ativar: `.\venv\Scripts\activate`
3. Instalar: `pip install streamlit pandas openpyxl xlsxwriter matplotlib`
4. Rodar: `streamlit run app_tp3_ruan_lima.py`

Depois é só carregar o `aeroportos.xlsx` ou o `hoteis.xlsx` no campo de upload da aplicação.