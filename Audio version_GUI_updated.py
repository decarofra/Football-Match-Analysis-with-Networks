import tkinter as tk
import csv
import pandas as pd
import numpy as np
import speech_recognition as sr
import threading
import os

# Alias vocali per facilitare la pronuncia
alias_mappa = {
    "alex": "Meret",
    "giovanni": "Di Lorenzo",
    "stefano": "Lobotka",
    "franco": "Anguissa",
    "scott": "McTominay",
    "amir": "Rrahmani",
    "gigi": "Gilmour",
    "filippo": "Billing",
    "ciao": "Ngonge",
    "marco": "Okafor",
    "mattia": "Olivera",
    "roberto": "Lukaku",
    "leonardo": "Spinazzola",
    "giacomo": "Raspadori",
    "alessandro": "Buongiorno"
}

# Carica rosa
rosa_df = pd.read_csv("napoli_rosa_24-25.csv")
giocatori_completi = rosa_df["nome"].tolist()

# Seleziona giocatori per la partita
def seleziona_giocatori():
    def conferma():
        global giocatori_selezionati, matrice
        giocatori_selezionati = [g for g, var in zip(giocatori_completi, vars) if var.get()]
        matrice = np.zeros((len(giocatori_selezionati), len(giocatori_selezionati)), dtype=int)
        selezione_window.destroy()

    selezione_window = tk.Tk()
    selezione_window.title("Seleziona giocatori per la partita")
    vars = []

    for g in giocatori_completi:
        var = tk.BooleanVar()
        chk = tk.Checkbutton(selezione_window, text=g, variable=var)
        chk.pack(anchor="w")
        vars.append(var)

    btn = tk.Button(selezione_window, text="Conferma", command=conferma)
    btn.pack()
    selezione_window.mainloop()

# GUI principale
def mostra_matrice_gui():
    global root, log_text, matrice_text, stop_ascolto

    root = tk.Tk()
    root.title("Analisi passaggi Napoli")

    log_text = tk.Text(root, height=10, width=60)
    log_text.pack(pady=10)

    matrice_text = tk.Text(root, height=15, width=80)
    matrice_text.pack(pady=10)

    def termina():
        global stop_ascolto
        stop_ascolto = True
        aggiorna_log("🛑 Chiusura richiesta. Salvataggio file...")
        salva_excel()
        root.destroy()

    btn_stop = tk.Button(root, text="Stop e Salva", command=termina)
    btn_stop.pack(pady=10)

    aggiorna_matrice_gui()

    root.mainloop()

def aggiorna_log(msg):
    log_text.insert(tk.END, msg + "\n")
    log_text.see(tk.END)

def aggiorna_matrice_gui():
    matrice_text.delete(1.0, tk.END)
    header = "\t" + "\t".join(giocatori_selezionati) + "\n"
    matrice_text.insert(tk.END, header)
    for i, row in enumerate(matrice):
        riga_str = giocatori_selezionati[i] + "\t" + "\t".join(str(val) for val in row) + "\n"
        matrice_text.insert(tk.END, riga_str)

# Salvataggio file Excel
def salva_excel():
    df = pd.DataFrame(matrice, index=giocatori_selezionati, columns=giocatori_selezionati)
    nome_file = f"Partite/{nome_partita}.xlsx"
    os.makedirs("Partite", exist_ok=True)
    df.to_excel(nome_file)
    print(f"✅ Matrice salvata in {nome_file}")

# Riconoscimento vocale
recognizer = sr.Recognizer()
stop_ascolto = False

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
                    passatore_raw = passatore_raw.lower().strip()
                    ricevente_raw = ricevente_raw.lower().strip()

                    # Applica alias
                    passatore_nome = alias_mappa.get(passatore_raw, passatore_raw.capitalize())
                    ricevente_nome = alias_mappa.get(ricevente_raw, ricevente_raw.capitalize())

                    giocatori_lower = [g.lower().strip() for g in giocatori_selezionati]

                    if passatore_nome.lower() in giocatori_lower and ricevente_nome.lower() in giocatori_lower:
                        i = giocatori_lower.index(passatore_nome.lower())
                        j = giocatori_lower.index(ricevente_nome.lower())
                        matrice[i][j] += 1
                        aggiorna_log(f"✅ {giocatori_selezionati[i]} → {giocatori_selezionati[j]} (Tot: {matrice[i][j]})")
                        aggiorna_matrice_gui()
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

# Main
if __name__ == "__main__":
    nome_partita = input("Ciao! Che partita stai guardando? (nome file): ")
    seleziona_giocatori()

    # Thread per ascolto vocale
    t_ascolto = threading.Thread(target=ascolta)
    t_ascolto.start()

    mostra_matrice_gui()

    stop_ascolto = True
    t_ascolto.join()