"""Testes locais SEM rede. O teste da API real é feito durante a execução."""
import json
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from quem_faz.pipeline import gerar_pedidos_sinteticos, conferir_coleta


class TesteFonteSimulada(unittest.TestCase):
    def test_geracao_reprodutivel_e_identificada(self):
        with tempfile.TemporaryDirectory() as tmp:
            dia = date(2026, 11, 10)
            arquivo = gerar_pedidos_sinteticos(dia, 120, tmp)
            dados = arquivo.read_bytes()
            registros = [json.loads(x) for x in dados.decode().splitlines()]
            self.assertEqual(len(registros), 120)
            self.assertEqual(len({x["pedido_id"] for x in registros}), 120)
            self.assertTrue(all(x["simulado"] is True for x in registros))
            self.assertTrue(all(x["concluido"] == (x["status"] == "concluido") for x in registros))
            self.assertTrue(all(x["quantidade_propostas"] >= 1 for x in registros if x["status"] in ("contratado", "concluido", "com_propostas")))
            arquivo2 = gerar_pedidos_sinteticos(dia, 120, tmp)
            self.assertEqual(dados, arquivo2.read_bytes())

    def test_conferencia_usa_arquivo_mock_apenas_no_teste(self):
        with tempfile.TemporaryDirectory() as tmp:
            arquivo_pedidos = gerar_pedidos_sinteticos(date(2026, 11, 10), 10, tmp)
            arquivo_ibge_mock = Path(tmp) / "ibge_mock_APENAS_TESTE.jsonl"
            arquivo_ibge_mock.write_text(json.dumps({"id": 123456, "nome": "Distrito fictício (mock)"}) + "\n", encoding="utf-8")
            resultado = conferir_coleta(arquivo_ibge_mock, arquivo_pedidos)
            self.assertEqual(resultado["ibge"]["registros"], 1)
            self.assertEqual(resultado["pedidos"]["registros"], 10)


if __name__ == "__main__":
    unittest.main()
