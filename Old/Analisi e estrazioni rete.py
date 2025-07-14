import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import os
from cdlib import algorithms
from networkx.algorithms import community

# === 1. Caricare la matrice di adiacenza dal file Excel ===
file_primotempo = "Partite/Serie A 2024-25/12a Giornata_Inter-Napoli/Primo tempo_12a Giornata 2024-25_Inter Napoli.xlsx"
df1 = pd.read_excel(file_primotempo, index_col=0)
file_secondotempo = "Partite/Serie A 2024-25/12a Giornata_Inter-Napoli/Secondo tempo_12a Giornata 2024-25_Inter Napoli.xlsx"
df2 = pd.read_excel(file_secondotempo, index_col=0)
df = df1.add(df2, fill_value=0)

# === 2. Creare il grafo ===
G1 = nx.from_pandas_adjacency(df1, create_using=nx.DiGraph)
isolated_nodes = list(nx.isolates(G1))
G1_clean = G1.copy()
G1_clean.remove_nodes_from(isolated_nodes)
nx.is_connected(G1_clean.to_undirected())
G2 = nx.from_pandas_adjacency(df2, create_using=nx.DiGraph)
G = nx.from_pandas_adjacency(df, create_using=nx.DiGraph)

# === 3. Calcolare misure di centralità ===
degree_centrality_1 = nx.degree_centrality(G1)
in_degree_centrality_1 = nx.in_degree_centrality(G1)
out_degree_centrality_1 = nx.out_degree_centrality(G1)
betweenness_centrality_1 = nx.betweenness_centrality(G1, weight='weight')
clustering_coefficient_1 = nx.clustering(G1, weight='weight')

degree_centrality_2 = nx.degree_centrality(G2)
in_degree_centrality_2 = nx.in_degree_centrality(G2)
out_degree_centrality_2 = nx.out_degree_centrality(G2)
betweenness_centrality_2 = nx.betweenness_centrality(G2, weight='weight')
clustering_coefficient_2 = nx.clustering(G2, weight='weight')

degree_centrality = nx.degree_centrality(G)
in_degree_centrality = nx.in_degree_centrality(G)
out_degree_centrality = nx.out_degree_centrality(G)
betweenness_centrality = nx.betweenness_centrality(G, weight='weight')
clustering_coefficient = nx.clustering(G, weight='weight')

# === 4. Trova comunità ===
communities1 = algorithms.louvain(G1_clean, weight = "weight")
communities2 = algorithms.louvain(G2, weight = "weight")
communities = algorithms.louvain(G, weight = "weight")

# Crea un mapping giocatore → numero comunità
player_to_comm1 = {}
for i, comm in enumerate(communities1.communities):
    for player in comm:
        player_to_comm1[player] = i + 1

player_to_comm2 = {}
for i, comm in enumerate(communities2.communities):
    for player in comm:
        player_to_comm2[player] = i + 1

player_to_comm = {}
for i, comm in enumerate(communities.communities):
    for player in comm:
        player_to_comm[player] = i + 1

print(communities.communities)

# === 5. Prepara DataFrame ===
data1 = []

for player in G1.nodes():
    data1.append({
        "Player": player,
        "DegreeCentrality": degree_centrality_1.get(player, 0),
        "InDegreeCentrality": in_degree_centrality_1.get(player, 0),
        "OutDegreeCentrality": out_degree_centrality_1.get(player, 0),
        "BetweennessCentrality": betweenness_centrality_1.get(player, 0),
        "ClusteringCoefficient": clustering_coefficient_1.get(player, 0),
        "Community": player_to_comm1.get(player, "")
    })

df_metrics1 = pd.DataFrame(data1)
df_metrics1 = df_metrics1.sort_values(by="DegreeCentrality", ascending=False)

data2 = []

for player in G2.nodes():
    data2.append({
        "Player": player,
        "DegreeCentrality": degree_centrality_2.get(player, 0),
        "InDegreeCentrality": in_degree_centrality_2.get(player, 0),
        "OutDegreeCentrality": out_degree_centrality_2.get(player, 0),
        "BetweennessCentrality": betweenness_centrality_2.get(player, 0),
        "ClusteringCoefficient": clustering_coefficient_2.get(player, 0),
        "Community": player_to_comm2.get(player, -1)
    })

df_metrics2 = pd.DataFrame(data2)
df_metrics2 = df_metrics2.sort_values(by="DegreeCentrality", ascending=False)

data = []

for player in G.nodes():
    data.append({
        "Player": player,
        "DegreeCentrality": degree_centrality.get(player, 0),
        "InDegreeCentrality": in_degree_centrality.get(player, 0),
        "OutDegreeCentrality": out_degree_centrality.get(player, 0),
        "BetweennessCentrality": betweenness_centrality.get(player, 0),
        "ClusteringCoefficient": clustering_coefficient.get(player, 0),
        "Community": player_to_comm.get(player, -1)
    })

df_metrics = pd.DataFrame(data)
df_metrics = df_metrics.sort_values(by="DegreeCentrality", ascending=False)

output_dir = "Output"
excel_path = os.path.join(output_dir, "analisi_centralita_completa.xlsx")
with pd.ExcelWriter(excel_path) as writer:
    df_metrics1.to_excel(writer, sheet_name="Primo Tempo", index=False)
    df_metrics2.to_excel(writer, sheet_name="Secondo Tempo", index=False)
    df_metrics.to_excel(writer, sheet_name="Partita Totale", index=False)

print(f"✅ File Excel salvato: {excel_path}")

# === Aggiungi attributi ai nodi ===
for node in G.nodes():
    G.nodes[node]["DegreeCentrality"] = degree_centrality.get(node, 0)
    G.nodes[node]["InDegreeCentrality"] = in_degree_centrality.get(node, 0)
    G.nodes[node]["OutDegreeCentrality"] = out_degree_centrality.get(node, 0)
    G.nodes[node]["BetweennessCentrality"] = betweenness_centrality.get(node, 0)
    G.nodes[node]["ClusteringCoefficient"] = clustering_coefficient.get(node, 0)
    G.nodes[node]["Community"] = player_to_comm.get(node, -1)

for node in G1.nodes():
    G1.nodes[node]["DegreeCentrality"] = degree_centrality_1.get(node, 0)
    G1.nodes[node]["InDegreeCentrality"] = in_degree_centrality_1.get(node, 0)
    G1.nodes[node]["OutDegreeCentrality"] = out_degree_centrality_1.get(node, 0)
    G1.nodes[node]["BetweennessCentrality"] = betweenness_centrality_1.get(node, 0)
    G1.nodes[node]["ClusteringCoefficient"] = clustering_coefficient_1.get(node, 0)
    G1.nodes[node]["Community"] = player_to_comm1.get(node, -1)

for node in G2.nodes():
    G2.nodes[node]["DegreeCentrality"] = degree_centrality_2.get(node, 0)
    G2.nodes[node]["InDegreeCentrality"] = in_degree_centrality_2.get(node, 0)
    G2.nodes[node]["OutDegreeCentrality"] = out_degree_centrality_2.get(node, 0)
    G2.nodes[node]["BetweennessCentrality"] = betweenness_centrality_2.get(node, 0)
    G2.nodes[node]["ClusteringCoefficient"] = clustering_coefficient_2.get(node, 0)
    G2.nodes[node]["Community"] = player_to_comm2.get(node, -1)

gexf_path = os.path.join(output_dir, "rete_partita.gexf")
nx.write_gexf(G, gexf_path)
print(f"✅ File GEXF salvato: {gexf_path}")

gexf_path1 = os.path.join(output_dir, "rete_primo tempo.gexf")
nx.write_gexf(G1, gexf_path1)
print(f"✅ File GEXF salvato: {gexf_path1}")

gexf_path2 = os.path.join(output_dir, "rete_secondo tempo.gexf")
nx.write_gexf(G1, gexf_path2)
print(f"✅ File GEXF salvato: {gexf_path2}")