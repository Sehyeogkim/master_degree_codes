"""
    RCR (Windkessel) Model for Hemodynamic Simulation
    Converted from MATLAB code to Python

    Main Features:
    Logical Structure:
    1. Heart out flow rate
    2. Windkessel model for the aortic heart pressure
    - Input parameters: SBP, DBP, decay_ratio
    - Output parameters: heart Pressure
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from scipy.interpolate import interp1d


def pressure_wave_form(inflow_path:str, SBP :float, DBP :float, tau :float, number_of_cycles :int, save_path:str = "pressure.dat", plot:bool = False):
    """
    Calculate the pressure waveform using the RCR model.
    
    Parameters:
    - inflow_path: Path to the inflow data file
    - SBP: Systolic blood pressure (dyn/cm²)
    - DBP: Diastolic blood pressure (dyn/cm²)
    - tau: Time constant (seconds)
    - number_of_cycles: Number of cycles to iterate

    output:
    - generate save_path file
    """


    # ============================================================================
    # 1. Data Loading and Preprocessing
    # ============================================================================
    print("Loading data...")
    inflow_file = Path(inflow_path)
    if not inflow_file.exists():
        raise FileNotFoundError(f"{inflow_path} file not found.")

    data = np.loadtxt(inflow_file)
    if data.ndim != 2 or data.shape[1] < 2:
        raise ValueError("Inflow file must contain at least two columns (time, flow).")

    # Sort data just in case and normalize time to start at zero
    data = data[np.argsort(data[:, 0])]
    time_raw = data[:, 0] - data[0, 0]
    flow_raw = data[:, 1]

    if np.any(np.diff(time_raw) <= 0):
        raise ValueError("Time values must be strictly increasing.")

    cycle_duration = time_raw[-1]
    if cycle_duration <= 0:
        raise ValueError("Cycle duration must be positive.")

    # Normalize to a 0–1 s window with 0.001 s resolution (1001 points)
    normalized_time = np.linspace(0.0, 1.0, 1001)
    scaled_time = normalized_time * cycle_duration

    interp_func = interp1d(time_raw, flow_raw, kind='linear', fill_value='extrapolate')
    flow_single_cycle = interp_func(scaled_time)

    # ============================================================================
    # 2. Flow Rate Data Interpolation
    # ============================================================================
    # Create high-resolution time vector (0.001s interval)
    time = normalized_time.copy()
    flow = flow_single_cycle

    # Flow rate plot
    plt.figure(figsize=(12, 5))
    plt.subplot(1, 2, 1)
    plt.plot(time, flow)
    plt.xlabel('Time (s)')
    plt.ylabel('Flow rate (cm³/s)')
    plt.title('Interpolated Flow Rate')
    plt.grid(True)
    plt.tight_layout()

    # ============================================================================
    # 3. RCR Parameter Calculation
    # ============================================================================
    # Calculate Mean Arterial Pressure (dyn/cm²)
    MAP = (2 * DBP + SBP) / 3
    mean_flow = np.mean(flow[:-1])
    if np.isclose(mean_flow, 0.0):
        raise ValueError("Mean flow must be non-zero to compute resistances.")

    # Calculate total resistance: R_total = MAP / mean_flow
    total_resistance = MAP / mean_flow

    # Proximal resistance (10% of total resistance)
    proximal_resistance = total_resistance * 0.10

    # Distal resistance (remaining 90%)
    distal_resistance = total_resistance - proximal_resistance

    # Calculate capacitance: C = tau / R_distal
    capacitance = tau / distal_resistance

    print(f"\nRCR Parameters:")
    print(f"  Total Resistance (R_total): {total_resistance:.2f} dyn·s/cm⁵")
    print(f"  Proximal Resistance (R_proximal): {proximal_resistance:.2f} dyn·s/cm⁵")
    print(f"  Distal Resistance (R_distal): {distal_resistance:.2f} dyn·s/cm⁵")
    print(f"  Capacitance (C): {capacitance:.6f} cm⁵/dyn")
    print(f"  Mean Arterial Pressure (MAP): {MAP:.2f} mmHg")

    # ============================================================================
    # 4. Time Iteration Calculation (RCR Model)
    # ============================================================================
    time_step_size = time[1] - time[0]  # Time step size (seconds)
    if time_step_size <= 0:
        raise ValueError("Time step must be positive.")

    steps_per_cycle = len(flow) - 1
    total_steps = steps_per_cycle * number_of_cycles + 1

    # Extend flow rate data to multiple cycles
    flow_extended = np.tile(flow[:-1], number_of_cycles)
    flow_extended = np.append(flow_extended, flow[-1])
    time_extended = np.linspace(0.0, number_of_cycles, total_steps)
    
    # Initialize pressure arrays
    pressures_cap = np.zeros(total_steps)
    pressures_prox = np.zeros(total_steps)
    pressures_cap[0] = SBP  # Initial pressure (dyn/cm²)

    print(f"\nCalculation Parameters:")
    print(f"  Time step size: {time_step_size:.4f} seconds")
    print(f"  Number of cycles: {number_of_cycles}")
    print(f"  Total number of time steps: {total_steps}")
    print(f"  Capacitance: {capacitance:.6e} cm⁵/dyn")

    venous_pressure = 0.0  # dyn/cm²

    # Calculate pressure using discrete RCR model
    print("\nCalculating pressure...")
    for n in range(1, total_steps):
        q_in = flow_extended[n-1]
        dP_cap = (time_step_size / capacitance) * (q_in - (pressures_cap[n-1] - venous_pressure) / distal_resistance)
        pressures_cap[n] = pressures_cap[n-1] + dP_cap
        pressures_prox[n-1] = pressures_cap[n-1] + proximal_resistance * q_in

        if n % 1000 == 0 or n == total_steps - 1:
            print(f"  Progress: {n}/{total_steps-1} ({100*n/(total_steps-1):.1f}%)")

    pressures_prox[-1] = pressures_cap[-1] + proximal_resistance * flow_extended[-1]

    # ============================================================================
    # 5. Result Visualization
    # ============================================================================
    dyn_to_mmhg = 1.0 / 1333.2237
    pressures_prox_mmHg = pressures_prox * dyn_to_mmhg

    # Extract pressure data from the last cycle (1001 points)
    points_per_cycle = len(time)
    pressure_final_cycle_dyn = pressures_prox[-points_per_cycle:]

    # Save final cycle pressure waveform
    if save_path:
        np.savetxt(save_path, np.column_stack((time, pressure_final_cycle_dyn)), fmt="%.5f %.5f")
        print(f"Saved final cycle pressure waveform (dyn/cm²) to {save_path}")
    
    if plot:
        plt.subplot(1, 2, 2)
        plt.plot(time_extended, pressures_prox_mmHg)
        plt.xlabel('Time (s)')
        plt.ylabel('Pressure (mmHg)')
        plt.title('Pressure Convergence over Cycles')
        plt.grid(True)
        plt.tight_layout()
        plt.show()

    # ============================================================================
    # Result Summary
    # ============================================================================
    pressure_final_cycle_mmHg = pressure_final_cycle_dyn * dyn_to_mmhg
    print(f"\nResult Summary:")
    print(f"  Final pressure range: {np.min(pressure_final_cycle_dyn):.2f} ~ {np.max(pressure_final_cycle_dyn):.2f} dyn/cm² "
          f"({np.min(pressure_final_cycle_mmHg):.2f} ~ {np.max(pressure_final_cycle_mmHg):.2f} mmHg)")
    print(f"  Mean pressure (last cycle): {np.mean(pressure_final_cycle_dyn):.2f} dyn/cm² "
          f"({np.mean(pressure_final_cycle_mmHg):.2f} mmHg)")
    print(f"  Calculation complete!")

def scale_pressure(pressure_path:str, SBP:float, DBP:float, save_path:str = "pressure_scaled.dat", plot:bool = False):
    """
    Scale the pressure waveform to the given SBP and DBP.
    
    Parameters:
    - pressure_path: Path to the pressure data file
    - SBP: Systolic blood pressure (dyn/cm²)
    - DBP: Diastolic blood pressure (dyn/cm²)
    """
    data = np.loadtxt(pressure_path)
    time = data[:, 0]
    pressure = data[:, 1]
    p_min = np.min(pressure)
    p_max = np.max(pressure)

    if np.isclose(p_max, p_min):
        raise ValueError("Pressure waveform has zero dynamic range; cannot scale.")

    # Linearly map min -> DBP and max -> SBP (dyn/cm²)
    pressure_scaled = (pressure - p_min) / (p_max - p_min) * (SBP - DBP) + DBP
    np.savetxt(save_path, np.column_stack((time, pressure_scaled)), fmt="%.5f %.5f")

    #plot the pressure waveform (mmhG)
    if plot:
        plt.figure(figsize=(12, 5))
        plt.plot(time, pressure_scaled / 1333.27)
        plt.xlabel('Time (s)')
        plt.ylabel('Pressure (dyn/cm²)')
        plt.title('Scaled Pressure Waveform (mmHg)')
        plt.grid(True)
        plt.tight_layout()
        plt.show()


if __name__ == "__main__":


    inflow_path = 'inflow.dat'
    SBP = 120 * 1333.27
    DBP = 80 * 1333.27
    tau = 1.5
    number_of_cycles = 20
    save_path = 'pressure.dat'
    pressure_wave_form(inflow_path=inflow_path, SBP=SBP, DBP=DBP, tau=tau, number_of_cycles=number_of_cycles, save_path=save_path, plot=True)
    scale_pressure(pressure_path=save_path, SBP=SBP, DBP=DBP, save_path='pressure_scaled.dat', plot=True)

