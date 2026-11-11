import tempfile
import unittest
from pathlib import Path

from mvp.validacao import DadosInvalidos, ler_categorias, resumir


class TesteMVP(unittest.TestCase):
    def test_csv_exportado(self):
        arquivo = Path(__file__).resolve().parents[1] / 'dados' / 'categorias_publicas.csv'
        rows = ler_categorias(arquivo)
        self.assertEqual(len(rows), 6)
        self.assertEqual(resumir(rows)['total_pedidos'], 200)
        self.assertEqual(resumir(rows)['pedidos_com_proposta'], 141)
        self.assertEqual(resumir(rows)['pedidos_contratados'], 95)
        self.assertEqual(resumir(rows)['servicos_concluidos'], 51)

    def test_rejeita_origem_nao_simulada(self):
        arquivo = Path(__file__).resolve().parents[1] / 'dados' / 'categorias_publicas.csv'
        texto = arquivo.read_text(encoding='utf-8-sig').replace('DADOS SIMULADOS', 'DADOS REAIS')
        with tempfile.TemporaryDirectory() as pasta:
            caminho = Path(pasta) / 'teste.csv'
            caminho.write_text(texto, encoding='utf-8')
            with self.assertRaises(DadosInvalidos):
                ler_categorias(caminho)

    def test_rejeita_taxa_incorreta(self):
        arquivo = Path(__file__).resolve().parents[1] / 'dados' / 'categorias_publicas.csv'
        texto = arquivo.read_text(encoding='utf-8-sig').replace('25.58', '99.99', 1)
        with tempfile.TemporaryDirectory() as pasta:
            caminho = Path(pasta) / 'teste.csv'
            caminho.write_text(texto, encoding='utf-8')
            with self.assertRaises(DadosInvalidos):
                ler_categorias(caminho)

if __name__ == '__main__':
    unittest.main()
