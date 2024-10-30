import random

class Boss:
    def __init__(self, hp):
        self.hp = hp

    def receber_dano(self, dano):
        self.hp -= dano
        if self.hp <= 0:
            return True  # O boss foi derrotado
        return False

    def contra_atacar(self):
        # Chance de contra-atacar ou roubar o prêmio
        chance = random.random()
        if chance < 0.2:
            return "contra_atacar"
        elif chance < 0.3:
            return "roubar_premio"
        return None
