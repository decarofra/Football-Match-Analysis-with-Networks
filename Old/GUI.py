import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import numpy as np
import os

# --- Leggi la rosa dal file CSV ---
df_rosa = pd.read_csv("napoli_rosa.csv")
giocatori = df_rosa["nome"].tolist()

n = len(giocatori)
matrice = np.zeros((n, n), dtype=int)
stack_passaggi = []

nome_partita = ""  # Variabile per salvare il nome della partita

def avvia_partita():
    global nome_partita
    nome_partita = entry_partita.get()
    if not nome_partita.strip():
        messagebox.showwarning("Attenzione", "Inserisci un nome per la partita!")
        return
    
    # Chiudi finestra iniziale e avvia quella principale
    finestra_iniziale.destroy()
    avvia_gui_principale()

def seleziona_passatore():
    seleziona_label.config(text="Chi ha fatto il passaggio?")
    passatore_combo["values"] = giocatori
    passatore_combo.current(0)
    passatore_combo.pack()
    conferma_passatore_btn.pack()

def conferma_passatore():
    global passatore_idx
    passatore = passatore_combo.get()
    passatore_idx = giocatori.index(passatore)

    seleziona_label.config(text="A chi l'ha passata?")
    ricevente_combo["values"] = [g for g in giocatori if g != passatore]
    ricevente_combo.current(0)
    passatore_combo.pack_forget()
    conferma_passatore_btn.pack_forget()
    ricevente_combo.pack()
    conferma_ricevente_btn.pack()

def conferma_ricevente():
    ricevente = ricevente_combo.get()
    ricevente_idx = giocatori.index(ricevente)

    matrice[passatore_idx][ricevente_idx] += 1
    stack_passaggi.append((passatore_idx, ricevente_idx))

    contatore_label.config(text=f"Passaggi registrati: {np.sum(matrice)}")
    aggiorna_tabella()

    ricevente_combo.pack_forget()
    conferma_ricevente_btn.pack_forget()
    seleziona_passatore()

def aggiorna_tabella():
    for i in tree.get_children():
        tree.delete(i)
    for i, riga in enumerate(matrice):
        values = list(riga)
        tree.insert("", "end", text=giocatori[i], values=values)

def annulla_ultimo():
    if stack_passaggi:
        passatore_idx, ricevente_idx = stack_passaggi.pop()
        if matrice[passatore_idx][ricevente_idx] > 0:
            matrice[passatore_idx][ricevente_idx] -= 1
        contatore_label.config(text=f"Passaggi registrati: {np.sum(matrice)}")
        aggiorna_tabella()
    else:
        messagebox.showinfo("Annulla", "Nessun passaggio da annullare!")

def esporta():
    df = pd.DataFrame(matrice, index=giocatori, columns=giocatori)
    # Salva usando il nome della partita
    filename = os.path.join("Partite", f"{nome_partita}.xlsx")
    df.to_excel(filename)
    messagebox.showinfo("Esporta", f"File esportato come '{filename}'!")

def termina():
    root.destroy()

def avvia_gui_principale():
    global root, seleziona_label, passatore_combo, ricevente_combo
    global conferma_passatore_btn, conferma_ricevente_btn
    global contatore_label, tree

    root = tk.Tk()
    root.title(f"Registratore passaggi Napoli - {nome_partita}")
    root.geometry("1000x600")

    seleziona_label = tk.Label(root, text="Chi ha fatto il passaggio?", font=("Helvetica", 12))
    seleziona_label.pack(pady=10)

    passatore_combo = ttk.Combobox(root, state="readonly")
    ricevente_combo = ttk.Combobox(root, state="readonly")

    conferma_passatore_btn = tk.Button(root, text="Conferma", command=conferma_passatore)
    conferma_ricevente_btn = tk.Button(root, text="Conferma", command=conferma_ricevente)

    contatore_label = tk.Label(root, text="Passaggi registrati: 0", font=("Helvetica", 10))
    contatore_label.pack(pady=10)

    # Frame bottoni
    btn_frame = tk.Frame(root)
    btn_frame.pack(pady=5)

    annulla_btn = tk.Button(btn_frame, text="Annulla ultimo", command=annulla_ultimo)
    annulla_btn.pack(side="left", padx=5)

    esporta_btn = tk.Button(btn_frame, text="Esporta", command=esporta)
    esporta_btn.pack(side="left", padx=5)

    termina_btn = tk.Button(btn_frame, text="Termina partita", command=termina)
    termina_btn.pack(side="left", padx=5)

    # Tabella
    tree_frame = tk.Frame(root)
    tree_frame.pack(pady=10, fill="x")

    cols = giocatori
    tree = ttk.Treeview(tree_frame, columns=cols, show="headings")
    for g in giocatori:
        tree.heading(g, text=g)
        tree.column(g, width=60, anchor="center")

    tree.pack(fill="x")

    seleziona_passatore()
    aggiorna_tabella()

    root.mainloop()

# --- Finestra iniziale ---
finestra_iniziale = tk.Tk()
finestra_iniziale.title("Inizia partita")
finestra_iniziale.geometry("400x150")

label_intro = tk.Label(finestra_iniziale, text="Ciao! Che partita stai guardando?", font=("Helvetica", 12))
label_intro.pack(pady=10)

entry_partita = tk.Entry(finestra_iniziale, font=("Helvetica", 12))
entry_partita.pack(pady=5)

btn_conferma = tk.Button(finestra_iniziale, text="Conferma", command=avvia_partita)
btn_conferma.pack(pady=10)

finestra_iniziale.mainloop()