"""Regras de leitura e validação da exportação agregada da Gold.

Sem Streamlit: pode ser testado diretamente com a biblioteca padrão do Python.
"""
from __future__ import annotations

import csv
from decimal import Decimal, InvalidOperation
from pathlib import Path

CAMPOS = (
    "categoria",
    "total_pedidos",
    "pedidos_com_proposta",
    "pedidos_contratados",
    "servicos_concluidos",
    "taxa_conclusao_percentual",
    "origem_dados",
)
COLUNAS_CONTAGEM = (
    "total_pedidos",
    "pedidos_com_proposta",
    "pedidos_contratados",
    "servicos_concluidos",
)


class DadosInvalidos(ValueError):
    """A exportação não respeita o contrato de dados da view pública."""


def ler_categorias(caminho: str | Path) -> list[dict]:
    """Carrega as categorias sem modificar os valores do CSV original."""
    caminho = Path(caminho)
    if not caminho.is_file():
        raise DadosInvalidos(f"Arquivo não encontrado: {caminho}")

    with caminho.open("r", encoding="utf-8-sig", newline="") as arquivo:
        leitor = csv.DictReader(arquivo)
        if leitor.fieldnames is None:
            raise DadosInvalidos("O CSV não contém cabeçalho.")
        faltantes = sorted(set(CAMPOS) - set(leitor.fieldnames))
        if faltantes:
            raise DadosInvalidos(f"Colunas ausentes: {', '.join(faltantes)}")
        linhas = list(leitor)

    if not linhas:
        raise DadosInvalidos("O CSV não possui registros.")

    resultado = []
    categorias = set()
    for numero, linha in enumerate(linhas, start=2):
        categoria = (linha.get("categoria") or "").strip()
        if not categoria or categoria.casefold() in categorias:
            raise DadosInvalidos(f"Categoria vazia ou repetida na linha {numero}.")
        categorias.add(categoria.casefold())

        registro = {"categoria": categoria}
        for campo in COLUNAS_CONTAGEM:
            try:
                numero_inteiro = int(linha[campo])
            except (TypeError, ValueError) as exc:
                raise DadosInvalidos(f"{campo} inválido na linha {numero}.") from exc
            if numero_inteiro < 0:
                raise DadosInvalidos(f"{campo} negativo na linha {numero}.")
            registro[campo] = numero_inteiro

        if not (
            registro["servicos_concluidos"] <= registro["pedidos_contratados"] <= registro["total_pedidos"]
            and registro["pedidos_com_proposta"] <= registro["total_pedidos"]
        ):
            raise DadosInvalidos(f"Contagens inconsistentes na linha {numero}.")
        try:
            taxa = Decimal((linha.get("taxa_conclusao_percentual") or "").strip())
        except InvalidOperation as exc:
            raise DadosInvalidos(f"Taxa inválida na linha {numero}.") from exc
        if not taxa.is_finite() or not (Decimal(0) <= taxa <= Decimal(100)):
            raise DadosInvalidos(f"Taxa fora da faixa na linha {numero}.")
        esperada = (
            Decimal(100) * registro["servicos_concluidos"] / registro["total_pedidos"]
            if registro["total_pedidos"] else Decimal(0)
        )
        if abs(taxa - esperada) > Decimal("0.011"):
            raise DadosInvalidos(f"Taxa de conclusão não confere com contagens na linha {numero}.")
        origem = (linha.get("origem_dados") or "").strip()
        if origem != "DADOS SIMULADOS":
            raise DadosInvalidos(f"Origem não identificada como simulada na linha {numero}.")
        registro["taxa_conclusao_percentual"] = float(taxa)
        registro["origem_dados"] = origem
        resultado.append(registro)

    return resultado


def resumir(registros: list[dict]) -> dict:
    """Soma os indicadores; útil para filtros e para os testes."""
    totais = {campo: sum(linha[campo] for linha in registros) for campo in COLUNAS_CONTAGEM}
    total = totais["total_pedidos"]
    totais["taxa_propostas"] = round(100 * totais["pedidos_com_proposta"] / total, 2) if total else 0.0
    totais["taxa_contratacao"] = round(100 * totais["pedidos_contratados"] / total, 2) if total else 0.0
    totais["taxa_conclusao"] = round(100 * totais["servicos_concluidos"] / total, 2) if total else 0.0
    return totais
