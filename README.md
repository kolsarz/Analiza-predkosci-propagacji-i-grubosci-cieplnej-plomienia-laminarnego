# Analiza prędkości propagacji i grubości cieplnej płomienia laminarnego

## Parametry początkowe symulacji

|Parametr|Badane wartości|
|-|-|
|**Współczynnik składu mieszanki ($\\Phi$)**|0.6, 0.8, 1.0, 1.2, 1.4|
|**Zawartość wilgoci w paliwie ($x$)**|0%, 5%, 10%, 15%, 20%|
|**Temperatura początkowa ($T$)**|300 K, 500 K, 700 K|
|**Ciśnienie ($P$)**|101325 Pa (stałe atmosferyczne)|

*Uwaga: W mechanizmie Cantera zawilgocenie wprowadzono poprzez odpowiednią modyfikację strumienia paliwa o wodę w stanie gazowym ($H\_2O$), pełniącą rolę balastu termicznego.*

\---

## Wykorzystane technologie i mechanizmy

Środowisko symulacji:

* **Język programowania:** Python 3.9
* **Silnik termodynamiczny:** Cantera 3.0 (model *FreeFlame*)
* **Mechanizm kinetyczny:** GRI-Mech 3.0
* **Zrównoleglenie obliczeń (HPC):** Open MPI (biblioteka `mpi4py`)
* **Analiza i wizualizacja danych:** `numpy`, `matplotlib`, `csv`

\---

## Uruchamianie projektu

Dzięki zastosowaniu biblioteki `mpi4py` projekt wykorzystuje architekturę obliczeń równoległych (model problemu trywialnie równoległego).

Aby uruchomić symulację z podziałem na określoną liczbę rdzeni (np. 4), należy wywołać skrypt w terminalu za pomocą komendy:

```bash
mpirun -n 4 python cantera\_tut\_simple\_mpi2.py
