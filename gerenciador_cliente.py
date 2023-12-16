import sqlite3

class Cliente:
    def __init__(self, nome, email):
        self.nome = nome
        self.email = email

    def exibir_informacoes(self):
        print(f'Nome: {self.nome}, Email: {self.email}')

def criar_tabela_clientes(conn):
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
            nome TEXT PRIMARY KEY,
            email TEXT
        )
    ''')
    conn.commit()
 

def criar_banco_dados():
    conexao = sqlite3.connect('gerenciador_vendas.db')
    cursor = conexao.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            preco REAL NOT NULL,
            estoque INTEGER NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pedidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente TEXT NOT NULL,
            produto_id INTEGER NOT NULL,
            quantidade INTEGER NOT NULL,
            data_pedido DATE DEFAULT CURRENT_DATE,
            FOREIGN KEY (produto_id) REFERENCES produtos (id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
            nome TEXT PRIMARY KEY,
            email TEXT
        )
    ''')

    conexao.commit()
    conexao.close()


def adicionar_produto(nome, preco, estoque):
    conexao = sqlite3.connect('gerenciador_vendas.db')
    cursor = conexao.cursor()

    cursor.execute('INSERT INTO produtos (nome, preco, estoque) VALUES (?, ?, ?)', (nome, preco, estoque))

    conexao.commit()
    conexao.close()


def receber_pedido(cliente, produto_id, quantidade):
    conexao = sqlite3.connect('gerenciador_vendas.db')
    cursor = conexao.cursor()

    cursor.execute('INSERT INTO pedidos (cliente, produto_id, quantidade) VALUES (?, ?, ?)', (cliente, produto_id, quantidade))

   
    cursor.execute('UPDATE produtos SET estoque = estoque - ? WHERE id = ?', (quantidade, produto_id))

    conexao.commit()
    conexao.close()


def relatorio_produtos_mais_vendidos():
    conexao = sqlite3.connect('gerenciador_vendas.db')
    cursor = conexao.cursor()

    cursor.execute('''
        SELECT produtos.nome, SUM(pedidos.quantidade) as total_vendido
        FROM pedidos
        JOIN produtos ON pedidos.produto_id = produtos.id
        GROUP BY produtos.nome
        ORDER BY total_vendido DESC
    ''')

    resultados = cursor.fetchall()

    for resultado in resultados:
        print(f'{resultado[0]}: {resultado[1]} unidades vendidas')

    conexao.close()


def relatorio_produto_por_cliente(cliente):
    conexao = sqlite3.connect('gerenciador_vendas.db')
    cursor = conexao.cursor()

    cursor.execute('''
        SELECT produtos.nome, pedidos.quantidade, pedidos.data_pedido
        FROM pedidos
        JOIN produtos ON pedidos.produto_id = produtos.id
        WHERE pedidos.cliente = ?
    ''', (cliente,))

    resultados = cursor.fetchall()

    for resultado in resultados:
        print(f'{resultado[0]}: {resultado[1]} unidades em {resultado[2]}')

    conexao.close()


def relatorio_consumo_medio_cliente(cliente):
    conexao = sqlite3.connect('gerenciador_vendas.db')
    cursor = conexao.cursor()

    cursor.execute('SELECT AVG(quantidade) FROM pedidos WHERE cliente = ?', (cliente,))

    resultado = cursor.fetchone()

    if resultado[0] is not None:
        print(f'Consumo médio do cliente {cliente}: {resultado[0]} unidades por pedido')
    else:
        print(f'Cliente {cliente} não possui pedidos registrados.')

    conexao.close()


def relatorio_produto_baixo_estoque(estoque_minimo):
    conexao = sqlite3.connect('gerenciador_vendas.db')
    cursor = conexao.cursor()

    cursor.execute('SELECT * FROM produtos WHERE estoque < ?', (estoque_minimo,))

    resultados = cursor.fetchall()

    for resultado in resultados:
        print(f'{resultado[1]} está com estoque baixo ({resultado[3]} unidades)')

    conexao.close()


def menu_gerenciador_vendas(conn):
    while True:
        print('\n=== Menu ===')
        print('1. Adicionar Produto')
        print('2. Receber Pedido de Compra')
        print('3. Relatório de Produtos Mais Vendidos')
        print('4. Relatório de Produto por Cliente')
        print('5. Relatório de Consumo Médio do Cliente')
        print('6. Relatório de Produto com Baixo Estoque')
        print('7. Menu de Clientes')
        print('0. Sair')

        escolha = input('Escolha uma opção: ')

        if escolha == '1':
            nome = input('Nome do produto: ')
            preco = float(input('Preço do produto: '))
            estoque = int(input('Quantidade em estoque: '))
            adicionar_produto(nome, preco, estoque)
        elif escolha == '2':
            cliente = input('Nome do cliente: ')
            produto_id = int(input('ID do produto: '))
            quantidade = int(input('Quantidade desejada: '))
            receber_pedido(cliente, produto_id, quantidade)
        elif escolha == '3':
            relatorio_produtos_mais_vendidos()
        elif escolha == '4':
            cliente = input('Nome do cliente: ')
            relatorio_produto_por_cliente(cliente)
        elif escolha == '5':
            cliente = input('Nome do cliente: ')
            relatorio_consumo_medio_cliente(cliente)
        elif escolha == '6':
            estoque_minimo = int(input('Quantidade mínima em estoque: '))
            relatorio_produto_baixo_estoque(estoque_minimo)
        elif escolha == '7':
            menu_clientes(conn)
        elif escolha == '0':
            break
        else:
            print('Opção inválida. Tente novamente.')


def menu_clientes(conn):
    criar_tabela_clientes(conn)

    while True:
        print('\nMenu de Clientes:')
        print('1. Criar Cliente')
        print('2. Exibir Clientes')
        print('3. Atualizar Cliente')
        print('4. Excluir Cliente')
        print('5. Voltar ao Menu Principal')
        print('0. Sair')

        escolha = input('Digite o número da operação desejada: ')

        if escolha == '1':
            criar_cliente(conn)
        elif escolha == '2':
            exibir_clientes(conn)
        elif escolha == '3':
            atualizar_cliente(conn)
        elif escolha == '4':
            excluir_cliente(conn)
        elif escolha == '5':
            break
        elif escolha == '0':
            print('Saindo do programa. Até logo!')
            exit()
        else:
            print('Escolha inválida. Por favor, escolha uma opção válida.')


def criar_cliente(conn):
    nome = input('Digite o nome do cliente: ')
    email = input('Digite o email do cliente: ')

    cursor = conn.cursor()
    cursor.execute('INSERT OR REPLACE INTO clientes (nome, email) VALUES (?, ?)', (nome, email))
    conn.commit()

    print(f'Cliente {nome} criado com sucesso.')


def exibir_clientes(conn):
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM clientes')

    print('Informações dos Clientes:')
    for row in cursor.fetchall():
        cliente = Cliente(row[0], row[1])
        cliente.exibir_informacoes()
        print('-' * 30)


def atualizar_cliente(conn):
    nome_cliente = input('Digite o nome do cliente que deseja atualizar: ')

    cursor = conn.cursor()
    cursor.execute('SELECT * FROM clientes WHERE nome = ?', (nome_cliente,))
    resultado = cursor.fetchone()

    if resultado:
        cliente = Cliente(resultado[0], resultado[1])
        novo_nome = input('Digite o novo nome (ou deixe em branco para manter o mesmo): ')
        novo_email = input('Digite o novo email (ou deixe em branco para manter o mesmo): ')

        if novo_nome:
            cliente.nome = novo_nome
        if novo_email:
            cliente.email = novo_email

        cursor.execute('INSERT OR REPLACE INTO clientes (nome, email) VALUES (?, ?)', (cliente.nome, cliente.email))
        conn.commit()

        print('Cliente atualizado com sucesso.')
    else:
        print('Cliente não encontrado.')


def excluir_cliente(conn):
    nome_cliente = input('Digite o nome do cliente que deseja excluir: ')

    cursor = conn.cursor()
    cursor.execute('DELETE FROM clientes WHERE nome = ?', (nome_cliente,))
    conn.commit()

    print(f'Cliente {nome_cliente} removido com sucesso.')


if __name__ == '__main__':
    conn = sqlite3.connect('gerenciador_vendas.db')
    criar_banco_dados()
    menu_gerenciador_vendas(conn)
    conn.close()
