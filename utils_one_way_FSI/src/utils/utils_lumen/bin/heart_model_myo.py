import numpy as np
import matplotlib.pyplot as plt

def generate_myocardial_pressure(P_myo_norm_path, SBP=120, HR=60, save_path=None, plot=False, P_ratio = 1.4):
    
    """
        Read the P_myo_norm.dat file and transform to the patient's Pmyo data
        
        The normalized data (0-1 range) is scaled to actual blood pressure range:
        P_myo_peak = 1.2 * SBP
        P_myo_low  = 10 mmhg = 10 *1333.22 dyne/cm^2

        P_actual = P_myo_norm * (P_myo_peak - P_myo_low) + P_myo_low
        
        Time is also scaled from 1s cycle to actual cardiac cycle:
        t_actual = t_norm * T_cycle (where T_cycle = 60/HR)

        Parameters:
        - P_myo_norm_path: Path to normalized pressure data file
        - SBP: Systolic blood pressure (mmHg)
        - HR: Heart rate (bpm)
        - save_path: Path to save the scaled pressure data
        - plot: Whether to plot the waveform
    """


    # Calculate actual cardiac cycle parameters
    T_cycle = 60.0 / HR  # Actual cardiac cycle period
    P_myo_peak = P_ratio * SBP * 1333.22  # Convert to Pa (mmHg to Pa)
    P_myo_low = 14 * 1333.22  # 14 mmHg in Pa
    
    # Read normalized data
    with open(P_myo_norm_path, 'r') as f:
        lines = f.readlines()
    
    # Get number of data points
    num_points_file = int(lines[0].strip())
    
    # Parse normalized data
    data = []
    for i in range(1, num_points_file + 1):
        parts = lines[i].strip().split()
        t_norm = float(parts[0])  # Normalized time (0-1s)
        P_norm = float(parts[1])  # Normalized pressure (0-1)
        data.append([t_norm, P_norm])
    
    data = np.array(data)
    t_norm = data[:, 0]  # 0 to 1 second
    P_norm = data[:, 1]  # 0 to 1 normalized pressure
    

    # Scale time from 1s to actual cardiac cycle
    t_actual = t_norm * T_cycle
    
    # Scale pressure from normalized (0-1) to actual blood pressure range
    P_actual = P_norm * (P_myo_peak - P_myo_low) + P_myo_low

    # Save scaled data
    if save_path:
        # Save data with just space between t and P values, no header
        with open(save_path, 'w') as f:
            for t, p in zip(t_actual, P_actual):
                f.write(f"{t:.6f} {p:.6f}\n")
        print(f"Scaled pressure data saved to {save_path}")
    
    # Plot comparison
    if plot:
        plt.figure(figsize=(15, 10))
        
        # Original normalized data
        plt.subplot(2, 1, 1)
        plt.plot(t_norm, P_norm, 'b-', linewidth=2, label='Normalized Data')
        plt.xlabel('Time [s]')
        plt.ylabel('Normalized Pressure [0-1]')
        plt.title('Original Normalized Data (1s cycle)')
        plt.grid(True, alpha=0.3)
        plt.legend()
        
        # Scaled actual data (Pressure unit [mmHg])
        plt.subplot(2, 1, 2)
        plt.plot(t_actual, P_actual / 1333.22, 'r-', linewidth=2, label='Scaled Data')
        plt.axhline(y=P_myo_peak/1333.22, color='g', linestyle='--', alpha=0.7, label=f'P_myo_peak ({P_myo_peak/1333.22:.1f} mmHg)')
        plt.axhline(y=P_myo_low/1333.22, color='orange', linestyle='--', alpha=0.7, label=f'P_myo_low ({P_myo_low/1333.22:.1f} mmHg)')
        plt.xlabel('Time [s]')
        plt.ylabel('Pressure [mmHg]')
        plt.title(f'Scaled Pressure Data (T_cycle = {T_cycle:.3f}s)')
        plt.grid(True, alpha=0.3)
        plt.legend()
    

        plt.tight_layout()
        plt.show()
    
    return t_actual, P_actual


# examples
if __name__ == "__main__":
    print("=== Myocardial Pressure Scaling from Normalized Data ===")
    
    P_norm_path = "/home/jeff/project/37.1D_real/scripts/P_myo_normalized.dat"
    
    # Test with different parameters
    print("\n1. Normal parameters (SBP=120, HR=60):")
    t1, P1 = generate_myocardial_pressure(P_norm_path, SBP=120, HR=60, 
                                         save_path="P_myo_scaled_normal.dat", plot=True)
    
    print("\n2. Hypertension (SBP=160, HR=70):")
    t2, P2 = generate_myocardial_pressure(P_norm_path, SBP=160, HR=70, 
                                         save_path="P_myo_scaled_hypertension.dat", plot=False)
    
    print("\n3. Bradycardia (SBP=120, HR=45):")
    t3, P3 = generate_myocardial_pressure(P_norm_path, SBP=120, HR=45, 
                                         save_path="P_myo_scaled_bradycardia.dat", plot=False)
    
    # Comparison plot
    plt.figure(figsize=(12, 8))
    
    plt.subplot(2, 1, 1)
    plt.plot(t1, P1/1333.22, 'b-', linewidth=2, label='Normal (SBP=120, HR=60)')
    plt.plot(t2, P2/1333.22, 'r-', linewidth=2, label='Hypertension (SBP=160, HR=70)')
    plt.plot(t3, P3/1333.22, 'g-', linewidth=2, label='Bradycardia (SBP=120, HR=45)')
    plt.xlabel('Time [s]')
    plt.ylabel('Pressure [mmHg]')
    plt.title('Scaled Myocardial Pressure Comparison')
    plt.grid(True, alpha=0.3)
    plt.legend()
    
    plt.subplot(2, 1, 2)
    # Show time scaling effect
    plt.plot(t1, P1/1333.22, 'b-', linewidth=2, label=f'HR=60 (T_cycle={60/60:.3f}s)')
    plt.plot(t2, P2/1333.22, 'r-', linewidth=2, label=f'HR=70 (T_cycle={60/70:.3f}s)')
    plt.plot(t3, P3/1333.22, 'g-', linewidth=2, label=f'HR=45 (T_cycle={60/45:.3f}s)')
    plt.xlabel('Time [s]')
    plt.ylabel('Pressure [mmHg]')
    plt.title('Time Scaling Effect (Different Heart Rates)')
    plt.grid(True, alpha=0.3)
    plt.legend()
    
    plt.tight_layout()
    plt.show()
    
    print(f"\n=== Final Summary ===")
    print(f"All scaled myocardial pressure data saved successfully!")
    print(f"Files created:")
    print(f"  - P_myo_scaled_normal.dat")
    print(f"  - P_myo_scaled_hypertension.dat") 
    print(f"  - P_myo_scaled_bradycardia.dat")
