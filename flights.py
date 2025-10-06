# ==============================
#  ALGORITMOS DE OTIMIZAÇÃO – CALENDÁRIO DE VOOS
#  Professor: Wesley Vieira | 6º Período Noite
# ==============================

import random
import math
from datetime import datetime
import matplotlib.pyplot as plt

# -----------------------------------
# ETAPA 1 – LEITURA DOS DADOS
# -----------------------------------

# Custo de espera (em euros por hora)
custo_espera_por_hora = 20  

# Converter HH:MM para minutos
def para_minutos(hora_str):
    h, m = map(int, hora_str.split(':'))
    return h * 60 + m

# Ler arquivo flights.txt
voos = {}
with open("flights.txt") as f:
    for linha in f:
        origem, destino, saida, chegada, preco = linha.strip().split(',')
        voos.setdefault((origem, destino), [])
        voos[(origem, destino)].append((para_minutos(saida), para_minutos(chegada), int(preco)))

# Pessoas e destinos
pessoas = [
    ('Lisboa', 'LIS'),
    ('Madrid', 'MAD'),
    ('Paris', 'CDG'),
    ('Dublin', 'DUB'),
    ('Bruxelas', 'BRU'),
    ('Londres', 'LHR')
]
destino = 'FCO'

# -----------------------------------
# ETAPA 2 – FUNÇÃO OBJETIVO
# -----------------------------------

def funcao_custo(agenda):
    total_preco_passagens = 0
    horarios_chegada_destino = []
    horarios_partida_volta = []

    for i in range(len(pessoas)):
        codigo_origem = pessoas[i][1]

        # Ida
        indice_voo_ida = agenda[i * 2]
        voo_ida = voos[(codigo_origem, destino)][indice_voo_ida]
        total_preco_passagens += voo_ida[2]
        horarios_chegada_destino.append(voo_ida[1])

        # Volta
        indice_voo_volta = agenda[i * 2 + 1]
        voo_volta = voos[(destino, codigo_origem)][indice_voo_volta]
        total_preco_passagens += voo_volta[2]
        horarios_partida_volta.append(voo_volta[0])

    # Espera na chegada
    horario_ultima_chegada = max(horarios_chegada_destino)
    custo_total_espera_ida = sum(
        (horario_ultima_chegada - h) / 60 * custo_espera_por_hora for h in horarios_chegada_destino
    )

    # Espera na volta
    horario_primeira_partida = min(horarios_partida_volta)
    custo_total_espera_volta = sum(
        (h - horario_primeira_partida) / 60 * custo_espera_por_hora for h in horarios_partida_volta
    )

    custo_final = total_preco_passagens + custo_total_espera_ida + custo_total_espera_volta
    return custo_final

# -----------------------------------
# ETAPA 3 – HILL CLIMB
# -----------------------------------

def hill_climb(max_iter=1000):
    solucao = []
    for p in pessoas:
        solucao.append(random.randint(0, len(voos[(p[1], destino)]) - 1))
        solucao.append(random.randint(0, len(voos[(destino, p[1])]) - 1))

    melhor = funcao_custo(solucao)
    historico = [melhor]

    for _ in range(max_iter):
        nova_solucao = solucao[:]
        i = random.randint(0, len(solucao) - 1)
        p_idx = i // 2
        if i % 2 == 0:
            nova_solucao[i] = random.randint(0, len(voos[(pessoas[p_idx][1], destino)]) - 1)
        else:
            nova_solucao[i] = random.randint(0, len(voos[(destino, pessoas[p_idx][1])]) - 1)

        novo_custo = funcao_custo(nova_solucao)
        if novo_custo < melhor:
            solucao, melhor = nova_solucao, novo_custo
        historico.append(melhor)

    return solucao, melhor, historico

# -----------------------------------
# ETAPA 4 – SIMULATED ANNEALING
# -----------------------------------

def simulated_annealing(temp=10000.0, resfriamento=0.95):
    solucao = []
    for p in pessoas:
        solucao.append(random.randint(0, len(voos[(p[1], destino)]) - 1))
        solucao.append(random.randint(0, len(voos[(destino, p[1])]) - 1))

    melhor = funcao_custo(solucao)
    historico = [melhor]

    while temp > 0.1:
        nova_solucao = solucao[:]
        i = random.randint(0, len(solucao) - 1)
        p_idx = i // 2
        if i % 2 == 0:
            nova_solucao[i] = random.randint(0, len(voos[(pessoas[p_idx][1], destino)]) - 1)
        else:
            nova_solucao[i] = random.randint(0, len(voos[(destino, pessoas[p_idx][1])]) - 1)

        novo_custo = funcao_custo(nova_solucao)
        if novo_custo < melhor or random.random() < math.exp(-(novo_custo - melhor) / temp):
            solucao, melhor = nova_solucao, novo_custo
        historico.append(melhor)
        temp *= resfriamento

    return solucao, melhor, historico

# -----------------------------------
# ETAPA 5 – ALGORITMO GENÉTICO
# -----------------------------------

def algoritmo_genetico(populacao=50, elites=10, geracoes=100):
    def criar_individuo():
        ind = []
        for p in pessoas:
            ind.append(random.randint(0, len(voos[(p[1], destino)]) - 1))
            ind.append(random.randint(0, len(voos[(destino, p[1])]) - 1))
        return ind

    populacao_atual = [criar_individuo() for _ in range(populacao)]

    for _ in range(geracoes):
        pontuacao = [(funcao_custo(ind), ind) for ind in populacao_atual]
        pontuacao.sort()
        elite = [ind for _, ind in pontuacao[:elites]]

        filhos = []
        while len(filhos) < populacao - elites:
            pai1, pai2 = random.sample(elite, 2)
            corte = random.randint(1, len(pessoas) * 2 - 2)
            filho = pai1[:corte] + pai2[corte:]
            if random.random() < 0.1:
                i = random.randint(0, len(filho) - 1)
                p_idx = i // 2
                if i % 2 == 0:
                    filho[i] = random.randint(0, len(voos[(pessoas[p_idx][1], destino)]) - 1)
                else:
                    filho[i] = random.randint(0, len(voos[(destino, pessoas[p_idx][1])]) - 1)
            filhos.append(filho)

        populacao_atual = elite + filhos

    melhor_custo, melhor_solucao = min(
        [(funcao_custo(ind), ind) for ind in populacao_atual], key=lambda x: x[0]
    )
    return melhor_solucao, melhor_custo

# -----------------------------------
# ETAPA 6 – EXECUÇÃO DOS ALGORITMOS
# -----------------------------------

sol1, c1, hill_hist = hill_climb()
sol2, c2, annealing_hist = simulated_annealing()
sol3, c3 = algoritmo_genetico()

print("=== RESULTADOS (com ida e volta) ===")
print(f"Hill Climb: {c1:.2f}")
print(f"Simulated Annealing: {c2:.2f}")
print(f"Algoritmo Genético: {c3:.2f}")

# -----------------------------------
# ETAPA 7 – VISUALIZAÇÃO DOS RESULTADOS
# -----------------------------------

# Gráfico 1: Comparação final
nomes = ['Hill Climb', 'Simulated Annealing', 'Algoritmo Genético']
custos = [c1, c2, c3]

plt.figure(figsize=(8,5))
plt.bar(nomes, custos, color=['#4CAF50', '#2196F3', '#FF9800'])
plt.title('Comparação de Custo Total entre Algoritmos', fontsize=14)
plt.ylabel('Custo Total (€)', fontsize=12)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show()

# Gráfico 2: Evolução do custo durante execução
plt.figure(figsize=(9,5))
plt.plot(hill_hist, label='Hill Climb', color='#4CAF50')
plt.plot(annealing_hist, label='Simulated Annealing', color='#2196F3')
plt.title('Evolução do Custo durante a Otimização', fontsize=14)
plt.xlabel('Iterações', fontsize=12)
plt.ylabel('Custo Total (€)', fontsize=12)
plt.legend()
plt.grid(True, linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show()

# -----------------------------------
# ETAPA 8 – EXIBIÇÃO DAS SOLUÇÕES
# -----------------------------------

def mostrar_solucao(solucao):
    for i, p in enumerate(pessoas):
        ida = voos[(p[1], destino)][solucao[i * 2]]
        volta = voos[(destino, p[1])][solucao[i * 2 + 1]]
        print(f"{p[0]}: Ida {ida[0]//60:02d}:{ida[0]%60:02d}→{ida[1]//60:02d}:{ida[1]%60:02d} ({ida[2]}€) | Volta {volta[0]//60:02d}:{volta[0]%60:02d}→{volta[1]//60:02d}:{volta[1]%60:02d} ({volta[2]}€)")

print("\n--- Hill Climb ---")
mostrar_solucao(sol1)
print("\n--- Simulated Annealing ---")
mostrar_solucao(sol2)
print("\n--- Algoritmo Genético ---")
mostrar_solucao(sol3)

# -------------------------------# -------------------------------
import matplotlib.pyplot as plt

# -------------------------------
# Criar histórico do Algoritmo Genético
# -------------------------------
def historico_genetico(populacao=50, elites=10, geracoes=100):
    def criar_individuo():
        ind = []
        for p in pessoas:
            ind.append(random.randint(0, len(voos[(p[1], destino)]) - 1))
            ind.append(random.randint(0, len(voos[(destino, p[1])]) - 1))
        return ind

    populacao_atual = [criar_individuo() for _ in range(populacao)]
    historico = []

    for _ in range(geracoes):
        pontuacao = [(funcao_custo(ind), ind) for ind in populacao_atual]
        pontuacao.sort()
        elite = [ind for _, ind in pontuacao[:elites]]

        # Salvar melhor custo da geração
        historico.append(pontuacao[0][0])

        filhos = []
        while len(filhos) < populacao - elites:
            pai1, pai2 = random.sample(elite, 2)
            corte = random.randint(1, len(pessoas) * 2 - 2)
            filho = pai1[:corte] + pai2[corte:]
            if random.random() < 0.1:
                i = random.randint(0, len(filho) - 1)
                p_idx = i // 2
                if i % 2 == 0:
                    filho[i] = random.randint(0, len(voos[(pessoas[p_idx][1], destino)]) - 1)
                else:
                    filho[i] = random.randint(0, len(voos[(destino, pessoas[p_idx][1])]) - 1)
            filhos.append(filho)

        populacao_atual = elite + filhos

    return historico

# Gerar histórico do Algoritmo Genético
genetico_hist = historico_genetico()

# -------------------------------
# Plotagem comparativa
# -------------------------------
plt.figure(figsize=(10,6))
plt.plot(hill_hist, label='Hill Climb', color='#4CAF50', linewidth=2)
plt.plot(annealing_hist, label='Simulated Annealing', color='#2196F3', linewidth=2)
plt.plot(genetico_hist, label='Algoritmo Genético', color='#FF9800', linewidth=2)
plt.title('Evolução do Custo por Algoritmo (Dados Reais)', fontsize=14)
plt.xlabel('Iterações / Gerações', fontsize=12)
plt.ylabel('Custo Total (€)', fontsize=12)
plt.grid(True, linestyle='--', alpha=0.7)
plt.legend(fontsize=12)
plt.tight_layout()
plt.show()

