# Quem Faz — Scripts SQL para Databricks

## Propósito
Este pacote organiza os **scripts SQL já executados no Databricks** durante a Global Solution FIAP 2026.2. Não inclui capturas de tela, credenciais ou dados pessoais. Copie a pasta `sql/` para a **raiz de `quem_faz_bigdata`**; não substitua arquivos existentes.

## Ordem sugerida para um ambiente novo
1. Coletar os dois lotes via Airflow e fazer upload em `/Volumes/workspace/quem_faz/volume_entrada/lote_01` e `/lote_02`.
2. `01_bronze.sql` — cria Bronze e ingere os quatro arquivos com `COPY INTO`.
3. `02_prata_silver.sql` — cria Silver e executa `MERGE`.
4. `06_qualidade_silver.sql` — demonstra as regras RQ01, RQ02 e RQ03, com auditoria e casos de teste.
5. `03_ouro_gold.sql` — cria duas dimensões e uma fato, depois valida integridade.
6. `04_cinco_consultas.sql` — cinco consultas de negócio, a última é um indicador de impacto **demonstrativo**.
7. `05_view_mvp.sql` — view agregada para exportação manual a `mvp/dados/categorias_publicas.csv`.

Execute cada arquivo no Databricks SQL Editor, conectado ao warehouse Serverless. O catálogo e schema usados são `workspace.quem_faz`.

**No ambiente atual do aluno, não há necessidade de executar tudo outra vez**: as tabelas foram criadas e testadas; os scripts ficam documentados para reprodutibilidade no GitHub. Não execute comandos `CREATE OR REPLACE TABLE` se houver dados de produção ou alterações manuais que queira preservar.

## Evidências já observadas

| Camada | Tabela ou indicador | Resultado |
| --- | --- | --- |
| Bronze | `bronze_pedidos` | 200 linhas / 200 IDs distintos |
| Bronze | `bronze_distritos` | 192 linhas / 96 IDs distintos (duas coletas) |
| Bronze | Reexecução `COPY INTO` | 0 inserções adicionais por arquivo |
| Silver | `silver_pedidos` | 200 linhas / 200 IDs distintos |
| Silver | `silver_distritos` | 96 linhas / 96 IDs distintos |
| Qualidade | 200 pedidos simulados | 0 rejeitados |
| Qualidade | 4 casos controlados | 1 aprovado, 3 rejeitados |
| Gold | Categorias | 6 |
| Gold | Distritos oficiais | 96 |
| Gold | Fato de pedidos | 200 linhas |
| Gold | Pedidos com proposta / contratação / conclusão | 141 / 95 / 51 |

Os resultados dos pedidos foram **gerados sinteticamente**. Eles mostram o funcionamento do pipeline, não estatísticas reais da cidade. Os distritos são provenientes da API pública oficial do IBGE.

## Privacidade e limitações

- A view pública só contém agregações por categoria e um rótulo `DADOS SIMULADOS`.
- A transformação `SHA2(pedido_id, 256)` na Gold não é garantia geral de anonimização.
- A integração com o MVP Streamlit usa **CSV exportado manualmente do Databricks**, sem sincronização automática.
- O `COPY INTO` evita duplicações por identidade do arquivo ingerido; o `MERGE` trabalha por chave de negócio. São controles diferentes.
- A auditoria RQ01/RQ02/RQ03 é uma consulta de medição; a filtragem executada em Silver aplica verificações adicionais.

## GitHub: não publicar segredos

O projeto inicial já contém `.gitignore` que exclui `airflow-data/`, `chegada/*.jsonl`, `.env` e caches. Antes de subir, confirme que a pasta `airflow-data/` e eventuais arquivos de senhas não aparecem em `git status`. Não inclua tokens, senhas de login ou prints que as exibam.

Recomendação: atualizar o README principal para refletir o status **validado** das etapas (pois o README original foi criado como kit de partida). Inclua as evidências reais em `docs/evidencias/`, selecionando apenas as capturas essenciais.
