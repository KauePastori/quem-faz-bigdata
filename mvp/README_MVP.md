# Quem Faz — Painel demonstrativo (Big Data FIAP)

Esta interface demonstra o consumo de um CSV exportado da view agregada `workspace.quem_faz.gold_vw_categorias_publicas` no Databricks. Os números são **simulados**; não representam oportunidades ou contratações reais. Não há conexão em tempo real com Databricks.

## Estrutura

- `app.py`: painel Streamlit com filtros e visualizações
- `validacao.py`: contrato de dados e validação do CSV
- `dados/categorias_publicas.csv`: exportação original, sem transformação
- `tests/`: verificações automatizadas
- `.streamlit/config.toml`: tema escuro

## Executar (Windows, VS Code)

Com o terminal aberto na raiz do projeto `quem_faz_bigdata`:

```powershell
python -m pip install -r mvp/requirements.txt
python -m unittest discover -s mvp/tests -v
cd mvp
python -m streamlit run app.py
```

Abra `http://localhost:8501` (normalmente também abre automaticamente).
Para parar, pressione `Ctrl+C` no terminal.

## Atualizar os dados

1. Execute `SELECT * FROM workspace.quem_faz.gold_vw_categorias_publicas ORDER BY total_pedidos DESC;` no Databricks.
2. Baixe o resultado em CSV.
3. Substitua `mvp/dados/categorias_publicas.csv` preservando cabeçalhos e dados.
4. Atualize a página; o cache leva em conta a data de modificação do CSV.

## Evidência da integração

Capture uma tela do painel aberto mostrando os indicadores e gráficos, juntamente com a consulta da view Gold e uma explicação do trajeto do arquivo. Esta é uma **integração por exportação manual de CSV**, não uma integração contínua nem um sistema completo de contratação.

## Privacidade

O painel recebe somente estatísticas agregadas por categoria, sem `pedido_id`, nomes, contatos ou endereços individuais. A exportação está marcada como `DADOS SIMULADOS`. Caso a solução evolua para dados pessoais reais, será necessário aprofundar controles de acesso, finalidade, retenção e segurança conforme a LGPD.
