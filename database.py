import psycopg2
from psycopg2 import sql

class Database:
    def __init__(self, db_url):
        self.conn = psycopg2.connect(db_url)
        self.cur = self.conn.cursor()

    def setup(self):
        # Criação da tabela de jogadores e danos se não existir
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS jogadores (
            id SERIAL PRIMARY KEY,
            player_id BIGINT UNIQUE NOT NULL,
            dano_total INT DEFAULT 0
        );
        """)
        self.conn.commit()

    def add_dano(self, player_id, dano):
        # Adiciona dano ao jogador, criando um registro caso ainda não exista
        self.cur.execute("""
        INSERT INTO jogadores (player_id, dano_total)
        VALUES (%s, %s)
        ON CONFLICT (player_id) DO UPDATE
        SET dano_total = jogadores.dano_total + EXCLUDED.dano_total;
        """, (player_id, dano))
        self.conn.commit()

    def get_top_danos(self, limit=3):
        # Pega os top jogadores em dano
        self.cur.execute("""
        SELECT player_id, dano_total FROM jogadores
        ORDER BY dano_total DESC
        LIMIT %s;
        """, (limit,))
        return self.cur.fetchall()

    def close(self):
        self.cur.close()
        self.conn.close()
