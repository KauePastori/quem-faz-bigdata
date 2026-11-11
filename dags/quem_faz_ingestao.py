"""DAG FIAP 2026.2: duas fontes em paralelo + conferência dos arquivos.

Usar com Airflow 3 (airflow.sdk) e PYTHONPATH=/opt/airflow/src.
"""
from datetime import timedelta

import pendulum
from airflow.sdk import dag, task


@dag(
    dag_id="quem_faz_coleta_diaria",
    description="Coleta a API real do IBGE e gera pedidos sintéticos para o MVP Quem Faz",
    schedule="@daily",
    start_date=pendulum.datetime(2026, 11, 10, tz="America/Sao_Paulo"),
    catchup=False,
    max_active_runs=1,
    default_args={"retries": 1, "retry_delay": timedelta(minutes=2)},
    tags=["fiap", "citizentech", "quem-faz", "big-data"],
)
def quem_faz_coleta_diaria():
    @task(task_id="coletar_ibge_real")
    def coletar_ibge():
        from quem_faz.pipeline import coletar_distritos_ibge
        return str(coletar_distritos_ibge())

    @task(task_id="gerar_pedidos_sinteticos")
    def gerar_pedidos():
        from quem_faz.pipeline import gerar_pedidos_sinteticos
        return str(gerar_pedidos_sinteticos())

    @task(task_id="conferir_arquivos")
    def conferir(ibge: str, pedidos: str):
        from quem_faz.pipeline import conferir_coleta
        import json
        resultado = conferir_coleta(ibge, pedidos)
        print(json.dumps(resultado, ensure_ascii=False, indent=2))
        return resultado

    # Duas tarefas paralelas; a conferência começa após ambas concluírem.
    conferir(coletar_ibge(), gerar_pedidos())


quem_faz_coleta_diaria()
