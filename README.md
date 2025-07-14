**Football Match Analysis adopting Network Analysis techniques and frameworks**

This project aims at studying tactical plays and coaches' strategies in football by leveraging network analysis.
The project focuses on SSC Napoli, covering matches in two different seasons, both ended with the team winning the Scudetto, but with very different journeys and tactics under two different coaches (Luciano Spalletti in 2022-23, Antonio Conte in 2024-25).
The repository contains:

- Two csv files with SSC Napoli's squad during the two seasons
- Two .py files (one for the 22-23 squad and one for the 24-25 squad) which are the code implementation of the GUIs used to gather data about matches by leveraging on speech recognition
- Two files ("Analisi e estrazione rete_modulare") which contain the code to implement network analysis on the produced datasets
- A "Partite" folder with the datasets produced with the GUI
- A "Output" folder with the plots, xlsx and gefx results of the analysis
- A "Old" folder with the initial implementations


***Data Collection and Dataset Production using Speech Recognition***


The data collected consists in two different adjacency matrices for each match, one for the first half and one for the second. Using speech recognition while watching the matches, each pass by a SSC Napoli player during the match is registered, so that in the adjacency matrix (which is a produced dataset consisting of an excel file) each value m_ij represents the number of passes player i directed to player j.
As a result, the graphs used in the analysis are both weighted and directed.


***The Analysis***


The analysis relies on the info gathered (number of passes between players) to determine which are the central players in the coach's gameplan, the communities (a.k.a. the group of players strongly connected as frequently exchanging passess between themselves) and the playing roles (obtained using k-means clustering on the network features extracted) which result from the tactics used during the match.
By analyzing matches played in different seasons, the difference in the style of playing comes out as very evident.
The network features extracted and considered to conduct the analysis and to build the clustering process are the following:

- Degree Centrality
- In Strength
- Out Strength
- Clustering Coefficient
- Betweenness Centrality


***The Results - an example: Inter-Napoli 1-1, Serie A 2024-25***


The repository contains the output files obtained analyzing one of the crucial matches of the 24-25 season: Inter-Napoli.
Frank Anguissa comes out as the most important and crucial player in building the game. He has both the highest degree and betweenness centrality. Romelu Lukaku, instead, comes out as a pivotal but poorly helped point of the team: he has a high in strength, especially in the first half, but a low out strength, meaning he often received passes and couldn't pass the ball to teammates because he was kinda isolated and didn't maintain the possession.
The following plot shows the graph with colours representing community clustering obtained with the Louvain algorithm, while node dimension represents degree centrality:

<p align="center">
  <img width="632" height="517" alt="DegreeCentrality_LouvainCommunities_FullMatch" src="https://github.com/user-attachments/assets/3a6170fb-10e3-4c7d-bad3-d1e3d43c6730" />
</p>

It is clear how Napoli's play is often very one-sided, as players like Buongiorno, Olivera, McTominay and Kvara are strictly connected, just like on the other side are Di Lorenzo, Anguissa and Politano.
The following plot focuses instead on betweenness centrality (represented by node dimension), while colors represent the k-means clustering:

<p align="center">
  <img width="565" height="483" alt="BetweennessCentrality_FunctionalClustering_FullMatch" src="https://github.com/user-attachments/assets/04352747-37bf-40cb-85c2-eb5cd1ba3cd3" />
</p>

We can see how the most dominant players in the gamestyle are for sure Anguissa and Lobotka, while Lukaku is once again mostly irrelevant. Also in this case, the "left" community is pretty noticeable, just as the strong connection in play between Anguissa and Di Lorenzo. Simeone and Ngonge played very few minutes and are irrelevant.


***Requisites***


The project is implemented using python, while the final plots showed are obtained using Gephi (https://gephi.org/). All the necessary libraries are listed in the source codes.
