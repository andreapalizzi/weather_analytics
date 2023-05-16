import i_o

run = i_o.read_run("prova.txt", "config.csv")

run.plot_profiles(abscissa="space")