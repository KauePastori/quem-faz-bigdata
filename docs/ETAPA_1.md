# Etapa 1 — Primeira execução

## Objetivo desta etapa
Preparar as duas fontes, validar o formato JSONL e obter duas saídas locais na pasta `chegada/`.

### Windows, PowerShell (Python 3.10+)
1. Extraia o ZIP e abra a pasta do projeto no VS Code.
2. No terminal PowerShell dessa pasta, rode `py --version`.
3. Rode `py -m unittest discover -s tests -v` — devem aparecer 2 testes como `OK`.
4. Rode `py executar_local.py pedidos` — cria `chegada/pedidos_DATA.jsonl`.
5. Rode `py executar_local.py ibge` — consulta a API pública e cria `chegada/distritos_ibge_DATA.jsonl`.
6. Rode `py executar_local.py todos` — confere os dois arquivos e imprime contagens e hashes SHA256.
7. Abra os arquivos JSONL no VS Code e confirme que cada linha é um objeto JSON.

**Comando alternativo:** se `py` não existir, experimente `python`.

Se a consulta IBGE falhar, verifique internet, firewall e endpoint no navegador. **Não substitua a API real por dados inventados para entregar como fonte externa.**

### Validação e evidência
- Fonte 1: resposta obtida diretamente de `servicodados.ibge.gov.br`.
- Fonte 2: registros sintéticos com `simulado=true`.
- Capture o terminal com os arquivos gerados e contagens (não confundir com print real do Airflow, que virá na etapa seguinte).

### Próxima etapa — Airflow 3
Instale Docker Desktop com backend WSL2, execute `docker compose up -d`, depois abra `http://localhost:8080`. Confira a DAG `quem_faz_coleta_diaria`, execute-a e salve os prints do Graph e Grid. No primeiro start, a senha de admin é informada no log (`docker compose logs airflow`). Consulte `README.md` para detalhes.

**Cuidado:** o arquivo `docker-compose.yml` deste kit é para laboratório, não implantação de produção. Ajustes podem ser necessários dependendo de versão, Docker Desktop e permissões da máquina.
