import csv
import pandas as pd
import numpy as np
from scipy.interpolate import pchip_interpolate
import matplotlib.pyplot as plt

def read_run(path, config_path):
    '''
    Parameters:
        path: csv file containing run
    '''

    # read config
    params = {}
    with open(config_path) as f:
        reader = csv.reader(f)
        next(reader, None)
        for row in reader:
            params[row[0]] = row[1]

    #read data
    data = []
    with open(path) as f:
        reader = csv.reader(f)
        next(reader, None)
        for row in reader:
            data.append(row)

    config = Config()
    config.set_params(params)

    run = Run(config)
    run.set_data(np.array(data))
    
    return run
    

class Run:
    def __init__(self, config):
        self.config = config
    
    def set_data(self, data):
        
        self.data = pd.DataFrame(data, columns=["Time", "Torq", "Speed", "Power", "Distance", "Cadence", "Heart rate", "ID", "Altitude"])
        n = len(self.data)
        self.data["Wind"] = np.zeros(n) # TODO: wind speed for each measurement
        self.data["Theta"] = np.zeros(n) # TODO: wind direction for each measurement
        v_cr = np.array([0,30,45,55,70,90,105,120,130,140,150])/3.6
        cr = np.array([0.0027,0.0030,0.0032,0.0033,0.0035,0.0037,0.0038,0.0040,0.0040,0.0041,0.0041])

        # Computing drag coefficient
        print(self.data["Speed"].iloc[:-1])     #TODO: per Gabriele: si accede cosi alle righe/colonne di un dataFrame. Dobbiamo combiare tutto qua sotto, e
                                                # dobbiamo anche scrivere "Power" che l'avevamo lasciato incompleto.
        interval_data = pd.DataFrame({"Wind relative average speed":(self.data[:-1,"Speed"]+self.data[1:,"Speed"])/2-self.data["Wind"]*np.cos(self.data["Theta"]),\
                                      "Power":self.data[1:,"Speed"],\
                                      "Speed difference":self.data[1:,"Speed"]-self.data[:-1,"Speed"],\
                                      "Squared-speed difference":self.data[1:,"Speed"]**2-self.data[:-1,"Speed"]**2,\
                                      "Distance difference":self.data[1:,"Distance"]-self.data[:-1,"Distance"],\
                                      "Squared-cadence difference":self.data[1:,"Cadence"]**2-self.data[:-1,"Cadence"]**2,\
                                      "Height difference":self.data[1:,"Height"]-self.data[:-1,"Height"],\
                                      "Cr":pchip_interpolate(v_cr, cr, self.data[:-1,"Speed"].values),})
        
        self.cd = 2*(interval_data["Power"]*self.config["Efficiency"]-self.config["Mass"]*self.config["g"]*(interval_data["Cr"]*interval_data["Distance difference"]+\
                                                                                                       interval_data["Height difference"])-\
                self.config["Mass"]*interval_data["Squared-speed difference"]/2-self.config["Inertia"]*interval_data["Squared-cadence difference"])/\
            (self.config["Area"]*self.config["Density"]*interval_data["Distance difference"]*interval_data["Wind relative average speed"]**2)
        
        self.cd = pd.DataFrame({"Cd":self.cd, "Wind relative average speed": interval_data["Wind relative average speed"]})

    def plot_cd(self):
        plt.plot(self.cd["Wind relative average speed"], self.cd["Cd"])
        plt.show()
        
class Config:
    def set_params(self, dictionary):
        self.params = dictionary

    def get_param(self, param_name):
        return self.params[param_name]

