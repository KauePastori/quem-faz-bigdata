# Quem Faz — Big Data Architecture & Data Integration

Projeto acadêmico da FIAP Global Solution 2026.2, dentro do tema CitizenTech.

> **Estado do projeto**: kit de partida (Etapa 1). Coleta real do IBGE, execução do Airflow, Databricks e integração do MVP ainda precisam ser executadas e comprovadas no ambiente do aluno. Não é uma entrega final pronta.

## Problema e proposta
O Quem Faz conecta quem precisa contratar serviços a prestadores em São Paulo. A componente de dados propõe organizar pedidos e categorias para demonstrar indicadores de demanda e de andamento das solicitações, sem afirmar que os resultados simulados são comportamento real de cidadãos.

## Requisitos da disciplina
- Mínimo 2 fontes, com pelo menos 1 externa real.
- Airflow 3 agendado, duas tarefas paralelas, tarefa de conferência, pasta `chegada/`.
- Dois lotes de dias de coleta diferentes enviados manualmente ao Databricks Volume.
- Bronze incremental (Auto Loader ou COPY INTO), com comprovação de idempotência.
- Prata com tratamento de nulos, inválidos, MERGE e 3+ verificações de qualidade com contagens.
- Ouro: 1 fato + 2 dimensões, 5 SQL (incluindo impacto), privacidade, contrato de consumo com MVP.
- PDF com evidências reais e GitHub público com código reprodutível.

## Estrutura
```
quem_faz_bigdata_starter/
├── executar_local.py          # rodar coleta sem Airflow
├── docker-compose.yml         # Airflow 3 local (laboratório)
├── src/quem_faz/pipeline.py   # geração sintética, API oficial e conferência
├── dags/quem_faz_ingestao.py  # DAG Airflow diária
├── docs/ETAPA_1.md            # roteiro da primeira etapa
├── docs/fontes_e_modelo.md    # proveniência e dicionário de dados
├── tests/test_pipeline.py     # testes locais sem internet
├── amostras/                  # amostras publicáveis (apenas simuladas)
└── chegada/                   # saída da coleta, não publicada no git
```

## Pré-requisitos
- Python 3.10+ (testes de fonte local).
- Internet para consultar a API pública do IBGE.
- Para a segunda etapa: Docker Desktop com WSL2 (Windows) e Docker Compose.
- Para etapas seguintes: conta Databricks Free Edition e repositório GitHub.

## Começar — Windows (PowerShell)
Na pasta que contém este README:
```powershell
py --version
py -m unittest discover -s tests -v
py executar_local.py pedidos
py executar_local.py ibge
py executar_local.py todos
```

Os arquivos aparecerão em `chegada/` e seus nomes terão a data local da execução.
As coletas de dias diferentes devem ser documentadas por seus logs reais.

## Apache Airflow 3 — desenvolvimento local
Com Docker Desktop aberto:
```powershell
docker --version
docker compose version
docker compose up -d
docker compose logs -f airflow
```
Abra http://localhost:8080. Procure `quem_faz_coleta_diaria` e execute a DAG. Os dois nós de extração rodam em paralelo; a verificação depende de ambos.

O Airflow `standalone` cria a conta de administração de laboratório e imprime instruções de acesso no log. Em novas versões, consulte o arquivo de senhas gerado dentro do diretório `airflow-data/` quando aplicável. Não compartilhe senhas em prints nem no GitHub.

Para interromper:
```powershell
docker compose down
```

A pasta `airflow-data/` armazena dados locais de execução e está no `.gitignore`.

## Próximas entregas planejadas
- `databricks/01_bronze` — ingestão incremental com contagens.
- `databricks/02_prata` — padronização, regras de qualidade, MERGE.
- `databricks/03_ouro` — modelo dimensional.
- `databricks/04_sql` — cinco perguntas e interpretação.
- Demonstração mínima consumindo dados agregados da Ouro.
- Relatório acadêmico com prints reais, diagrama, fontes e conclusões.

## Fontes e documentação oficial
- IBGE API: https://servicodados.ibge.gov.br/api/docs/localidades
- Endpoint usado: https://servicodados.ibge.gov.br/api/v1/localidades/municipios/3550308/distritos
- Apache Airflow: https://airflow.apache.org/docs/
- Databricks Volumes: https://docs.databricks.com/aws/en/volumes/volume-files

## Ética, LGPD e reprodutibilidade
- Todos os pedidos foram gerados por código e **não representam cidadãos nem transações reais**.
- A tabela da fonte externa deve ser coletada de verdade do IBGE; nenhum dado fictício será apresentado como oficial.
- Não subir chaves, senhas, tokens ou dados pessoais reais.
- Este pipeline é um componente acadêmico e não representa produção com controles de autenticação corporativos.
