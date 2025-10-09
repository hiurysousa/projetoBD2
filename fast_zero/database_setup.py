import sqlite3
import threading
import time

DB_NAME = "loja_carros.db"


# ----------------- 1. Funções de Banco de Dados -----------------

def create_db():
    """Cria o banco de dados e insere um carro de teste."""
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

    # Limpar dados e inserir um carro popular para simular a concorrência
    c.execute("DELETE FROM Veiculos")
    c.execute("DELETE FROM Vendas")
    c.execute("INSERT INTO Veiculos (VeiculoID, Modelo, Status) VALUES (101, 'Fusca 1970', 'Disponivel')")

    conn.commit()
    conn.close()
    print(f"Banco de dados '{DB_NAME}' inicializado com 1 Fusca Disponível.")


def attempt_sale_transaction(thread_id, veiculo_id, comprador_nome):
    """
    Simula uma transação de venda que tenta garantir Atomicidade e Isolamento.
    Usa BEGIN IMMEDIATE para forçar o bloqueio imediato do arquivo/banco.
    """
    conn = sqlite3.connect(DB_NAME, timeout=2)  # Timeout curto para forçar falha mais rápido
    c = conn.cursor()

    try:
        # Início da Transação explícita
        c.execute('BEGIN IMMEDIATE;')
        print(f"[{comprador_nome}]: Transação iniciada e recurso bloqueado (BEGIN IMMEDIATE).")

        # 1. Verificar disponibilidade (e aplicar bloqueio, implícito no IMMEDIATE)
        c.execute("SELECT Status FROM Veiculos WHERE VeiculoID = ? AND Status = 'Disponivel'", (veiculo_id,))
        veiculo = c.fetchone()

        if not veiculo:
            print(f"[{comprador_nome}]: Falha! Veículo {veiculo_id} já não está disponível.")
            raise Exception("Veículo não disponível.")

        # Simula o tempo que o vendedor leva para preencher o contrato (Tempo de Concorrência)
        print(f"[{comprador_nome}]: Verificou disponibilidade. Aguardando...")
        time.sleep(3 if thread_id == 1 else 1)  # Vendedor A é mais lento para forçar o conflito

        # 2. Atualizar o Status (Bloqueio)
        c.execute("UPDATE Veiculos SET Status = 'Reservado' WHERE VeiculoID = ?", (veiculo_id,))

        # 3. Registrar a Venda
        c.execute("INSERT INTO Vendas (VeiculoID, Comprador) VALUES (?, ?)", (veiculo_id, comprador_nome))

        # 4. Finalizar o Status
        c.execute("UPDATE Veiculos SET Status = 'Vendido' WHERE VeiculoID = ?", (veiculo_id,))

        # Fim da Transação: Se tudo deu certo, COMMIT (Atomicidade)
        conn.commit()
        print(f"[{comprador_nome}]: SUCESSO! Transação FINALIZADA com COMMIT.")

    except sqlite3.OperationalError as e:
        # Se ocorrer um erro operacional (ex: Database is locked), o SGBD previne o deadlock
        print(f"[{comprador_nome}]: ERRO OPERACIONAL: {e}. Transação cancelada (ROLLBACK implícito).")
    except Exception as e:
        # Outros erros de lógica (ex: Veículo não disponível)
        print(f"[{comprador_nome}]: ERRO LÓGICO: {e}. Transação cancelada (ROLLBACK implícito).")
    finally:
        conn.close()


# ----------------- 2. Simulação -----------------

if __name__ == '__main__':
    create_db()

    VEICULO_ID_CRITICO = 101

    # Simular dois vendedores (threads) tentando vender o mesmo carro
    thread1 = threading.Thread(target=attempt_sale_transaction, args=(1, VEICULO_ID_CRITICO, 'Comprador A - Thread 1'))
    thread2 = threading.Thread(target=attempt_sale_transaction, args=(2, VEICULO_ID_CRITICO, 'Comprador B - Thread 2'))

    print("\n--- INÍCIO DA SIMULAÇÃO DE VENDA CONCORRENTE ---")
    thread1.start()
    thread2.start()

    thread1.join()
    thread2.join()
    print("--- FIM DA SIMULAÇÃO ---")

    # 3. Verificar o resultado final
    conn = sqlite3.connect(DB_NAME, timeout=5)
    c = conn.cursor()

    print("\n--- RESULTADO FINAL DO BANCO DE DADOS ---")

    c.execute("SELECT * FROM Veiculos WHERE VeiculoID = ?", (VEICULO_ID_CRITICO,))
    print("Veículo:", c.fetchone())

    c.execute("SELECT * FROM Vendas")
    print("Vendas Registradas:")
    for row in c.fetchall():
        print(f"  Venda ID: {row[0]}, Veículo ID: {row[1]}, Comprador: {row[2]}")

    conn.close()