import tkinter as tk
from tkinter import messagebox
import pandas as pd
import numpy as np
import os
import speech_recognition as sr
import threading

# --- Carica la rosa ---
df_rosa = pd.read_csv("napoli_rosa.csv")
rosa_completa = df_rosa["nome"].tolist()

alias_mappa = {
    "alex": "Meret",
    "giovanni": "Di Lorenzo",
    "lobo": "Lobotka",
    "franco": "Anguissa",
    "scott": "McTominay",
    "amir": "Rrahmani",
    "bill": "Gilmour",
    "filippo": "Billing",
    "ciao": "Ngonge",
    "marco": "Okafor",
    "mattia": "Olivera",
    "roberto": "Lukaku",
    "leonardo": "Spinazzola",
    "giacomo": "Raspadori",
    "alessandro": "Buongiorno"
}

giocatori_selezionati = []
giocatori_selezionati_lower = []
matrice = None
nome_partita = ""
recognizer = sr.Recognizer()
stop_ascolto = False

def conferma_rosa():
    global giocatori_selezionati, giocatori_selezionati_lower
    giocatori_selezionati = [g for g, var in checkbox_vars.items() if var.get()]
    if not giocatori_selezionati:
        messagebox.showwarning("Attenzione", "Seleziona almeno un giocatore!")
        return
    # Creo anche la lista "normalizzata"
    giocatori_selezionati_lower = [g.lower().strip() for g in giocatori_selezionati]
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
    avvia_vocale()

def avvia_vocale():
    global finestra_vocale
    finestra_vocale = tk.Tk()
    finestra_vocale.title(f"Ascolto vocale - {nome_partita}")
    finestra_vocale.geometry("500x300")

    label_info = tk.Label(finestra_vocale, text="Sto ascoltando...\nPronuncia: 'Passatore Ricevente'", font=("Helvetica", 14), fg="blue")
    label_info.pack(pady=20)

    log_box = tk.Text(finestra_vocale, height=10, width=60)
    log_box.pack(pady=10)

    def aggiorna_log(msg):
        log_box.insert(tk.END, msg + "\n")
        log_box.see(tk.END)

    def ascolta():
        global stop_ascolto
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source)
            while not stop_ascolto:
                try:
                    audio = recognizer.listen(source, timeout=5)
                    testo = recognizer.recognize_google(audio, language="it-IT")
                    parole = testo.strip().split()

                    if len(parole) == 2:
                        passatore_raw, ricevente_raw = parole
                        # Normalizza
                        passatore_raw = passatore_raw.lower().strip()
                        ricevente_raw = ricevente_raw.lower().strip()

                        # Applica alias
                        passatore_nome = alias_mappa.get(passatore_raw, passatore_raw.capitalize())
                        ricevente_nome = alias_mappa.get(ricevente_raw, ricevente_raw.capitalize())

                        # Ricostruisci lista normalizzata di selezionati
                        giocatori_selezionati_lower = [g.lower().strip() for g in giocatori_selezionati]

                        if passatore_nome.lower() in giocatori_selezionati_lower and ricevente_nome.lower() in giocatori_selezionati_lower:
                            i = giocatori_selezionati_lower.index(passatore_nome.lower())
                            j = giocatori_selezionati_lower.index(ricevente_nome.lower())
                            matrice[i][j] += 1
                            aggiorna_log(f"✅ {giocatori_selezionati[i]} → {giocatori_selezionati[j]} (Tot: {matrice[i][j]})")
                        else:
                            aggiorna_log(f"⚠️ Giocatori non trovati: {passatore_nome}, {ricevente_nome}")

                    else:
                        aggiorna_log(f"⚠️ Riconosciute {len(parole)} parole: '{testo}' (servono esattamente 2)")

                except sr.WaitTimeoutError:
                    aggiorna_log("⏳ Timeout, riprovo...")
                except sr.UnknownValueError:
                    aggiorna_log("❓ Non capito, riprova...")
                except Exception as e:
                    aggiorna_log(f"⚠️ Errore: {e}")

    def ferma_e_esporta():
        global stop_ascolto
        stop_ascolto = True
        df = pd.DataFrame(matrice, index=giocatori_selezionati, columns=giocatori_selezionati)
        cartella = "Partite"
        if not os.path.exists(cartella):
            os.makedirs(cartella)
        filename = os.path.join(cartella, f"{nome_partita}.xlsx")
        df.to_excel(filename)
        messagebox.showinfo("Esporta", f"File esportato in '{filename}'!")
        finestra_vocale.destroy()

    tk.Button(finestra_vocale, text="Stop ed esporta", command=ferma_e_esporta).pack(pady=10)

    threading.Thread(target=ascolta, daemon=True).start()
    finestra_vocale.mainloop()

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
    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
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

tk.Button(scrollable_frame, text="Conferma rosa", command=conferma_rosa).pack(pady=10)

finestra_rosa.mainloop()