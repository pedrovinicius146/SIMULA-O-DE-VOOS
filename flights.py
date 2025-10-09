import random
import math
from datetime import datetime
import matplotlib.pyplot as plt

custo_espera = 20  

def converte_minutos(hora):
    h, m = map(int, hora.split(':'))
    return h * 60 + m

voos_disponiveis = {}
with open("flights.txt") as arquivo:
    for linha in arquivo:
        origem, destino, saida, chegada, preco = linha.strip().split(',')
        voos_disponiveis.setdefault((origem, destino), [])
        voos_disponiveis[(origem, destino)].append((converte_minutos(saida), converte_minutos(chegada), int(preco)))

pessoas_lista = [
    ('Lisboa', 'LIS'),
    ('Madrid', 'MAD'),
    ('Paris', 'CDG'),
    ('Dublin', 'DUB'),
    ('Bruxelas', 'BRU'),
    ('Londres', 'LHR')
]
destino_viagem = 'FCO'


# ============================================================
# FUNÇÃO DE CÁLCULO DE CUSTO TOTAL
# ============================================================

def calcula_custo(agenda):
    total_passagens = 0
    chegadas_destino = []
    partidas_destino = []

    for i in range(len(pessoas_lista)):
        codigo_origem = pessoas_lista[i][1]

        idx_ida = agenda[i * 2]
        voo_ida = voos_disponiveis[(codigo_origem, destino_viagem)][idx_ida]
        total_passagens += voo_ida[2]
        chegadas_destino.append(voo_ida[1])

        idx_volta = agenda[i * 2 + 1]
        voo_volta = voos_disponiveis[(destino_viagem, codigo_origem)][idx_volta]
        total_passagens += voo_volta[2]
        partidas_destino.append(voo_volta[0])

    ultima_chegada = max(chegadas_destino)
    espera_ida = sum((ultima_chegada - h) / 60 * custo_espera for h in chegadas_destino)

    primeira_partida = min(partidas_destino)
    espera_volta = sum((h - primeira_partida) / 60 * custo_espera for h in partidas_destino)

    return total_passagens + espera_ida + espera_volta


# ============================================================
# HILL CLIMB
# ============================================================

def hill_climb(max_iter=1000):
    solucao_atual = []
    for pessoa in pessoas_lista:
        solucao_atual.append(random.randint(0, len(voos_disponiveis[(pessoa[1], destino_viagem)]) - 1))
        solucao_atual.append(random.randint(0, len(voos_disponiveis[(destino_viagem, pessoa[1])]) - 1))

    melhor_custo = calcula_custo(solucao_atual)
    historico = [melhor_custo]

    for _ in range(max_iter):
        nova_solucao = solucao_atual[:]
        i = random.randint(0, len(solucao_atual) - 1)
        pessoa_idx = i // 2
        if i % 2 == 0:
            nova_solucao[i] = random.randint(0, len(voos_disponiveis[(pessoas_lista[pessoa_idx][1], destino_viagem)]) - 1)
        else:
            nova_solucao[i] = random.randint(0, len(voos_disponiveis[(destino_viagem, pessoas_lista[pessoa_idx][1])]) - 1)

        custo_novo = calcula_custo(nova_solucao)
        if custo_novo < melhor_custo:
            solucao_atual, melhor_custo = nova_solucao, custo_novo
        historico.append(melhor_custo)

    return solucao_atual, melhor_custo, historico


# ============================================================
# RECOZIMENTO SIMULADO
# ============================================================

def recozimento_simulado(temp_inicial=10000.0, taxa_resfriamento=0.95):
    solucao_atual = []
    for pessoa in pessoas_lista:
        solucao_atual.append(random.randint(0, len(voos_disponiveis[(pessoa[1], destino_viagem)]) - 1))
        solucao_atual.append(random.randint(0, len(voos_disponiveis[(destino_viagem, pessoa[1])]) - 1))

    melhor_custo = calcula_custo(solucao_atual)
    historico = [melhor_custo]

    temp = temp_inicial
    while temp > 0.1:
        nova_solucao = solucao_atual[:]
        i = random.randint(0, len(solucao_atual) - 1)
        pessoa_idx = i // 2
        if i % 2 == 0:
            nova_solucao[i] = random.randint(0, len(voos_disponiveis[(pessoas_lista[pessoa_idx][1], destino_viagem)]) - 1)
        else:
            nova_solucao[i] = random.randint(0, len(voos_disponiveis[(destino_viagem, pessoas_lista[pessoa_idx][1])]) - 1)

        custo_novo = calcula_custo(nova_solucao)
        if custo_novo < melhor_custo or random.random() < math.exp(-(custo_novo - melhor_custo) / temp):
            solucao_atual, melhor_custo = nova_solucao, custo_novo
        historico.append(melhor_custo)
        temp *= taxa_resfriamento

    return solucao_atual, melhor_custo, historico


# ============================================================
# GENÉTICO
# ============================================================

def genetico(qtd_pop=50, qtd_elite=10, qtd_geracoes=100):
    def cria_individuo():
        ind = []
        for pessoa in pessoas_lista:
            ind.append(random.randint(0, len(voos_disponiveis[(pessoa[1], destino_viagem)]) - 1))
            ind.append(random.randint(0, len(voos_disponiveis[(destino_viagem, pessoa[1])]) - 1))
        return ind

    populacao = [cria_individuo() for _ in range(qtd_pop)]

    for _ in range(qtd_geracoes):
        avaliacoes = [(calcula_custo(ind), ind) for ind in populacao]
        avaliacoes.sort()
        elite = [ind for _, ind in avaliacoes[:qtd_elite]]

        filhos = []
        while len(filhos) < qtd_pop - qtd_elite:
            pai1, pai2 = random.sample(elite, 2)
            corte = random.randint(1, len(pessoas_lista) * 2 - 2)
            filho = pai1[:corte] + pai2[corte:]
            if random.random() < 0.1:
                i = random.randint(0, len(filho) - 1)
                pessoa_idx = i // 2
                if i % 2 == 0:
                    filho[i] = random.randint(0, len(voos_disponiveis[(pessoas_lista[pessoa_idx][1], destino_viagem)]) - 1)
                else:
                    filho[i] = random.randint(0, len(voos_disponiveis[(destino_viagem, pessoas_lista[pessoa_idx][1])]) - 1)
            filhos.append(filho)

        populacao = elite + filhos

    melhor_custo, melhor_solucao = min(
        [(calcula_custo(ind), ind) for ind in populacao], key=lambda x: x[0]
    )
    return melhor_solucao, melhor_custo


# ============================================================
# EXECUÇÃO
# ============================================================

sol_hill, custo_hill, hist_hill = hill_climb()
sol_annealing, custo_annealing, hist_annealing = recozimento_simulado()
sol_gen, custo_gen = genetico()

print("=== RESULTADOS ===")
print(f"Hill Climb: {custo_hill:.2f}")
print(f"Recozimento Simulado: {custo_annealing:.2f}")
print(f"Genético: {custo_gen:.2f}")


# ============================================================
# GRÁFICOS
# ============================================================

algoritmos = ['Hill Climb', 'Recozimento Simulado', 'Genético']
custos = [custo_hill, custo_annealing, custo_gen]

plt.figure(figsize=(8,5))
plt.bar(algoritmos, custos, color=['#4CAF50', '#2196F3', '#FF9800'])
plt.title('Comparação de Custos')
plt.ylabel('Custo (€)')
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show()

plt.figure(figsize=(9,5))
plt.plot(hist_hill, label='Hill Climb', color='#4CAF50')
plt.plot(hist_annealing, label='Recozimento Simulado', color='#2196F3')
plt.title('Evolução do Custo')
plt.xlabel('Iterações')
plt.ylabel('Custo (€)')
plt.legend()
plt.grid(True, linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show()


# ============================================================
# MOSTRAR SOLUÇÃO
# ============================================================

def mostra_solucao(solucao):
    for i, pessoa in enumerate(pessoas_lista):
        ida = voos_disponiveis[(pessoa[1], destino_viagem)][solucao[i * 2]]
        volta = voos_disponiveis[(destino_viagem, pessoa[1])][solucao[i * 2 + 1]]
        print(f"{pessoa[0]}: Ida {ida[0]//60:02d}:{ida[0]%60:02d}→{ida[1]//60:02d}:{ida[1]%60:02d} ({ida[2]}€) | Volta {volta[0]//60:02d}:{volta[0]%60:02d}→{volta[1]//60:02d}:{volta[1]%60:02d} ({volta[2]}€)")

print("\n--- Hill Climb ---")
mostra_solucao(sol_hill)
print("\n--- Recozimento Simulado ---")
mostra_solucao(sol_annealing)
print("\n--- Genético ---")
mostra_solucao(sol_gen)


# ============================================================
# HISTÓRICO DO GENÉTICO
# ============================================================

def historico_genetico(qtd_pop=50, qtd_elite=10, qtd_geracoes=100):
    def cria_individuo():
        ind = []
        for pessoa in pessoas_lista:
            ind.append(random.randint(0, len(voos_disponiveis[(pessoa[1], destino_viagem)]) - 1))
            ind.append(random.randint(0, len(voos_disponiveis[(destino_viagem, pessoa[1])]) - 1))
        return ind

    populacao = [cria_individuo() for _ in range(qtd_pop)]
    historico = []

    for _ in range(qtd_geracoes):
        avaliacoes = [(calcula_custo(ind), ind) for ind in populacao]
        avaliacoes.sort()
        elite = [ind for _, ind in avaliacoes[:qtd_elite]]
        historico.append(avaliacoes[0][0])

        filhos = []
        while len(filhos) < qtd_pop - qtd_elite:
            pai1, pai2 = random.sample(elite, 2)
            corte = random.randint(1, len(pessoas_lista) * 2 - 2)
            filho = pai1[:corte] + pai2[corte:]
            if random.random() < 0.1:
                i = random.randint(0, len(filho) - 1)
                pessoa_idx = i // 2
                if i % 
