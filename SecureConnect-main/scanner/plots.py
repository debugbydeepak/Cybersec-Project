import matplotlib
matplotlib.use('Agg')  # Set backend for production/headless
import matplotlib.pyplot as plt
import io
import base64
import numpy as np
import random
from matplotlib.patches import ConnectionPatch

# Universal Aesthetics
LUXURY_TAN = '#C08552'
LUXURY_DARK = '#4B2E2B'
LUXURY_CREAM = '#FFF8F0'
SUCCESS_GREEN = '#27c93f'
DANGER_RED = '#ff5f56'
WARNING_GOLD = '#ffbd2e'

def get_base64_plot(fig):
    buffer = io.BytesIO()
    fig.savefig(buffer, format='png', bbox_inches='tight', transparent=True, dpi=120)
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    buffer.close()
    plt.close(fig)
    return image_base64

def get_vuln_distribution_plot(counts=None):
    if not counts:
        labels = ['BOLA', 'XSS', 'SQLI', 'SSRF', 'OTHER']
        sizes = [35, 20, 15, 20, 10]
    else:
        labels = list(counts.keys())
        sizes = list(counts.values())
        if sum(sizes) == 0:
            sizes = [1]
            labels = ['Operational']

    colors = [LUXURY_TAN, '#A67345', '#8C6139', '#735030', '#593E26']
    
    fig, ax = plt.subplots(figsize=(5, 5))
    
    # Create the Donut
    wedges, texts, autotexts = ax.pie(
        sizes, labels=labels, autopct='%1.1f%%', startangle=140,
        colors=colors, pctdistance=0.8,
        wedgeprops={'width': 0.4, 'edgecolor': 'none', 'antialiased': True},
        textprops={'color': LUXURY_TAN, 'weight': 'bold', 'fontsize': 9}
    )
    
    plt.setp(autotexts, size=8, weight="bold", color="white")
    plt.setp(texts, size=8)

    ax.set_title('VULNERABLE VECTOR NODES', color=LUXURY_TAN, weight='bold', size=12, pad=20)
    
    return get_base64_plot(fig)

def get_response_latency_plot():
    events = np.arange(1, 11)
    latency = [120, 145, 110, 180, 130, 210, 150, 140, 165, 125]
    
    fig, ax = plt.subplots(figsize=(8, 3))
    
    # Simulated Glow Effect by layering lines
    ax.plot(events, latency, color=LUXURY_TAN, linewidth=4, alpha=0.1)
    ax.plot(events, latency, color=LUXURY_TAN, linewidth=2, alpha=0.3)
    ax.plot(events, latency, color=LUXURY_TAN, linewidth=1, marker='o', markersize=4)
    
    ax.fill_between(events, latency, color=LUXURY_TAN, alpha=0.05)
    
    # Styling
    ax.set_facecolor('none')
    ax.set_title('AUTONOMOUS RESPONSE LATENCY (MS)', color=LUXURY_TAN, size=10, weight='bold', loc='left')
    
    # Grid and Spines
    ax.grid(True, linestyle='--', alpha=0.1, color=LUXURY_TAN)
    for spine in ax.spines.values():
        spine.set_visible(False)
    
    ax.tick_params(colors=LUXURY_TAN, labelsize=7)
    
    return get_base64_plot(fig)

def get_threat_intensity_plot():
    # Multi-layered intensity graph
    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    detected = [45, 78, 52, 91, 65, 88, 70]
    blocked = [30, 60, 40, 75, 50, 70, 55]

    fig, ax = plt.subplots(figsize=(10, 4))
    
    # Area fills with different intensities
    ax.fill_between(days, detected, color=LUXURY_TAN, alpha=0.1, label='Total Vectors')
    ax.fill_between(days, blocked, color=SUCCESS_GREEN, alpha=0.2, label='Auto-Remediated')
    
    # Glowing lines
    ax.plot(days, detected, color=LUXURY_TAN, linewidth=2, marker='h', markersize=6)
    ax.plot(days, blocked, color=SUCCESS_GREEN, linewidth=2, marker='D', markersize=5)

    ax.set_facecolor('none')
    ax.set_title('THREAT PROPAGATION & MITIGATION VELOCITY', color=LUXURY_TAN, size=12, weight='bold', pad=15)
    
    # Clean axes
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color(LUXURY_TAN)
    ax.spines['bottom'].set_color(LUXURY_TAN)
    ax.spines['left'].set_alpha(0.3)
    ax.spines['bottom'].set_alpha(0.3)
    
    ax.tick_params(colors=LUXURY_TAN, labelsize=8)
    
    legend = ax.legend(frameon=False, loc='upper right', fontsize=8)
    plt.setp(legend.get_texts(), color=LUXURY_TAN)
    
    return get_base64_plot(fig)

def get_attack_surface_radar_plot():
    categories = ['API Exposure', 'PII Risk', 'Logic Depth', 'Auth Entropy', 'DOM Leakage']
    N = len(categories)
    
    values = [75, 60, 90, 45, 80]
    values += values[:1]
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]
    
    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    
    # Radar Styling
    ax.set_facecolor('none')
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    
    plt.xticks(angles[:-1], categories, color=LUXURY_TAN, size=8, weight='bold')
    ax.set_rlabel_position(0)
    plt.yticks([25, 50, 75], ["25", "50", "75"], color=LUXURY_TAN, size=7, alpha=0.4)
    plt.ylim(0, 100)
    
    # Glowing Plot
    ax.plot(angles, values, color=LUXURY_TAN, linewidth=3, alpha=0.8)
    ax.fill(angles, values, color=LUXURY_TAN, alpha=0.2)
    
    # Grid custom
    ax.grid(color=LUXURY_TAN, alpha=0.2, linestyle='--')
    ax.spines['polar'].set_visible(False)
    
    ax.set_title('ATTACK SURFACE CORRELATION MATRIX', color=LUXURY_TAN, size=12, weight='bold', pad=30)
    
    return get_base64_plot(fig)

def get_kernel_load_plot():
    labels = ['JIT', 'OAST', 'V8', 'Logic']
    load = [random.randint(60, 95) for _ in range(4)]
    
    fig, ax = plt.subplots(figsize=(6, 4))
    
    # Horizontal bar for a more technical 'meter' look
    bars = ax.barh(labels, load, color=LUXURY_TAN, alpha=0.6, height=0.6)
    
    ax.set_facecolor('none')
    ax.set_xlim(0, 100)
    
    # Cleanup spines
    for spine in ax.spines.values():
        spine.set_visible(False)
    
    ax.tick_params(colors=LUXURY_TAN, labelsize=9)
    ax.set_title('KERNEL RESOURCE ALLOCATION (%)', color=LUXURY_TAN, size=11, weight='bold')
    
    # Adding text labels to the right of the bars
    for bar in bars:
        width = bar.get_width()
        ax.text(width + 2, bar.get_y() + bar.get_height()/2, f'{width}%', 
                va='center', color=LUXURY_TAN, weight='bold', size=8)

    return get_base64_plot(fig)

