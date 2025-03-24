import subprocess
import re
import numpy as np
import matplotlib.pyplot as plt

from dataclasses import dataclass

SIM = "../dpm-simulator/dpm_simulator"
#SIM = "dpm-simulator/dpm_simulator_sleep"
PSM = "../dpm-simulator/example/psm.txt"
WL1 = "../workloads/workload_1.txt"
WL2 = "../workloads/workload_2.txt"
LOWER_LIMIT = 0
UPPER_LIMIT = 20


@dataclass
class WorkloadStats:
    active_time: float
    inactive_time: float
    time_run: float
    time_idle: float
    time_sleep: float
    time_waiting: float
    time_transitions: float
    total_transitions: float
    energy_transitions: float
    energy_total_no_dpm: float
    energy_total_dpm: float

    def saved_energy(self):
        return self.energy_total_no_dpm - self.energy_total_dpm
    def saved_energy_perc(self):
        return (self.energy_total_no_dpm - self.energy_total_dpm) / self.energy_total_no_dpm


def extract(pattern, output):
    match = re.search(pattern, output, re.IGNORECASE)
    if not match:
        print(f"Cannot find match for {pattern}")
        exit(-1)

    return float(match.group(1))

#incative parameter wants i(idle) or s(sleep) to identify the inactive status we want to use
def dpm_sim_t(timeout, workload, inactive):

    if(inactive != 'i' and inactive != 's'):
        print(f"Cannot find meanings for {inactive} - i or s has to be inserted")
        exit(-1)

    args = [SIM, "-t"+inactive, str(timeout), "-psm", PSM, "-wl", workload]
    status = subprocess.run(args, stdout=subprocess.PIPE)

    if status.returncode != 0:
        print("There was an error")
        exit(-1)

    return extract_data_workload(status)

def dpm_sim_ha(sleep_threshold, idle_threshold, workload):

    args = [SIM, "-ha", str(sleep_threshold), str(idle_threshold), "-psm", PSM, "-wl", workload]
    status = subprocess.run(args, stdout=subprocess.PIPE)

    if status.returncode != 0:
        print("There was an error")
        exit(-1)

    return extract_data_workload(status)

def extract_data_workload(stdout_bin):
    stdout = stdout_bin.stdout.decode("utf-8")

    active_time = extract(r"Active time in profile = ([0-9\.]+)", stdout)
    inactive_time = extract(r"Inactive time in profile = ([0-9\.]+)", stdout)
    time_run = extract(r"Total time in state Run = ([0-9\.]+)", stdout)
    time_idle = extract(r"Total time in state Idle = ([0-9\.]+)", stdout)
    time_sleep = extract(r"Total time in state Sleep = ([0-9\.]+)", stdout)
    time_waiting = extract(r"Timeout waiting time = ([0-9\.]+)", stdout)
    time_transitions = extract(r"Transitions time = ([0-9\.]+)", stdout)
    total_transitions = extract(r"N. of transitions = ([0-9\.]+)", stdout)
    energy_transitions = extract(r"Energy for transitions = ([0-9\.]+)", stdout)
    energy_total_no_dpm = extract(r"Tot. Energy w/o DPM = ([0-9\.]+)", stdout)
    energy_total_dpm = extract(r"Tot. Energy w DPM = ([0-9\.]+)", stdout)

    workload_stats = WorkloadStats(
        active_time,
        inactive_time,
        time_run,
        time_idle,
        time_sleep,
        time_waiting,
        time_transitions,
        total_transitions,
        energy_transitions,
        energy_total_no_dpm,
        energy_total_dpm,
    )

    return workload_stats

def plot_saved_energy_ha():#function to run in loop ha policy incrementing threshold
    return

def plot_saved_energy_timeout():
    energy_saved = []
    timeout = []
    for t in range(LOWER_LIMIT, UPPER_LIMIT):
        workload_stats = dpm_sim_t(timeout=t, workload=WL1, inactive='i')
        saved = workload_stats.saved_energy()
        print(t)
        energy_saved.append(saved)
        timeout.append(t)

    plt.plot(timeout, energy_saved, label=f'Workload 1', marker='^', markersize=4, linestyle='-')

    energy_saved = []
    timeout = []
    for t in range(LOWER_LIMIT, UPPER_LIMIT):
        workload_stats = dpm_sim_t(timeout=t, workload=WL2, inactive='i')
        saved = workload_stats.saved_energy()
        print(t)
        energy_saved.append(saved)
        timeout.append(t)

    plt.plot(timeout, energy_saved, label=f'Workload 2', marker='^', markersize=4, linestyle='-')

    plt.xlabel('Timeout (s)')
    plt.ylabel('Energy Saved (J)')
    plt.title('Energy Saved vs. Timeout')
    plt.legend()
    #plt.show()
    plt.savefig(f'../graph/saved_idle_{LOWER_LIMIT}_{UPPER_LIMIT}.png', format="png", dpi=300)

def plot_workload_stats(path):
    workload = open(path, 'r')
    lines = workload.readlines()

    # Prepare time and state lists
    time_points = []
    state_points = []
    current_time = 0

    for line in lines:
        # Add an idle period if there's a gap before the next run period
        start_time, duration = line.split(' ', 1)
        start_time = int(start_time)
        duration = int(duration)

        if start_time > current_time:
            time_points.append(current_time)
            state_points.append(0)  # Idle state
            time_points.append(start_time)
            state_points.append(0)  # Idle state

        # Add the run period
        time_points.append(start_time)
        state_points.append(1)  # Run state
        time_points.append(start_time + duration)
        state_points.append(1)  # Run state

        # Update the current time to end of the run period
        current_time = start_time + duration
    print(time_points)
    print(str(time_points[-1]))
        

   # Plot the workload states over time
    plt.figure(figsize=(10, 4))
    plt.step(time_points, state_points, where='post', label="Workload State")
    plt.ylim(-0.1, 1.1)
    print(f'path: {path}, WL1:{WL1}, WL2:{WL2}')
    if path == WL1:
        plt.xlim(0, 600)
    if path == WL2:
        plt.xlim(0, 122224)
    plt.xlabel("Time")
    plt.ylabel("State (1=On, 0=Off)")
    plt.title("Workload On and Off Timeline")
    plt.grid(True)
    plt.legend()
    plt.savefig(f'../graph/workload2.png', format="png", dpi=300)

    plt.show()

#TODO implement plotting of power state
#TODO implement plotting of energy saved in function of Tto
#TODO implement plotting of idle and run time and their durations


#TODO implement plotting difference on energy saving between idle and sleep mode
def plot_saved_energy_comparison():
    timeouts = range(LOWER_LIMIT, UPPER_LIMIT)
    workloads = [WL1, WL2]
    colors = ['blue', 'green']

    for idx, workload in enumerate(workloads):
        energy_saved_idle = []
        energy_saved_sleep = []

        # Calcolare l'energia salvata per modalità "idle" e "sleep"
        for t in timeouts:
            stats_idle = dpm_sim_t(timeout=t, workload=workload, inactive='i')
            stats_sleep = dpm_sim_t(timeout=t, workload=workload, inactive='s')

            energy_saved_idle.append(stats_idle.saved_energy())
            energy_saved_sleep.append(stats_sleep.saved_energy())

        # Calcolare la differenza tra modalità
        energy_diff = np.array(energy_saved_idle) - np.array(energy_saved_sleep)

        # Plot differenza
        plt.plot(
            timeouts,
            energy_diff,
            label=f'Differenza {workload.split("/")[-1]}',
            color=colors[idx],
            marker='o',
            linestyle='--'
        )

    plt.axhline(0, color='red', linestyle=':', label='Zero Difference')
    plt.xlabel('Timeout (s)')
    plt.ylabel('Differenza Energia Salvata (J)')
    plt.title('Confronto Energia Salvata: Idle vs Sleep')
    plt.legend()
    plt.grid()
    plt.savefig(f'../graph/saved_energy_comparison_{LOWER_LIMIT}_{UPPER_LIMIT}.png', format="png", dpi=300)
    plt.show()

def plot_energy_usage_comparison():
    # Liste per memorizzare l'energia per idle e sleep
    energy_idle_1 = []
    energy_sleep_1 = []
    timeout_1 = []
    
    energy_idle_2 = []
    energy_sleep_2 = []
    timeout_2 = []
    
    for t in range(LOWER_LIMIT, UPPER_LIMIT):
        # Esegui la simulazione per il workload 1 (Idle)
        stats_idle_1 = dpm_sim_t(timeout=t, workload=WL1, inactive='i')
        energy_idle_1.append(stats_idle_1.energy_total_dpm)  # Senza le parentesi
        
        # Esegui la simulazione per il workload 1 (Sleep)
        stats_sleep_1 = dpm_sim_t(timeout=t, workload=WL1, inactive='s')
        energy_sleep_1.append(stats_sleep_1.energy_total_dpm)  # Senza le parentesi
        
        timeout_1.append(t)
        
        # Esegui la simulazione per il workload 2 (Idle)
        stats_idle_2 = dpm_sim_t(timeout=t, workload=WL2, inactive='i')
        energy_idle_2.append(stats_idle_2.energy_total_dpm)  # Senza le parentesi
        
        # Esegui la simulazione per il workload 2 (Sleep)
        stats_sleep_2 = dpm_sim_t(timeout=t, workload=WL2, inactive='s')
        energy_sleep_2.append(stats_sleep_2.energy_total_dpm)  # Senza le parentesi
        
        timeout_2.append(t)
    
    # Creazione del grafico per il Workload 1
    plt.figure(figsize=(10, 6))
    plt.plot(timeout_1, energy_idle_1, label='Energia in modalità Idle', marker='o', linestyle='-', color='blue')
    plt.plot(timeout_1, energy_sleep_1, label='Energia in modalità Sleep', marker='o', linestyle='--', color='red')
    plt.xlabel('Timeout (s)')
    plt.ylabel('Energia Utilizzata (J)')
    plt.title('Energia Utilizzata per Workload 1: Idle vs Sleep')
    plt.legend()
    plt.grid(True)
    plt.savefig(f'../graph/energia_utilizzata_workload1.png', format="png", dpi=300)
    
    # Creazione del grafico per il Workload 2
    plt.figure(figsize=(10, 6))
    plt.plot(timeout_2, energy_idle_2, label='Energia in modalità Idle', marker='o', linestyle='-', color='blue')
    plt.plot(timeout_2, energy_sleep_2, label='Energia in modalità Sleep', marker='o', linestyle='--', color='red')
    plt.xlabel('Timeout (s)')
    plt.ylabel('Energia Utilizzata (J)')
    plt.title('Energia Utilizzata per Workload 2: Idle vs Sleep')
    plt.legend()
    plt.grid(True)
    plt.savefig(f'../graph/energia_utilizzata_workload2.png', format="png", dpi=300)
    
    # Mostra i grafici
    plt.show()



if __name__ == "__main__":
    #plot_saved_energy_timeout()
    plot_workload_stats(WL2)
    plot_saved_energy_comparison()
    plot_energy_usage_comparison()