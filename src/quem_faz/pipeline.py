
"""Ingestão de duas fontes do Quem Faz.

Fonte pública real: IBGE - distritos do município de São Paulo.
Fonte interna: pedidos SINTÉTICOS, gerados de maneira reprodutível.
Nenhum registro sintético representa pessoa ou contratação reais.
"""

from __future__ import annotations

import hashlib
import gzip
import json
import os
import random
import time
import unicodedata
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo


IBGE_URL = (
    "https://servicodados.ibge.gov.br/api/v1/"
    "localidades/municipios/3550308/distritos"
)

MUNICIPIO_IBGE = 3550308

CATEGORIAS = [
    (1, "Limpeza"),
    (2, "Manutenção"),
    (3, "Pintura"),
    (4, "Elétrica"),
    (5, "Hidráulica"),
    (6, "Montagem de móveis"),
]

# Nomes de áreas utilizados APENAS na fonte interna sintética.
# A correspondência com os distritos oficiais deve ser
# auditada na camada Prata do Databricks.

DISTRITOS_EXEMPLO = [
    "Sé",
    "Pinheiros",
    "Santana",
    "Lapa",
    "Butantã",
    "Vila Mariana",
    "Santo Amaro",
    "Itaquera",
    "Penha",
    "Mooca",
    "Tucuruvi",
    "Consolação",
]

STATUS = [
    "publicado",
    "com_propostas",
    "contratado",
    "concluido",
    "cancelado",
]

PESOS_STATUS = [25, 25, 20, 25, 5]


def data_local() -> date:
    """Retorna a data atual no fuso horário de São Paulo."""
    return datetime.now(
        ZoneInfo("America/Sao_Paulo")
    ).date()


def pasta_chegada(
    base_dir: str | Path | None = None
) -> Path:
    """Cria e retorna a pasta de chegada dos arquivos.

    Ambiente local: raiz do projeto.
    Docker: QF_BASE_DIR=/opt/airflow.
    """
    raiz = Path(
        base_dir
        or os.environ.get("QF_BASE_DIR")
        or Path(__file__).resolve().parents[2]
    )

    chegada = raiz / "chegada"
    chegada.mkdir(parents=True, exist_ok=True)

    return chegada


def _gravar_jsonl(
    caminho: Path,
    registros: list[dict]
) -> Path:
    """Grava registros JSONL em UTF-8 de forma atômica."""

    temporario = caminho.with_suffix(".tmp")

    with temporario.open(
        "w",
        encoding="utf-8",
        newline="\n"
    ) as arquivo:

        for registro in registros:
            arquivo.write(
                json.dumps(
                    registro,
                    ensure_ascii=False,
                    sort_keys=True
                ) + "\n"
            )

    temporario.replace(caminho)

    return caminho


def gerar_pedidos_sinteticos(
    dia: date | None = None,
    quantidade: int = 100,
    base_dir: str | Path | None = None
) -> Path:
    """Gera um lote sintético idempotente por data e versão."""

    dia = dia or data_local()

    if quantidade <= 0:
        raise ValueError(
            "A quantidade deve ser positiva"
        )

    rng = random.Random(
        f"quem-faz:v1:{dia.isoformat()}:{quantidade}"
    )

    registros = []

    for indice in range(1, quantidade + 1):

        categoria_id, categoria = rng.choice(
            CATEGORIAS
        )

        status = rng.choices(
            STATUS,
            weights=PESOS_STATUS,
            k=1
        )[0]

        if status == "publicado":
            total_propostas = 0

        elif status == "cancelado":
            total_propostas = rng.randint(0, 2)

        else:
            total_propostas = rng.randint(1, 8)

        hora = rng.randint(6, 22)
        minuto = rng.randint(0, 59)

        registros.append({
            "pedido_id": (
                f"QF-{dia:%Y%m%d}-{indice:05d}"
            ),
            "criado_em": (
                f"{dia.isoformat()}"
                f"T{hora:02d}:{minuto:02d}:00-03:00"
            ),
            "municipio_ibge_id": MUNICIPIO_IBGE,
            "distrito_nome": rng.choice(
                DISTRITOS_EXEMPLO
            ),
            "categoria_id": categoria_id,
            "categoria_nome": categoria,
            "caminho_contratacao": rng.choice([
                "explorar_categoria",
                "publicar_pedido"
            ]),
            "status": status,
            "quantidade_propostas": total_propostas,
            "concluido": status == "concluido",
            "origem": "quem_faz_simulado",
            "simulado": True,
        })

    destino = (
        pasta_chegada(base_dir)
        / f"pedidos_{dia.isoformat()}.jsonl"
    )

    return _gravar_jsonl(destino, registros)


def coletar_distritos_ibge(
    dia: date | None = None,
    base_dir: str | Path | None = None
) -> Path:
    """Coleta distritos reais do IBGE.

    Suporta respostas JSON e GZIP.

    Falha explicitamente se a API estiver indisponível.
    Não substitui dados públicos por dados simulados.
    """

    dia = dia or data_local()

    requisicao = Request(
        IBGE_URL,
        headers={
            "User-Agent": (
                "QuemFaz-Academico/1.0 "
                "(FIAP Global Solution)"
            ),
            "Accept": "application/json",
        }
    )

    erro = None

    for tentativa in range(1, 4):

        try:
            with urlopen(
                requisicao,
                timeout=25
            ) as resposta:

                # Lê os bytes originais da resposta HTTP.
                corpo = resposta.read()

                # Identifica o tipo de compressão informado.
                codificacao = resposta.headers.get(
                    "Content-Encoding", ""
                ).lower()

                # Descomprime caso a resposta seja GZIP.
                # A assinatura também identifica GZIP quando
                # o servidor não informa Content-Encoding.
                if (
                    "gzip" in codificacao
                    or corpo.startswith(b"\x1f\x8b")
                ):
                    corpo = gzip.decompress(corpo)

                # Decodifica UTF-8 e converte para JSON.
                # utf-8-sig também aceita arquivos com BOM.
                conteudo = json.loads(
                    corpo.decode("utf-8-sig")
                )

            # Verifica se a API retornou uma lista válida.
            if (
                not isinstance(conteudo, list)
                or not conteudo
            ):
                raise ValueError(
                    "Resposta inesperada do IBGE: "
                    "lista vazia ou estrutura inválida"
                )

            # Verifica os campos obrigatórios.
            if not all(
                isinstance(item, dict)
                and "id" in item
                and "nome" in item
                for item in conteudo
            ):
                raise ValueError(
                    "Resposta do IBGE sem id ou nome "
                    "em um distrito"
                )

            # Define o arquivo de saída.
            destino = (
                pasta_chegada(base_dir)
                / f"distritos_ibge_{dia.isoformat()}.jsonl"
            )

            # Salva os dados oficiais em JSONL.
            return _gravar_jsonl(
                destino,
                conteudo
            )

        except (
            HTTPError,
            URLError,
            TimeoutError,
            json.JSONDecodeError,
            UnicodeDecodeError,
            OSError
        ) as exc:

            erro = exc

            # Aguarda antes de tentar novamente.
            if tentativa < 3:
                time.sleep(2)

    raise RuntimeError(
        "Coleta real do IBGE falhou "
        f"após 3 tentativas: {erro}"
    )


def conferir_coleta(
    arquivo_ibge: str | Path,
    arquivo_pedidos: str | Path
) -> dict:
    """Valida os arquivos e calcula evidências de integridade.

    Verifica:
    - Existência dos arquivos;
    - Presença de registros;
    - Estrutura dos dados;
    - Identificação dos pedidos simulados;
    - Quantidade de registros;
    - Hash SHA-256.
    """

    resultado = {}

    for nome, arquivo in (
        ("ibge", arquivo_ibge),
        ("pedidos", arquivo_pedidos)
    ):

        caminho = Path(arquivo)

        if (
            not caminho.is_file()
            or caminho.stat().st_size == 0
        ):
            raise FileNotFoundError(
                f"Arquivo ausente ou vazio: {caminho}"
            )

        registros = []

        with caminho.open(
            encoding="utf-8"
        ) as arq:

            for linha in arq:
                if linha.strip():
                    registros.append(
                        json.loads(linha)
                    )

        if not registros:
            raise ValueError(
                f"Arquivo sem registros: {caminho}"
            )

        # Validação da fonte pública.
        if nome == "ibge" and not all(
            "id" in x and "nome" in x
            for x in registros
        ):
            raise ValueError(
                "Arquivo IBGE em formato inesperado"
            )

        # Validação da fonte sintética.
        if nome == "pedidos" and not all(
            x.get("simulado") is True
            and "pedido_id" in x
            for x in registros
        ):
            raise ValueError(
                "Pedidos precisam estar "
                "identificados como sintéticos"
            )

        # Evidências utilizadas no pipeline.
        resultado[nome] = {
            "arquivo": caminho.name,
            "registros": len(registros),
            "sha256": hashlib.sha256(
                caminho.read_bytes()
            ).hexdigest(),
        }

    return resultado
