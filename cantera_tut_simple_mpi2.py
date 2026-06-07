import cantera as ct
import numpy as np
import matplotlib.pyplot as plt
from mpi4py import MPI
import itertools
import csv

# 1. Inicjalizacja środowiska MPI
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

# ==========================================
# GŁÓWNE PARAMETRY DO ZMIANY
# ==========================================
P = 101325.0  # Ciśnienie [Pa]

# Tylko proces główny (rank 0) definiuje zakres badań
tasks = None
if rank == 0:
    # Definiujemy listy parametrów do przebadania
    T_list = [300.0, 500.0, 700.0]           # Lista temperatur (jak w mpi2)
    phi_list = [0.6, 0.8, 1.0, 1.2, 1.4]     # Lista ułamków mieszanki
    moisture_list = [0.0, 0.05, 0.10, 0.15]  # Lista wilgotności (jak w mpi1)
    
    # Tworzymy wszystkie możliwe kombinacje (T, phi, wilgotność)
    tasks = list(itertools.product(T_list, phi_list, moisture_list))
    print(f"Rozpoczynam obliczenia! Łączna liczba punktów: {len(tasks)}")
    print(f"Zadania zostały podzielone na {size} rdzeni(e).")

# Rozsyłamy zadania ze wszystkimi kombinacjami do rdzeni
tasks = comm.bcast(tasks, root=0)
local_tasks = np.array_split(tasks, size)[rank]

# Tablica na wyniki policzone przez dany rdzeń
local_results = []
gas = ct.Solution('gri30.yaml')

# 2. Obliczenia niezależne na rdzeniach
for T, phi, moisture in local_tasks:
    # Skład mieszanki z uwzględnieniem wilgoci
    ch4_fraction = 1.0 - moisture
    fuel_string = f"CH4:{ch4_fraction}, H2O:{moisture}"
    oxidizer_string = "O2:1.0, N2:3.76"

    gas.set_equivalence_ratio(phi, fuel_string, oxidizer_string)
    gas.TP = T, P
    
    f = ct.FreeFlame(gas, width=0.03)
    f.set_refine_criteria(ratio=3, slope=0.06, curve=0.12)
    
    try:
        f.solve(loglevel=0, auto=True)
        
        # Zczytywanie wyników z obiektu płomienia
        Su = f.velocity[0]
        T_profile = f.T
        dTdx = np.gradient(T_profile, f.grid)
        thickness = (np.max(T_profile) - np.min(T_profile)) / np.max(dTdx) * 1000 # [mm]
        
    except Exception:
        # Zabezpieczenie przed brakiem zapłonu dla ekstremalnych parametrów
        Su = np.nan
        thickness = np.nan
        
    # Zapisujemy komplet parametrów i wyników
    local_results.append([T, phi, moisture, Su, thickness])

# 3. Zbierz wyniki ze wszystkich rdzeni do procesu głównego
gathered_results = comm.gather(local_results, root=0)

# 4. Finalizacja: zapis i rysowanie (tylko na procesie nr 0)
if rank == 0:
    # Spłaszczanie otrzymanej listy list
    final_results = [item for sublist in gathered_results for item in sublist]
    
    # Sortowanie wyników: by T, potem wilgotność, potem phi
    final_results.sort(key=lambda x: (x[0], x[2], x[1]))

    # --- ZAPIS DO JEDNEGO ZBIORCZEGO PLIKU CSV ---
    filename = "wyniki_kompletne_mpi2.csv"
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Temperatura[K]", "Phi", "Wilgotnosc_Paliwa", "Predkosc_Plomienia[m/s]", "Grubosc_Plomienia[mm]"])
        writer.writerows(final_results)
    print(f"\nWyniki zapisano pomyślnie do pliku: {filename}")

    # --- RYSOWANIE WYKRESÓW ---
    plt.style.use('bmh')
    
    unique_moistures = sorted(list(set([r[2] for r in final_results])))
    unique_T = sorted(list(set([r[0] for r in final_results])))

    # Generujemy osobną parę wykresów (prędkość i grubość) dla KAŻDEJ wartości wilgotności
    for moist_val in unique_moistures:
        fig1, ax1 = plt.subplots(figsize=(8, 5))
        fig2, ax2 = plt.subplots(figsize=(8, 5))

        # Na danym wykresie wilgotności rysujemy linie dla poszczególnych temperatur (jak w mpi2)
        for T_val in unique_T:
            data_filtered = [r for r in final_results if r[0] == T_val and r[2] == moist_val]
            
            if not data_filtered: continue
            
            phis = [r[1] for r in data_filtered]
            speeds = [r[3] for r in data_filtered]
            thicks = [r[4] for r in data_filtered]

            ax1.plot(phis, speeds, marker='o', label=f"T = {T_val} K")
            ax2.plot(phis, thicks, marker='s', label=f"T = {T_val} K")

        # Ustawienia i zapis wykresu prędkości dla danej wilgotności
        moist_percent = int(moist_val * 100)
        ax1.set_xlabel('Współczynnik składu mieszanki ($\\phi$)')
        ax1.set_ylabel('Prędkość $S_L$ [m/s]')
        ax1.set_title(f'Prędkość płomienia (Zawilgocenie {moist_percent}%)')
        ax1.legend()
        fig1.savefig(f'mpi_predkosc_multi_T_wilg_{moist_percent}proc.png', dpi=300)

        # Ustawienia i zapis wykresu grubości dla danej wilgotności
        ax2.set_xlabel('Współczynnik składu mieszanki ($\\phi$)')
        ax2.set_ylabel('Grubość cieplna $\\delta_L$ [mm]')
        ax2.set_title(f'Grubość płomienia (Zawilgocenie {moist_percent}%)')
        ax2.legend()
        fig2.savefig(f'mpi_grubosc_multi_T_wilg_{moist_percent}proc.png', dpi=300)
        
        # Zamykamy wykresy, żeby nie zużywać pamięci RAM w pętli
        plt.close(fig1)
        plt.close(fig2)

    print("Zakończono generowanie wszystkich wykresów! Zostały zapisane z rozszerzeniem .png")