# Fontes, proveniência e contrato de dados — Quem Faz

## Fonte 1: API pública oficial IBGE
- Origem: Instituto Brasileiro de Geografia e Estatística (IBGE).
- Endpoint: https://servicodados.ibge.gov.br/api/v1/localidades/municipios/3550308/distritos
- Formato da resposta: JSON; exportamos um item original por linha (JSONL).
- Frequência prevista: coleta diária via Apache Airflow.
- Nome do arquivo: `distritos_ibge_YYYY-MM-DD.jsonl`.
- Autenticação: não exigida.
- Relevância: referência oficial de distritos do município, para enriquecimento geográfico.
- Observação: dados públicos reais; validar os campos efetivamente retornados pela API durante a coleta.

## Fonte 2: pedidos do Quem Faz — SIMULAÇÃO ACADÊMICA
- Origem: gerador determinístico em Python, não API do produto.
- Formato: JSONL, 100 registros de exemplo por lote (configurável).
- Frequência prevista: diária via Apache Airflow.
- Nome do arquivo: `pedidos_YYYY-MM-DD.jsonl`.
- Relevância: permite demonstrar a jornada de contratação mesmo sem backend integrado.
- Não representar os números sintéticos como demanda real ou resultados reais da plataforma.
- Geração: mesma data e quantidade => mesmos identificadores e mesmos valores (idempotência).

### Esquema dos pedidos sintéticos
| Coluna | Tipo esperado | Significado |
|---|---|---|
| pedido_id | STRING | Chave estável `QF-AAAAMMDD-00001` |
| criado_em | TIMESTAMP / STRING Bronze | Data/hora de criação |
| municipio_ibge_id | LONG | 3550308 = São Paulo |
| distrito_nome | STRING | Área do pedido, nome do distrito a validar com fonte externa |
| categoria_id | INT | Identificador de categoria |
| categoria_nome | STRING | Ex.: Limpeza, Pintura, Manutenção |
| caminho_contratacao | STRING | `explorar_categoria` ou `publicar_pedido` |
| status | STRING | `publicado`, `com_propostas`, `contratado`, `concluido`, `cancelado` |
| quantidade_propostas | INT | Número simulado de propostas recebidas |
| concluido | BOOLEAN | Verdadeiro apenas para status `concluido` |
| origem | STRING | `quem_faz_simulado` |
| simulado | BOOLEAN | Sempre `true` |

## Qualidade: regras propostas para a futura Prata
1. `pedido_id` não pode ser nulo nem vazio e não pode ficar duplicado após MERGE.
2. `categoria_id` deve pertencer ao catálogo conhecido (1..6).
3. `quantidade_propostas` deve ser >= 0 e, nos status com proposta obrigatória, >= 1.
4. `status` deve pertencer à lista de estados válida.
5. `distrito_nome` deve ter correspondência territorial definida ou ser segregado para tratamento.

A Prata registrará a contagem de rejeições por regra e criará medidas para a camada Ouro.

## Modelo dimensional futuro da Ouro
- `dim_categoria`: categoria_id, categoria_nome.
- `dim_distrito`: id de distrito oficial, nome oficial normalizado, município.
- `fato_pedidos`: pedido_id, data, ids dimensionais, caminho, status, quantidade_propostas, concluido.
- Visão para o MVP: agregações de contagem e taxa por categoria/distrito, sem identificadores pessoais.

## Integração planejada ao MVP
O produto consome um JSON agregado exportado da Ouro para mostrar categorias demandadas por distrito e taxa de conclusão **somente dos registros simulados**, explicitamente marcados como demonstração.

## Privacidade
Não gerar nomes, documentos, telefones, e-mails, endereços completos nem dados pessoais reais. Se forem introduzidos dados reais em fase posterior, anonimizar e restringir antes da publicação no GitHub e na camada Ouro.
