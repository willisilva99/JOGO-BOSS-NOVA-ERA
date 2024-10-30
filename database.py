import psycopg2
from psycopg2 import sql

class Database:
    def __init__(self, db_url):
        self.db_url = db_url
        self.conn = None

    def connect(self):
        """Estabelece a conexão com o banco de dados."""
        try:
            self.conn = psycopg2.connect(self.db_url)
            self.conn.autocommit = True  # Ativa o autocommit para evitar chamadas de commit explícitas
            print("Conexão com o banco de dados estabelecida.")
        except psycopg2.Error as e:
            print(f"Erro ao conectar ao banco de dados: {e}")
            self.conn = None  # Assegura que conn seja None se a conexão falhar

    def setup(self):
        """Configura a tabela jogadores no banco de dados."""
        with self.conn.cursor() as cur:
            cur.execute("""
            CREATE TABLE IF NOT EXISTS jogadores (
                id SERIAL PRIMARY KEY,
                player_id BIGINT UNIQUE NOT NULL,
                dano_total INT DEFAULT 0
            );
            """)

    def add_dano(self, player_id, dano):
        """Adiciona dano ao jogador no banco de dados."""
        if dano < 0:
            print("O dano não pode ser negativo.")
            return

        with self.conn.cursor() as cur:
            cur.execute("""
            INSERT INTO jogadores (player_id, dano_total)
            VALUES (%s, %s)
            ON CONFLICT (player_id) DO UPDATE
            SET dano_total = jogadores.dano_total + EXCLUDED.dano_total;
            """, (player_id, dano))
            print(f"Dano de {dano} adicionado para o jogador {player_id}.")

    def get_top_danos(self, limit=3):
        """Retorna os jogadores com os maiores danos acumulados."""
        with self.conn.cursor() as cur:
            cur.execute("""
            SELECT player_id, dano_total FROM jogadores
            ORDER BY dano_total DESC
            LIMIT %s;
            """, (limit,))
            top_danos = cur.fetchall()
            print(f"Top {limit} jogadores: {top_danos}")
            return top_danos

    def close(self):
        """Fecha a conexão com o banco de dados."""
        if self.conn:
            self.conn.close()
            print("Conexão com o banco de dados fechada.")
