-- QUEM FAZ | 06 | TESTES DE QUALIDADE (Prata)
-- Auditoria sobre os 200 pedidos simulados + testes CONTROLADOS (sem INSERT).

-- Auditoria na Bronze: RQ01 = ID/categoria; RQ02 = status/propostas; RQ03 = distrito oficial.
WITH distritos_oficiais AS (
    SELECT DISTINCT UPPER(TRIM(nome)) AS distrito_normalizado
    FROM workspace.quem_faz.bronze_distritos
    WHERE nome IS NOT NULL
), validacao AS (
    SELECT p.pedido_id,
      (p.pedido_id IS NULL OR TRIM(p.pedido_id) = ''
       OR TRY_CAST(p.categoria_id AS INT) IS NULL
       OR TRIM(COALESCE(p.categoria_nome,'')) = '') AS erro_rq01,
      (p.status IS NULL OR p.status NOT IN
            ('publicado','com_propostas','contratado','concluido','cancelado')
       OR p.quantidade_propostas IS NULL OR p.quantidade_propostas < 0
       OR (p.status = 'publicado' AND p.quantidade_propostas <> 0)
       OR (p.status IN ('com_propostas','contratado','concluido')
           AND p.quantidade_propostas < 1)) AS erro_rq02,
      (p.distrito_nome IS NULL OR TRIM(p.distrito_nome) = ''
       OR d.distrito_normalizado IS NULL) AS erro_rq03
    FROM workspace.quem_faz.bronze_pedidos p
    LEFT JOIN distritos_oficiais d
      ON UPPER(TRIM(p.distrito_nome)) = d.distrito_normalizado
)
SELECT COUNT(*) AS total_analisado,
    COUNT_IF(erro_rq01) AS rejeitados_rq01,
    COUNT_IF(erro_rq02) AS rejeitados_rq02,
    COUNT_IF(erro_rq03) AS rejeitados_rq03,
    COUNT_IF(NOT erro_rq01 AND NOT erro_rq02 AND NOT erro_rq03) AS registros_validos,
    COUNT_IF(erro_rq01 OR erro_rq02 OR erro_rq03) AS total_rejeitados
FROM validacao;
-- Observado: 200 analisados, 200 válidos, rejeitados RQ01/RQ02/RQ03 = 0.

-- Teste unitário com quatro casos temporários. Não altera dados originais.
WITH casos_teste AS (
  SELECT * FROM VALUES
    ('VALIDO-001', 1, 'Limpeza', 'publicado', 0, 'Pinheiros'),
    (NULL, 1, 'Limpeza', 'publicado', 0, 'Pinheiros'),
    ('ERRO-RQ02', 1, 'Limpeza', 'status_invalido', 0, 'Pinheiros'),
    ('ERRO-RQ03', 1, 'Limpeza', 'publicado', 0, 'Distrito Inexistente')
  AS t(pedido_id,categoria_id,categoria_nome,status,quantidade_propostas,distrito_nome)
), validacao AS (
  SELECT c.*,
    (c.pedido_id IS NULL OR TRIM(c.pedido_id) = '' OR c.categoria_id IS NULL
     OR c.categoria_id <= 0 OR TRIM(COALESCE(c.categoria_nome,'')) = '') AS erro_rq01,
    (c.status IS NULL OR c.status NOT IN
       ('publicado','com_propostas','contratado','concluido','cancelado')
     OR c.quantidade_propostas IS NULL OR c.quantidade_propostas < 0
     OR (c.status = 'publicado' AND c.quantidade_propostas <> 0)
     OR (c.status IN ('com_propostas','contratado','concluido')
          AND c.quantidade_propostas < 1)) AS erro_rq02,
    (d.distrito_id IS NULL) AS erro_rq03
  FROM casos_teste c
  LEFT JOIN workspace.quem_faz.silver_distritos d
    ON UPPER(TRIM(c.distrito_nome)) = d.distrito_nome_normalizado
)
SELECT COUNT(*) AS total_testado,
    COUNT_IF(erro_rq01) AS rejeitados_rq01,
    COUNT_IF(erro_rq02) AS rejeitados_rq02,
    COUNT_IF(erro_rq03) AS rejeitados_rq03,
    COUNT_IF(NOT erro_rq01 AND NOT erro_rq02 AND NOT erro_rq03) AS aprovados,
    COUNT_IF(erro_rq01 OR erro_rq02 OR erro_rq03) AS rejeitados
FROM validacao;
-- Observado: 4 casos; 1 rejeição em cada regra; 1 aprovado e 3 rejeitados.
