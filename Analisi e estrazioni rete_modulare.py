import pandas as pd
import networkx as nx
import os
from cdlib import algorithms
import logging

logging.basicConfig(level=logging.INFO)

# === 1. Caricamento dati ===
def load_adjacency_matrix(file_path):
    return pd.read_excel(file_path, index_col=0)

def merge_halves(df1, df2):
    return df1.add(df2, fill_value=0)

# === 2. Costruzione e pulizia grafo ===
def build_graph(df):
    return nx.from_pandas_adjacency(df, create_using=nx.DiGraph)

def clean_graph(G):
    G_clean = G.copy()
    G_clean.remove_nodes_from(list(nx.isolates(G_clean)))
    return G_clean

# === 3. Calcolo delle misure di centralità ===
def compute_centrality(G):
    return {
        "DegreeCentrality": nx.degree_centrality(G),
        "InDegreeCentrality": nx.in_degree_centrality(G),
        "OutDegreeCentrality": nx.out_degree_centrality(G),
        "BetweennessCentrality": nx.betweenness_centrality(G, weight='weight'),
        "ClusteringCoefficient": nx.clustering(G, weight='weight')
    }

# === 4. Rilevamento comunità ===
def detect_communities(G, clean=False):
    if clean:
        G = clean_graph(G)
    communities = algorithms.louvain(G, weight='weight', randomize=False)
    mapping = {}
    for i, comm in enumerate(communities.communities):
        for player in comm:
            mapping[player] = i + 1
    return communities, mapping

# === 5. Creazione DataFrame ===
def create_metrics_df(G, centrality_dict, community_map):
    data = []
    for player in G.nodes():
        data.append({
            "Player": player,
            "DegreeCentrality": centrality_dict["DegreeCentrality"].get(player, 0),
            "InDegreeCentrality": centrality_dict["InDegreeCentrality"].get(player, 0),
            "OutDegreeCentrality": centrality_dict["OutDegreeCentrality"].get(player, 0),
            "BetweennessCentrality": centrality_dict["BetweennessCentrality"].get(player, 0),
            "ClusteringCoefficient": centrality_dict["ClusteringCoefficient"].get(player, 0),
            "Community": community_map.get(player, -1)
        })
    return pd.DataFrame(data).sort_values(by="DegreeCentrality", ascending=False)

# === 6. Esportazione ===
def export_excel(output_dir, file_name, dfs_dict):
    path = os.path.join(output_dir, file_name)
    with pd.ExcelWriter(path) as writer:
        for sheet_name, df in dfs_dict.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    logging.info(f"✅ File Excel salvato: {path}")

def export_gexf(output_dir, name, G):
    path = os.path.join(output_dir, f"{name}.gexf")
    nx.write_gexf(G, path)
    logging.info(f"✅ File GEXF salvato: {path}")

# === 7. Main ===
def main():
    # === File input ===
    output_dir = "Output"
    os.makedirs(output_dir, exist_ok=True)

    file_primotempo = "Partite/Serie A 2024-25/12a Giornata_Inter-Napoli/Primo tempo_12a Giornata 2024-25_Inter Napoli.xlsx"
    file_secondotempo = "Partite/Serie A 2024-25/12a Giornata_Inter-Napoli/Secondo tempo_12a Giornata 2024-25_Inter Napoli.xlsx"

    # === Caricamento ===
    df1 = load_adjacency_matrix(file_primotempo)
    df2 = load_adjacency_matrix(file_secondotempo)
    df = merge_halves(df1, df2)

    # === Costruzione grafi ===
    G1 = build_graph(df1)
    G2 = build_graph(df2)
    G = build_graph(df)

    # === Misure di centralità ===
    centrality_1 = compute_centrality(G1)
    centrality_2 = compute_centrality(G2)
    centrality_full = compute_centrality(G)

    # === Comunità ===
    _, comm_map1 = detect_communities(G1, clean=True)
    _, comm_map2 = detect_communities(G2)
    _, comm_map_full = detect_communities(G)

    # === DataFrame dei risultati ===
    df_metrics1 = create_metrics_df(G1, centrality_1, comm_map1)
    df_metrics2 = create_metrics_df(G2, centrality_2, comm_map2)
    df_metrics = create_metrics_df(G, centrality_full, comm_map_full)

    # === Esportazione ===
    export_excel(output_dir, "analisi_centralita_completa.xlsx", {
        "Primo Tempo": df_metrics1,
        "Secondo Tempo": df_metrics2,
        "Partita Totale": df_metrics
    })

    # === Attributi sui nodi ===
    for Gx, centrality, comm_map in [(G, centrality_full, comm_map_full),
                                     (G1, centrality_1, comm_map1),
                                     (G2, centrality_2, comm_map2)]:
        for node in Gx.nodes():
            for k in centrality:
                Gx.nodes[node][k] = centrality[k].get(node, 0)
            Gx.nodes[node]["Community"] = comm_map.get(node, -1)

    # === Esportazione GEXF ===
    export_gexf(output_dir, "rete_partita", G)
    export_gexf(output_dir, "rete_primo_tempo", G1)
    export_gexf(output_dir, "rete_secondo_tempo", G2)

if __name__ == "__main__":
    main()