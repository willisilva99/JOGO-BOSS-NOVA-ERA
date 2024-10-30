class Boss:
    def __init__(self, hp):
        self.hp = hp

    def receber_dano(self, dano):
        self.hp -= dano
        if self.hp <= 0:
            return True  # O boss foi derrotado
        return False

    def contra_atacar(self):
        # Aqui você pode adicionar lógica para o contra-ataque
        pass
