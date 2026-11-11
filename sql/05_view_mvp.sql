-- QUEM FAZ | 05 | VIEW AGREGADA PARA DEMONSTRAÇÃO DO MVP
-- Essa view não expõe IDs dos pedidos, nem informações pessoais.
-- NÃO é uma integração em tempo real: resultado exportado manualmente para CSV.

CREATE OR REPLACE VIEW workspace.quem_faz.gold_vw_categorias_publicas AS
SELECT
    c.categoria_nome AS categoria,
    COUNT(*) AS total_pedidos,
    SUM(f.recebeu_proposta) AS pedidos_com_proposta,
    SUM(f.teve_contratacao) AS pedidos_contratados,
    SUM(f.servico_concluido) AS servicos_concluidos,
    ROUND(SUM(f.servico_concluido) * 100.0 / NULLIF(COUNT(*),0),2)
        AS taxa_conclusao_percentual,
    'DADOS SIMULADOS' AS origem_dados
FROM workspace.quem_faz.gold_fato_pedidos f
JOIN workspace.quem_faz.gold_dim_categoria c ON f.categoria_id = c.categoria_id
WHERE f.simulado = TRUE
GROUP BY c.categoria_id, c.categoria_nome;

SELECT * FROM workspace.quem_faz.gold_vw_categorias_publicas
ORDER BY total_pedidos DESC;
-- Exportar resultado como CSV e copiar para mvp/dados/categorias_publicas.csv.
