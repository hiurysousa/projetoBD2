from fastapi import FastAPI, HTTPException
import sqlite3
import threading
import time

app = FastAPI()

DB_NAME = "loja_carros.db"


# ----------------- Funções de Banco de Dados (Replicadas do setup) -----------------

def create_db_fastapi():
    """Inicializa o banco de dados com a estrutura e dados iniciais."""
    conn = sqlite3.connect(DB_NAME, timeout=5)
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS Veiculos (
            VeiculoID INTEGER PRIMARY KEY,
            Modelo TEXT,
            Status TEXT
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS Vendas (
            VendaID INTEGER PRIMARY KEY AUTOINCREMENT,
            VeiculoID INTEGER,
            Comprador TEXT
        )
    ''')

    # Limpar e inserir o carro crítico (ID 101) para a simulação
    c.execute("DELETE FROM Veiculos")
    c.execute("DELETE FROM Vendas")
    c.execute("INSERT INTO Veiculos (VeiculoID, Modelo, Status) VALUES (101, 'Fusca 1970', 'Disponivel')")
    c.execute("INSERT INTO Veiculos (VeiculoID, Modelo, Status) VALUES (200, 'Ford Ka', 'Disponivel')")

    conn.commit()
    conn.close()


def attempt_sale_transaction_thread(thread_id, veiculo_id, comprador_nome):
    """Função para ser executada em threads, simulando a concorrência na API."""
    conn = sqlite3.connect(DB_NAME, timeout=1)  # Timeout de 1 segundo
    c = conn.cursor()

    try:
        # Início da Transação explícita com bloqueio imediato
        c.execute('BEGIN IMMEDIATE;')
        print(f"Thread {thread_id} ({comprador_nome}): Transação iniciada.")

        # 1. Verificar disponibilidade
        c.execute("SELECT Status FROM Veiculos WHERE VeiculoID = ? AND Status = 'Disponivel'", (veiculo_id,))
        veiculo = c.fetchone()

        if not veiculo:
            print(f"Thread {thread_id}: Falha! Veículo {veiculo_id} já vendido.")
            raise Exception("Veículo não disponível.")

        # Simula o tempo de espera do processo (Condição de Corrida)
        time.sleep(3 if thread_id == 1 else 1)

        # 2. Atualizar Status e 3. Registrar Venda
        c.execute("UPDATE Veiculos SET Status = 'Reservado' WHERE VeiculoID = ?", (veiculo_id,))
        c.execute("INSERT INTO Vendas (VeiculoID, Comprador) VALUES (?, ?)", (veiculo_id, comprador_nome))
        c.execute("UPDATE Veiculos SET Status = 'Vendido' WHERE VeiculoID = ?", (veiculo_id,))

        conn.commit()
        print(f"Thread {thread_id}: SUCESSO! COMMIT realizado.")

    except sqlite3.OperationalError as e:
        print(f"Thread {thread_id}: ERRO OPERACIONAL de BLOQUEIO: {e}. ROLLBACK implícito.")
    except Exception as e:
        print(f"Thread {thread_id}: ERRO LÓGICO: {e}. ROLLBACK implícito.")
    finally:
        conn.close()


# ----------------- ROTAS FASTAPI -----------------

@app.post("/init-db")
def init_db():
    """Inicializa o banco de dados e as tabelas para a simulação."""
    try:
        create_db_fastapi()
        return {"status": "ok",
                "message": "Banco de dados de carros inicializado. Carro ID 101 disponível para concorrência."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao inicializar o DB: {e}")


@app.post("/simulate-concurrent-sale")
def simulate_concurrent_sale():
    """
    Simula dois processos (threads) tentando vender o mesmo carro (ID 101) ao mesmo tempo,
    demonstrando o controle de concorrência.
    """
    VEICULO_ID = 101

    thread1 = threading.Thread(target=attempt_sale_transaction_thread, args=(1, VEICULO_ID, 'Vendedor X'))
    thread2 = threading.Thread(target=attempt_sale_transaction_thread, args=(2, VEICULO_ID, 'Vendedor Y'))

    # Iniciando as transações concorrentes
    thread1.start()
    thread2.start()

    # Esperando a conclusão das transações
    thread1.join()
    thread2.join()

    return {"status": "ok",
            "message": f"Simulação de concorrência concluída para Veículo {VEICULO_ID}. Cheque o console e a rota /veiculos."}


@app.get("/veiculos")
def get_veiculos():
    """Retorna todos os veículos e seus status."""
    conn = sqlite3.connect(DB_NAME, timeout=5)
    c = conn.cursor()
    c.execute("SELECT VeiculoID, Modelo, Status FROM Veiculos")
    rows = c.fetchall()
    conn.close()
    return {"veiculos": rows}


@app.get("/vendas")
def get_vendas():
    """Retorna o registro de vendas."""
    conn = sqlite3.connect(DB_NAME, timeout=5)
    c = conn.cursor()
    c.execute("SELECT VendaID, VeiculoID, Comprador FROM Vendas")
    rows = c.fetchall()
    conn.close()
    return {"vendas": rows}