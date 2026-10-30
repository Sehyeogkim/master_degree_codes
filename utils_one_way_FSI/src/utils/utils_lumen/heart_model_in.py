from tkinter import FALSE
import numpy as np
import matplotlib.pyplot as plt


def generate_coronary_pressure(P_in_norm_path, SBP, DBP, HR, save_path=None, plot=False):
    
    """
        Read the P_in_norm.dat file and transform to the patient's Pin data
        
        The normalized data (0-1 range) is scaled to actual blood pressure range:
        P_actual = P_norm * (SBP - DBP) + DBP
        
        Time is also scaled from 1s cycle to actual cardiac cycle:
        t_actual = t_norm * T_cycle (where T_cycle = 60/HR)

        Parameters:
        - P_in_norm_path: Path to normalized pressure data file
        - SBP: Systolic blood pressure (mmHg)
        - DBP: Diastolic blood pressure (mmHg) 
        - HR: Heart rate (bpm)
        - save_path: Path to save the scaled pressure data
        - plot: Whether to plot the waveform
    """

    # Calculate actual cardiac cycle parameters
    T_cycle = 60.0 / HR  # Actual cardiac cycle period
    
    # Read normalized data
    with open(P_in_norm_path, 'r') as f:
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
    P_actual = P_norm * (SBP - DBP) + DBP


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
        
        # Scaled actual data [ unit [mmHg] ]
        plt.subplot(2, 1, 2)
        plt.plot(t_actual, P_actual/1333.22, 'r-', linewidth=2, label='Scaled Data')
        plt.axhline(y=SBP/1333.22, color='g', linestyle='--', alpha=0.7, label=f'SBP ({SBP/1333.22:.1f} mmHg)')
        plt.axhline(y=DBP/1333.22, color='orange', linestyle='--', alpha=0.7, label=f'DBP ({DBP/1333.22:.1f} mmHg)')
        plt.xlabel('Time [s]')
        plt.ylabel('Pressure [mmHg]')
        plt.title(f'Scaled Pressure Data (T_cycle = {T_cycle:.3f}s)')
        plt.grid(True, alpha=0.3)
        plt.legend()
        
        plt.tight_layout()
        plt.show()
    
    return t_actual, P_actual

def generate_coronary_pressure_cos(SBP, DBP, HR, decay_ratio, save_path = None, plot = False,
                               t_peak_ratio = 0.2, num_points=1001):
    """
    Generate coronary artery pressure waveform with two cosine functions in systole:
    
    # 0.0s -> T_peak -> T_sys -> T_cycle
    - 0 ~ t_peak: DBP -> SBP (cosine upstroke)
    - t_peak ~ t_sys: SBP -> P_end_sys (cosine downstroke) 
    - t_sys ~ T_cycle: P_end_sys -> DBP (exponential decay)
    

    decay_ratio: 0.0 ~ 1.0 I would say. but no 0.0.
    """
    T_cycle = 60.0 / HR
    T_peak = t_peak_ratio * T_cycle  # peak timing as ratio of total cycle
    T_sys = T_peak + (1 - decay_ratio) * 0.2 * T_cycle
    
    # End-systolic pressure (between SBP and DBP)
    P_end_sys = DBP + 0.5 * (SBP - DBP)

    # Time vector
    t = np.linspace(0, T_cycle, num_points)
    P = np.zeros_like(t)

    # --- Phase 1: 0 ~ t_peak (cosine upstroke) ---
    mask1 = (t <= T_peak)
    if np.any(mask1):
        # Cosine function: P(t) = DBP + (SBP-DBP) * (1-cos(π*t/t_peak))/2
        P[mask1] = DBP + (SBP - DBP) * (1 - np.cos(np.pi * t[mask1] / T_peak)) / 2
        print(f"Phase 1 (0~t_peak): DBP={DBP} -> SBP={SBP} (cosine upstroke)")

    # --- Phase 2: t_peak ~ T_sys (cosine downstroke) ---
    mask2 = (t > T_peak) & (t <= T_sys)
    if np.any(mask2):
        # Normalized time for this phase: tau = (t - t_peak) / (T_sys - t_peak)
        tau = (t[mask2] - T_peak) / (T_sys - T_peak)
        # Cosine function: P(t) = SBP + (P_end_sys-SBP) * (1-cos(π*tau))/2
        P[mask2] = SBP + (P_end_sys - SBP) * (1 - np.cos(np.pi * tau)) / 2
        print(f"Phase 2 (t_peak~T_sys): SBP={SBP} -> P_end_sys={P_end_sys:.1f} (cosine downstroke)")

    # --- Phase 3: T_sys ~ T_cycle (exponential decay) ---
    # --- Phase 3: T_sys ~ T_cycle (exponential decay) ---
    mask3 = (t > T_sys)
    if np.any(mask3):
        """
        Exponential function passes two points:
        [1]. (T_sys, P_end_sys)
        [2]. (T_cycle, DBP)

        We use a normalized time s in [0, 1]:
            s = (t - T_sys) / (T_cycle - T_sys)

        And define:
            P(s) = DBP + (P_end_sys - DBP) * (exp(-k*s) - exp(-k)) / (1 - exp(-k))

        so that:
            P(0) = P_end_sys
            P(1) = DBP

        Larger decay_ratio -> larger k -> more dramatic drop.
        """
        t3 = t[mask3]
        dt_dia = T_cycle - T_sys
        s = (t3 - T_sys) / dt_dia  # normalized 0~1

        # Map decay_ratio (0~1) -> shape parameter k (0.1~6.0, for example)
        k_min, k_max = 0.1, 6.0
        k = k_min + decay_ratio * (k_max - k_min)

        # Avoid numerical issues when k is extremely small
        E = np.exp(-k)
        denom = 1.0 - E
        if np.isclose(denom, 0.0):
            # fallback to simple linear interpolation if k is too small
            P[mask3] = P_end_sys + (DBP - P_end_sys) * s
        else:
            num = np.exp(-k * s) - E
            P[mask3] = DBP + (P_end_sys - DBP) * (num / denom)

        print(f"Phase 3 (T_sys~T_cycle): P_end_sys={P_end_sys:.1f} -> DBP={DBP} "
              f"(exponential decay, decay_ratio={decay_ratio:.3f}, k={k:.3f})")


    if save_path:
        with open(save_path, 'w') as f:
            #f.write(f"{len(t)}\n")
            for t_val, p_val in zip(t, P):
                f.write(f"{t_val:.6f} {p_val:.6f}\n")
        print(f"Pressure data saved to {save_path} ({len(t)} points)")


    #plot
    if plot:
        SBP_mmhg = SBP / 1333.22
        DBP_mmhg = DBP / 1333.22
        plt.figure(figsize=(12, 8))
        plt.plot(t, P / 1333.22, 'b-', linewidth=2, label='Pressure Waveform')
        plt.axhline(y=SBP_mmhg, color='g', linestyle='--', alpha=0.7, label=f'SBP ({SBP_mmhg:.1f} mmHg)')
        plt.axhline(y=DBP_mmhg, color='orange', linestyle='--', alpha=0.7, label=f'DBP ({DBP_mmhg:.1f} mmHg)')
        plt.xlabel('Time [s]')
        plt.ylabel('Pressure [mmHg]')
        plt.title(f'Coronary Pressure Waveform\n(SBP={SBP_mmhg:.1f}mmHg, DBP={DBP_mmhg:.1f}mmHg, Decay ratio={decay_ratio:.2f}\n HR={HR}, T_sys={T_sys:.3f}s')
        plt.grid(True, alpha=0.3)
        plt.legend()
        plt.show()



    return t, P

def generate_coronary_pressure_decay_ratio(SBP, DBP, HR, T_s, DR, save_path=None, plot=False, num_points=1001):
    """
    Generate coronary pressure waveform using sin² function for systole 
    and exponential decay for diastole.
    
    Mathematical formulation:
    - Systolic phase (0 ≤ t ≤ T_s): 
      P(t) = P_d + (P_s - P_d) * sin²(πt/(2T_s))
    
    - Diastolic phase (T_s < t ≤ T):
      P(t) = P_d + (P_s - P_d) * exp(-(t - T_s)/(DR * T))
    
    Parameters:
    - SBP: Systolic blood pressure (mmHg)
    - DBP: Diastolic blood pressure (mmHg)
    - HR: Heart rate (bpm)
    - T_s: Systolic duration (seconds)
    - DR: Decay ratio (dimensionless, typically 0.4-0.6)
    - save_path: Path to save the pressure data (format: first line = number of points, then t P pairs)
    - plot: Whether to plot the waveform
    - num_points: Number of points in the time array (default: 1001)
    
    Returns:
    - t: Time array (seconds)
    - P: Pressure array (Pa)
    """
    
    # Calculate cardiac cycle parameters
    T_cycle = 60.0 / HR  # Total cardiac cycle period (seconds)
    
    # Convert pressure from mmHg to Pa (dyn/cm²)
    P_s = SBP  # Systolic pressure in Pa
    P_d = DBP # Diastolic pressure in Pa
    
    # Generate time array
    t = np.linspace(0, T_cycle, num_points)
    
    # Initialize pressure array
    P = np.zeros_like(t)
    
    # Calculate decay time constant
    tau = DR * T_cycle
    
    # Systolic phase: sin² function (0 ≤ t ≤ T_s)
    mask_systolic = t <= T_s
    if np.any(mask_systolic):
        t_systolic = t[mask_systolic]
        # P(t) = P_d + (P_s - P_d) * sin²(πt/(2T_s))
        P[mask_systolic] = P_d + (P_s - P_d) * np.sin(np.pi * t_systolic / (2 * T_s))**2
    
    # Diastolic phase: exponential decay (T_s < t ≤ T)
    mask_diastolic = t > T_s
    if np.any(mask_diastolic):
        t_diastolic = t[mask_diastolic]
        # P(t) = P_d + (P_s - P_d) * exp(-(t - T_s)/(DR * T))
        P[mask_diastolic] = P_d + (P_s - P_d) * np.exp(-(t_diastolic - T_s) / tau)
    
    # Ensure continuity at transition point (T_s)
    # At t = T_s: sin²(π/2) = 1, so P = P_s
    # At t = T_s: exp(0) = 1, so P = P_s
    # Both should equal P_s, so continuity is guaranteed
    
    # Save data
    if save_path:
        with open(save_path, 'w') as f:
            #f.write(f"{len(t)}\n")
            for t_val, p_val in zip(t, P):
                f.write(f"{t_val:.6f} {p_val:.6f}\n")
        print(f"Pressure data saved to {save_path} ({len(t)} points)")
    
    # Plot waveform
    if plot:
        plt.figure(figsize=(12, 8))
        
        plt.subplot(2, 1, 1)
        plt.plot(t, P / 1333.22, 'b-', linewidth=2, label='Pressure Waveform')
        plt.axvline(x=T_s, color='r', linestyle='--', alpha=0.7, label=f'Systolic Duration (T_s = {T_s:.3f}s)')
        plt.axhline(y=SBP/1333.22, color='g', linestyle='--', alpha=0.7, label=f'SBP ({SBP:.1f} mmHg)')
        plt.axhline(y=DBP/1333.22, color='orange', linestyle='--', alpha=0.7, label=f'DBP ({DBP:.1f} mmHg)')
        plt.xlabel('Time [s]')
        plt.ylabel('Pressure [mmHg]')
        plt.title(f'Coronary Pressure Waveform\n(SBP={SBP:.1f}mmHg, DBP={DBP:.1f}mmHg, HR={HR}, T_s={T_s:.3f}s, DR={DR:.2f})')
        plt.grid(True, alpha=0.3)
        plt.legend()
        
        plt.subplot(2, 1, 2)
        # Show systolic and diastolic phases separately
        plt.plot(t[mask_systolic], P[mask_systolic] / 1333.22, 'r-', linewidth=2, 
                label=f'Systolic Phase: sin² (0 ≤ t ≤ {T_s:.3f}s)')
        plt.plot(t[mask_diastolic], P[mask_diastolic] / 1333.22, 'b-', linewidth=2, 
                label=f'Diastolic Phase: exp decay ({T_s:.3f}s < t ≤ {T_cycle:.3f}s)')
        plt.axhline(y=SBP, color='g', linestyle='--', alpha=0.5)
        plt.axhline(y=DBP, color='orange', linestyle='--', alpha=0.5)
        plt.xlabel('Time [s]')
        plt.ylabel('Pressure [mmHg]')
        plt.title('Phase Separation')
        plt.grid(True, alpha=0.3)
        plt.legend()
        
        plt.tight_layout()
        plt.show()
    
    return t, P


# example
if __name__ == "__main__":
    print("=== Coronary Pressure Scaling from Normalized Data ===")
    
    P_norm_path = "/home/jeff/project/37.1D_real/scripts/P_in_normalized.dat"
    
    # Test with different parameters
    print("\n1. Normal parameters (SBP=120, DBP=80, HR=60):")
    t1, P1 = generate_coronary_pressure_decay_ratio(SBP=120, DBP=80, HR=60, tau=0.1, 
                                       save_path="P_in_decay_ratio_normal.dat", plot=False)
    
    print("\n2. Hypertension (SBP=160, DBP=100, HR=70):")
    t2, P2 = generate_coronary_pressure(P_norm_path, SBP=160, DBP=100, HR=70, 
                                       save_path="P_in_scaled_hypertension.dat", plot=False)
    
    print("\n3. Bradycardia (SBP=120, DBP=80, HR=45):")
    t3, P3 = generate_coronary_pressure(P_norm_path, SBP=120, DBP=80, HR=45, 
                                       save_path="P_in_scaled_bradycardia.dat", plot=False)
    
    # Test new cosine + exponential function
    print("\n4. New cosine + exponential function (SBP=120, DBP=80, HR=60, decay_ratio=0.5):")
    t4, P4 = generate_coronary_pressure_cos(SBP=120, DBP=80, HR=60, decay_ratio=0.5,
                                             save_path="P_in_cos_exp.dat", plot=True)
    
    # Comparison plot
    plt.figure(figsize=(12, 8))
    
    plt.subplot(2, 1, 1)
    plt.plot(t1, P1/1333.22, 'b-', linewidth=2, label='Normal (SBP=120, DBP=80, HR=60)')
    plt.plot(t2, P2/1333.22, 'r-', linewidth=2, label='Hypertension (SBP=160, DBP=100, HR=70)')
    plt.plot(t3, P3/1333.22, 'g-', linewidth=2, label='Bradycardia (SBP=120, DBP=80, HR=45)')
    plt.xlabel('Time [s]')
    plt.ylabel('Pressure [mmHg]')
    plt.title('Scaled Coronary Pressure Comparison')
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
    print(f"All scaled pressure data saved successfully!")
    print(f"Files created:")
    print(f"  - P_in_scaled_normal.dat")
    print(f"  - P_in_scaled_hypertension.dat") 
    print(f"  - P_in_scaled_bradycardia.dat")
