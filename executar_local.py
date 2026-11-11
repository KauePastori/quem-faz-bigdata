"""Executor local da fase 1 (sem depender de Airflow ou bibliotecas extras)."""

import argparse
import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))
from quem_faz.pipeline import (  # noqa: E402
    coletar_distritos_ibge, conferir_coleta, data_local, gerar_pedidos_sinteticos,
)


def main():
    parser = argparse.ArgumentParser(description="Testes iniciais das fontes de dados Quem Faz")
    parser.add_argument("modo", choices=["pedidos", "ibge", "todos"])
    parser.add_argument("--data", default=data_local().isoformat(), help="YYYY-MM-DD")
    parser.add_argument("--quantidade", type=int, default=100)
    args = parser.parse_args()
    dia = date.fromisoformat(args.data)
    try:
        pedidos = gerar_pedidos_sinteticos(dia, args.quantidade) if args.modo in ("pedidos", "todos") else None
        ibge = coletar_distritos_ibge(dia) if args.modo in ("ibge", "todos") else None
        if pedidos:
            print(f"[OK] Fonte INTERNA SIMULADA: {pedidos}")
        if ibge:
            print(f"[OK] Fonte EXTERNA REAL (IBGE): {ibge}")
        if pedidos and ibge:
            print("[OK] Conferência:", json.dumps(conferir_coleta(ibge, pedidos), ensure_ascii=False, indent=2))
    except Exception as exc:
        print(f"[ERRO] {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
