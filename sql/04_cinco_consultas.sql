-- QUEM FAZ | 04 | CINCO CONSULTAS DE NEGÓCIO DA CAMADA OURO
-- Resultados demonstrativos: base interna de PEDIDOS SIMULADOS, não representam demanda real.

-- CONSULTA 01: Categorias mais solicitadas
SELECT c.categoria_nome AS categoria,
       COUNT(*) AS total_pedidos,
       ROUND(COUNT(*) * 100.0 /
             (SELECT COUNT(*) FROM workspace.quem_faz.gold_fato_pedidos), 2)
           AS percentual_total
FROM workspace.quem_faz.gold_fato_pedidos f
JOIN workspace.quem_faz.gold_dim_categoria c ON f.categoria_id = c.categoria_id
GROUP BY c.categoria_id, c.categoria_nome
ORDER BY total_pedidos DESC;
-- Observado: Hidráulica 43 (21,5%), Montagem de móveis 33 (16,5%).

-- CONSULTA 02: Distritos com mais pedidos
SELECT d.distrito_nome AS distrito,
       COUNT(*) AS total_pedidos,
       ROUND(COUNT(*) * 100.0 /
             (SELECT COUNT(*) FROM workspace.quem_faz.gold_fato_pedidos), 2)
           AS percentual_total
FROM workspace.quem_faz.gold_fato_pedidos f
JOIN workspace.quem_faz.gold_dim_distrito d ON f.distrito_id = d.distrito_id
GROUP BY d.distrito_id, d.distrito_nome
ORDER BY total_pedidos DESC, distrito ASC;
-- Observado: Tucuruvi 23 (11,5%), Itaquera e Vila Mariana 22 cada (11%).

-- CONSULTA 03: Pedidos que receberam propostas
SELECT COUNT(*) AS total_pedidos,
       COUNT_IF(recebeu_proposta = 1) AS pedidos_com_proposta,
       COUNT_IF(recebeu_proposta = 0) AS pedidos_sem_proposta,
       SUM(quantidade_propostas) AS total_propostas_registradas,
       ROUND(COUNT_IF(recebeu_proposta = 1) * 100.0 / NULLIF(COUNT(*),0),2)
           AS percentual_com_proposta
FROM workspace.quem_faz.gold_fato_pedidos;
-- Observado: 200 total, 141 com proposta, 59 sem proposta, 613 propostas (70,5%).

-- CONSULTA 04: Taxa de contratação por categoria
SELECT c.categoria_nome AS categoria,
       COUNT(*) AS total_pedidos,
       COUNT_IF(f.teve_contratacao = 1) AS pedidos_contratados,
       COUNT_IF(f.servico_concluido = 1) AS servicos_concluidos,
       ROUND(COUNT_IF(f.teve_contratacao = 1) * 100.0 / NULLIF(COUNT(*),0),2)
           AS taxa_contratacao_percentual
FROM workspace.quem_faz.gold_fato_pedidos f
JOIN workspace.quem_faz.gold_dim_categoria c ON f.categoria_id = c.categoria_id
GROUP BY c.categoria_id, c.categoria_nome
ORDER BY taxa_contratacao_percentual DESC, total_pedidos DESC;
-- Observado: Montagem de móveis tem taxa mais alta: 24/33 (72,73%).

-- CONSULTA 05: Resultado operacional / impacto DEMONSTRATIVO
SELECT COUNT(*) AS total_solicitacoes,
       COUNT_IF(recebeu_proposta = 1) AS pedidos_com_proposta,
       COUNT_IF(teve_contratacao = 1) AS pedidos_contratados,
       COUNT_IF(servico_concluido = 1) AS servicos_concluidos,
       ROUND(COUNT_IF(teve_contratacao = 1) * 100.0 / NULLIF(COUNT(*),0),2)
           AS taxa_contratacao,
       ROUND(COUNT_IF(servico_concluido = 1) * 100.0 / NULLIF(COUNT(*),0),2)
           AS taxa_conclusao,
       ROUND(COUNT_IF(servico_concluido = 1) * 100.0 /
             NULLIF(COUNT_IF(teve_contratacao = 1),0),2)
           AS conclusao_entre_contratados,
       COUNT(DISTINCT distrito_id) AS distritos_atendidos,
       COUNT(DISTINCT categoria_id) AS categorias_disponiveis
FROM workspace.quem_faz.gold_fato_pedidos;
-- Observado: 200, 141, 95, 51, 47,50%, 25,50%, 53,68%, 12, 6.
