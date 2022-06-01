Questa cartella contiene i risultati delle istanze i cui dati energetici sono calcolati in base alla posizione della facility e all'irraggiamento medio.

Le posizioni delle facility sono nel file facilities_coord_umt.csv, mentre l'irraggiamento medio di ogni facility è in un file nella cartella data/irradiation.

Il file stast.csv contiene una tabella che ha una riga per ogni risultato e come colonne il tempo necessario per arrivare alla soluzione (in minuti), lo stato della soluzione, il valore della funzione obbiettivo nel risultato e il valore ottimo della funzione obbiettivo (il gap tra i due è <= 0.1%).

I nomi dei file indicano i dati che sono stati usati per computare quella soluzione:

result_{dataset label}_{numero di time-slots}t_{numero instanza}_{dati energetici}_{funzione distanza}.csv

dove con `dati energetici` si intende quali dati energetici sono stati usati per calcolare la costante, e con `funzione distanza` in che modo cresce la potenza energetica delle facility in funzione della distanza dal centro.

Ogni file contiene una tabella in cui le righe indicano lo stato della facility `k` nel time slot `t`, mentre le colonne sono rispettivamente l'energia residua, l'energia usata, l'energia acquistata e gli AP connessi.
