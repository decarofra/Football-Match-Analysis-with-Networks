import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import numpy as np
import os

# ---- Leggi rosa dal CSV ----
df_rosa = pd.read_csv("napoli_rosa.csv")
rosa_completa = df_rosa["nome"].tolist()

# Variabili globali
giocatori_selezionati = []
matrice = None
stack_passaggi = []
nome_partita = ""
root = None
buttons = {}

def conferma_rosa():
    global giocatori_selezionati
    giocatori_selezionati = [g for g, var in checkbox_vars.items() if var.get()]
    if not giocatori_selezionati:
        messagebox.showwarning("Attenzione", "Seleziona almeno un giocatore!")
        return

    finestra_rosa.destroy()
    chiedi_nome_partita()

def chiedi_nome_partita():
    global entry_partita, finestra_partita
    finestra_partita = tk.Tk()
    finestra_partita.title("Nome partita")
    finestra_partita.geometry("400x150")

    tk.Label(finestra_partita, text="Inserisci il nome della partita:", font=("Helvetica", 12)).pack(pady=10)
    entry_partita = tk.Entry(finestra_partita, font=("Helvetica", 12))
    entry_partita.pack(pady=5)
    tk.Button(finestra_partita, text="Conferma", command=conferma_partita).pack(pady=10)

def conferma_partita():
    global nome_partita, matrice
    nome_partita = entry_partita.get().strip()
    if not nome_partita:
        messagebox.showwarning("Attenzione", "Inserisci un nome per la partita!")
        return

    finestra_partita.destroy()
    matrice = np.zeros((len(giocatori_selezionati), len(giocatori_selezionati)), dtype=int)
    avvia_matrice()

def avvia_matrice():
    global root, buttons
    root = tk.Tk()
    root.title(f"Passaggi - {nome_partita}")
    root.geometry("1200x700")

    tk.Label(root, text="Clicca +1 per registrare passaggi", font=("Helvetica", 12, "bold")).grid(row=0, column=1, columnspan=len(giocatori_selezionati)+1, pady=10)

    # Colonne (riceventi)
    for j, ricevente in enumerate(giocatori_selezionati):
        tk.Label(root, text=ricevente, borderwidth=1, relief="solid", width=12).grid(row=1, column=j+1, padx=1, pady=1)

    # Righe (passatori)
    for i, passatore in enumerate(giocatori_selezionati):
        tk.Label(root, text=passatore, borderwidth=1, relief="solid", width=12).grid(row=i+2, column=0, padx=1, pady=1)

        for j, ricevente in enumerate(giocatori_selezionati):
            if i == j:
                btn = tk.Label(root, text="X", width=4, relief="ridge", bg="gray80")
                btn.grid(row=i+2, column=j+1, padx=1, pady=1)
                buttons[(i, j)] = btn
            else:
                frame = tk.Frame(root)
                btn = tk.Button(frame, text="0", width=4, command=lambda x=i, y=j: incrementa(x, y))
                btn.pack()
                frame.grid(row=i+2, column=j+1, padx=1, pady=1)
                buttons[(i, j)] = btn

    # Bottoni sotto
    btn_frame = tk.Frame(root)
    btn_frame.grid(row=len(giocatori_selezionati)+3, column=0, columnspan=len(giocatori_selezionati)+1, pady=10)

    tk.Button(btn_frame, text="Annulla ultimo", command=annulla_ultimo).pack(side="left", padx=5)
    tk.Button(btn_frame, text="Esporta", command=esporta).pack(side="left", padx=5)
    tk.Button(btn_frame, text="Chiudi", command=root.destroy).pack(side="left", padx=5)

    root.mainloop()

def incrementa(i, j):
    matrice[i][j] += 1
    buttons[(i, j)].config(text=str(matrice[i][j]))
    stack_passaggi.append((i, j))

def annulla_ultimo():
    if stack_passaggi:
        i, j = stack_passaggi.pop()
        if matrice[i][j] > 0:
            matrice[i][j] -= 1
            buttons[(i, j)].config(text=str(matrice[i][j]))
    else:
        messagebox.showinfo("Info", "Nessun passaggio da annullare!")

def esporta():
    df = pd.DataFrame(matrice, index=giocatori_selezionati, columns=giocatori_selezionati)
    cartella = "Partite"
    if not os.path.exists(cartella):
        os.makedirs(cartella)
    filename = os.path.join(cartella, f"{nome_partita}.xlsx")
    df.to_excel(filename)
    messagebox.showinfo("Esporta", f"File esportato in '{filename}'!")

# --- Prima finestra: selezione rosa ---
finestra_rosa = tk.Tk()
finestra_rosa.title("Seleziona giocatori")
finestra_rosa.geometry("400x600")

tk.Label(finestra_rosa, text="Seleziona i giocatori presenti:", font=("Helvetica", 12)).pack(pady=10)

canvas = tk.Canvas(finestra_rosa)
scrollbar = tk.Scrollbar(finestra_rosa, orient="vertical", command=canvas.yview)
scrollable_frame = tk.Frame(canvas)

scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(
        scrollregion=canvas.bbox("all")
    )
)

canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

checkbox_vars = {}
for giocatore in rosa_completa:
    var = tk.BooleanVar()
    chk = tk.Checkbutton(scrollable_frame, text=giocatore, variable=var)
    chk.pack(anchor="w")
    checkbox_vars[giocatore] = var

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

tk.Button(finestra_rosa, text="Conferma rosa", command=conferma_rosa).pack(pady=10)

finestra_rosa.mainloop()