import numpy as np
import matplotlib.pyplot as plt

def generate_coronary_pressure(SBP=120, DBP=80, MAP=93, HR=60, 
                               t_peak_ratio=0.2, num_points=1001):
    """
    Generate coronary artery pressure waveform with two cosine functions in systole:
    - 0 ~ t_peak: DBP -> SBP (cosine upstroke)
    - t_peak ~ t_sys: SBP -> P_end_sys (cosine downstroke) 
    - t_sys ~ T_cycle: P_end_sys -> DBP (linear decay)
    
    Both systolic phases use cosine functions for smooth transitions.
    """

    # Cardiac cycle info
    T_cycle = 60.0 / HR
    T_sys = 0.35 * T_cycle
    T_dia = T_cycle - T_sys
    t_peak = t_peak_ratio * T_cycle  # peak timing as ratio of total cycle
    # End-systolic pressure (between SBP and DBP)
    P_end_sys = DBP + 0.5 * (SBP - DBP)

    # Time vector
    t = np.linspace(0, T_cycle, num_points)
    P = np.zeros_like(t)

    print(f"Cardiac cycle parameters:")
    print(f"  T_cycle = {T_cycle:.3f} s")
    print(f"  T_sys = {T_sys:.3f} s") 
    print(f"  t_peak = {t_peak:.3f} s (ratio = {t_peak_ratio})")
    print(f"  P_end_sys = {P_end_sys:.1f} mmHg")

    # --- Phase 1: 0 ~ t_peak (cosine upstroke) ---
    mask1 = (t <= t_peak)
    if np.any(mask1):
        # Cosine function: P(t) = DBP + (SBP-DBP) * (1-cos(π*t/t_peak))/2
        P[mask1] = DBP + (SBP - DBP) * (1 - np.cos(np.pi * t[mask1] / t_peak)) / 2
        print(f"Phase 1 (0~t_peak): DBP={DBP} -> SBP={SBP} (cosine upstroke)")

    # --- Phase 2: t_peak ~ T_sys (cosine downstroke) ---
    mask2 = (t > t_peak) & (t <= T_sys)
    if np.any(mask2):
        # Normalized time for this phase: tau = (t - t_peak) / (T_sys - t_peak)
        tau = (t[mask2] - t_peak) / (T_sys - t_peak)
        # Cosine function: P(t) = SBP + (P_end_sys-SBP) * (1-cos(π*tau))/2
        P[mask2] = SBP + (P_end_sys - SBP) * (1 - np.cos(np.pi * tau)) / 2
        print(f"Phase 2 (t_peak~T_sys): SBP={SBP} -> P_end_sys={P_end_sys:.1f} (cosine downstroke)")

    # --- Phase 3: T_sys ~ T_cycle (linear decay) ---
    mask3 = (t > T_sys)
    if np.any(mask3):
        slope = (DBP - P_end_sys) / T_dia
        P[mask3] = P_end_sys + slope * (t[mask3] - T_sys)
        print(f"Phase 3 (T_sys~T_cycle): P_end_sys={P_end_sys:.1f} -> DBP={DBP} (linear decay)")

    # --- MAP correction (shift to enforce correct mean) ---
    mean_val = np.trapz(P, t) / T_cycle
    P += (MAP - mean_val)
    print(f"MAP correction: {mean_val:.1f} -> {MAP:.1f} mmHg")

    return t, P




# 실행 예시
if __name__ == "__main__":
    print("=== Coronary Pressure Waveform Generator ===")
    
    # Generate pressure waveform
    t, P = generate_coronary_pressure(SBP=120, DBP=80, MAP=93, HR=60, t_peak_ratio=0.2)
    
    # Calculate parameters for plotting
    T_cycle = 60.0 / 60
    T_sys = 0.35 * T_cycle
    t_peak = 0.2 * T_cycle
    
    # Create comprehensive visualization
    plt.figure(figsize=(15, 10))
    
    # Main waveform plot
    plt.subplot(2, 2, 1)
    plt.plot(t, P, 'b-', linewidth=2, label='Pressure Waveform')
    
    # Mark key points
    key_times = [0, t_peak, T_sys, T_cycle]
    key_pressures = [P[0], P[np.argmin(np.abs(t - t_peak))], P[np.argmin(np.abs(t - T_sys))], P[-1]]
    plt.plot(key_times, key_pressures, 'ro', markersize=8, label='Key Points')
    
    # Add phase boundaries
    plt.axvline(x=t_peak, color='g', linestyle='--', alpha=0.7, label='Peak Time')
    plt.axvline(x=T_sys, color='r', linestyle='--', alpha=0.7, label='End of Systole')
    
    plt.xlabel('Time [s]')
    plt.ylabel('Pressure [mmHg]')
    plt.title('Coronary Pressure Waveform\n(Two Cosine Functions in Systole)')
    plt.grid(True, alpha=0.3)
    plt.legend()
    
    # Phase separation
    plt.subplot(2, 2, 2)
    mask1 = (t <= t_peak)
    mask2 = (t > t_peak) & (t <= T_sys)
    mask3 = (t > T_sys)
    
    plt.plot(t[mask1], P[mask1], 'r-', linewidth=3, label='Phase 1: Cosine Upstroke')
    plt.plot(t[mask2], P[mask2], 'orange', linewidth=3, label='Phase 2: Cosine Downstroke')
    plt.plot(t[mask3], P[mask3], 'b-', linewidth=3, label='Phase 3: Linear Decay')
    plt.plot(key_times, key_pressures, 'ko', markersize=6)
    
    plt.xlabel('Time [s]')
    plt.ylabel('Pressure [mmHg]')
    plt.title('Phase Separation')
    plt.grid(True, alpha=0.3)
    plt.legend()
    
    # Derivative analysis
    plt.subplot(2, 2, 3)
    dt = t[1] - t[0]
    derivative = np.gradient(P, dt)
    plt.plot(t, derivative, 'g-', linewidth=2, label='dP/dt')
    plt.axhline(y=0, color='k', linestyle='-', alpha=0.3)
    plt.axvline(x=t_peak, color='g', linestyle='--', alpha=0.7, label='Peak Time')
    plt.axvline(x=T_sys, color='r', linestyle='--', alpha=0.7, label='End of Systole')
    
    plt.xlabel('Time [s]')
    plt.ylabel('dP/dt [mmHg/s]')
    plt.title('Pressure Derivative')
    plt.grid(True, alpha=0.3)
    plt.legend()
    
    # Mathematical functions visualization
    plt.subplot(2, 2, 4)
    # Plot the actual mathematical functions
    t_phase1 = np.linspace(0, t_peak, 100)
    t_phase2 = np.linspace(t_peak, T_sys, 100)
    t_phase3 = np.linspace(T_sys, T_cycle, 100)
    
    # Phase 1: Cosine upstroke
    P_phase1 = 80 + (120 - 80) * (1 - np.cos(np.pi * t_phase1 / t_peak)) / 2
    
    # Phase 2: Cosine downstroke  
    tau = (t_phase2 - t_peak) / (T_sys - t_peak)
    P_end_sys = 80 + 0.5 * (120 - 80)
    P_phase2 = 120 + (P_end_sys - 120) * (1 - np.cos(np.pi * tau)) / 2
    
    # Phase 3: Linear decay
    slope = (80 - P_end_sys) / (T_cycle - T_sys)
    P_phase3 = P_end_sys + slope * (t_phase3 - T_sys)
    
    plt.plot(t_phase1, P_phase1, 'r-', linewidth=3, label='Phase 1: Cosine Upstroke')
    plt.plot(t_phase2, P_phase2, 'orange', linewidth=3, label='Phase 2: Cosine Downstroke')
    plt.plot(t_phase3, P_phase3, 'b-', linewidth=3, label='Phase 3: Linear Decay')
    
    plt.xlabel('Time [s]')
    plt.ylabel('Pressure [mmHg]')
    plt.title('Mathematical Functions')
    plt.grid(True, alpha=0.3)
    plt.legend()
    
    plt.tight_layout()
    plt.show()
    
    # Print summary
    print(f"\n=== Waveform Summary ===")
    print(f"Peak pressure: {np.max(P):.1f} mmHg at t = {t[np.argmax(P)]:.3f} s")
    print(f"Minimum pressure: {np.min(P):.1f} mmHg at t = {t[np.argmin(P)]:.3f} s")
    print(f"Mean pressure: {np.mean(P):.1f} mmHg")
    print(f"Pulse pressure: {np.max(P) - np.min(P):.1f} mmHg")
    
    # Test with different parameters
    print(f"\n=== Testing Different Parameters ===")
    
    # Hypertension
    print("\n1. Hypertension (SBP=160, DBP=100):")
    t2, P2 = generate_coronary_pressure(SBP=160, DBP=100, MAP=120, HR=70, t_peak_ratio=0.2)
    
    # Bradycardia
    print("\n2. Bradycardia (HR=45):")
    t3, P3 = generate_coronary_pressure(SBP=120, DBP=80, MAP=93, HR=45, t_peak_ratio=0.2)
    
    # Comparison plot
    plt.figure(figsize=(12, 6))
    plt.plot(t, P, 'b-', linewidth=2, label='Normal (SBP=120, DBP=80, HR=60)')
    plt.plot(t2, P2, 'r-', linewidth=2, label='Hypertension (SBP=160, DBP=100, HR=70)')
    plt.plot(t3, P3, 'g-', linewidth=2, label='Bradycardia (SBP=120, DBP=80, HR=45)')
    
    plt.xlabel('Time [s]')
    plt.ylabel('Pressure [mmHg]')
    plt.title('Pressure Waveform Comparison')
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.show()
