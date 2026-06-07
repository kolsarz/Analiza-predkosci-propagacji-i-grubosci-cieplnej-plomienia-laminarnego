import csv
import matplotlib.pyplot as plt

# 1. Wczytanie gotowych danych z pliku CSV
filename = "wyniki_kompletne_wilgotnosc.csv"
T_list, phi_list, moist_list, speeds, thicks = [], [], [], [], []

print(f"Wczytywanie danych z pliku {filename}...")

try:
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Pomijamy nagłówek tabeli
        for row in reader:
            # Zamieniamy tekst z pliku na liczby zmiennoprzecinkowe
            T_list.append(float(row[0]))
            phi_list.append(float(row[1]))
            moist_list.append(float(row[2]))
            speeds.append(float(row[3]))
            thicks.append(float(row[4]))
except FileNotFoundError:
    print(f"Błąd: Nie znaleziono pliku {filename}. Upewnij się, że obliczenia MPI się zakończyły.")
    exit()

# Wyciągamy unikalne wartości, żeby wiedzieć, ile wykresów narysować
unique_T = sorted(list(set(T_list)))
unique_moist = sorted(list(set(moist_list)))

# 2. Ustawienia globalne wykresów
plt.style.use('bmh')

# Tworzymy dwie duże "tablice" na wykresy (każda ma 2 wiersze i 2 kolumny)
fig1, axs1 = plt.subplots(2, 2, figsize=(12, 10))
fig1.suptitle('Wpływ Temperatury na Prędkość Płomienia ($S_L$)', fontsize=16, fontweight='bold')

fig2, axs2 = plt.subplots(2, 2, figsize=(12, 10))
fig2.suptitle('Wpływ Temperatury na Grubość Płomienia ($\delta_L$)', fontsize=16, fontweight='bold')

# "Spłaszczamy" siatkę osi, żeby łatwiej było iterować po nich w pętli
axs1 = axs1.flatten()
axs2 = axs2.flatten()

# 3. Rysowanie danych
for i, moist in enumerate(unique_moist):
    ax1 = axs1[i]
    ax2 = axs2[i]
    
    # Dla każdego z 4 wykresów rysujemy linie dla różnych temperatur
    for T in unique_T:
        # Wyciągamy punkty pasujące tylko do aktualnej pary (Wilgotność, Temperatura)
        x_data = [phi_list[j] for j in range(len(phi_list)) if T_list[j] == T and moist_list[j] == moist]
        y_speed = [speeds[j] for j in range(len(speeds)) if T_list[j] == T and moist_list[j] == moist]
        y_thick = [thicks[j] for j in range(len(thicks)) if T_list[j] == T and moist_list[j] == moist]
        
        ax1.plot(x_data, y_speed, marker='o', linewidth=2, label=f'T = {T} K')
        ax2.plot(x_data, y_thick, marker='s', linewidth=2, label=f'T = {T} K')
        
    # Formatowanie pojedynczego kafelka dla prędkości
    ax1.set_title(f'Zawartość wilgoci: {moist*100:.0f}%', fontsize=12)
    ax1.set_xlabel('Współczynnik składu ($\phi$)')
    ax1.set_ylabel('Prędkość [m/s]')
    ax1.legend()
    
    # Formatowanie pojedynczego kafelka dla grubości
    ax2.set_title(f'Zawartość wilgoci: {moist*100:.0f}%', fontsize=12)
    ax2.set_xlabel('Współczynnik składu ($\phi$)')
    ax2.set_ylabel('Grubość [mm]')
    ax2.legend()

# 4. Automatyczne poprawienie odstępów i zapis
plt.tight_layout(rect=[0, 0.03, 1, 0.95]) # Zapobiega nakładaniu się tytułu na wykresy
fig1.savefig('zestawienie_predkosc_wszystkie_T.png', dpi=300)
fig2.savefig('zestawienie_grubosc_wszystkie_T.png', dpi=300)

print("\nSukces! Zapisano dwa nowe, wielopanelowe wykresy:")
print("- zestawienie_predkosc_wszystkie_T.png")
print("- zestawienie_grubosc_wszystkie_T.png")