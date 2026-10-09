import os
import numpy as np
import plotly.graph_objects as go
import yaml

with open('config/parameters.yaml', 'r') as f:
    config = yaml.safe_load(f)

L = config['module_a']['geometry']['L']['value']
dm = config['module_a']['geometry']['dm']['value']
dw = config['module_a']['geometry']['dm']['value'] * 4
tm = config['module_a']['geometry']['tm']['value']

os.makedirs('figures', exist_ok=True)

def generate_diagrams(module_name, catalyst_location='annulus', feed_label='Feed In', sweep_label='Sweep In', perm_label='Permeate', retentate_label='Retentate'):
    # 2D Cross Section
    fig = go.Figure()

    # Outer Wall
    theta = np.linspace(0, 2*np.pi, 100)
    x_wall = dw/2 * np.cos(theta)
    y_wall = dw/2 * np.sin(theta)
    fig.add_trace(go.Scatter(x=x_wall, y=y_wall, mode='lines', line=dict(color='gray', width=4), name='Outer Wall', fill='toself', fillcolor='rgba(200,200,200,0.1)'))

    # Membrane
    x_mem = dm/2 * np.cos(theta)
    y_mem = dm/2 * np.sin(theta)
    fig.add_trace(go.Scatter(x=x_mem, y=y_mem, mode='lines', line=dict(color='blue', width=4), name='Membrane', fill='toself', fillcolor='rgba(100,150,255,0.2)'))

    # Catalyst
    if catalyst_location == 'annulus':
        r_cat = np.random.uniform(dm/2, dw/2, 500)
    else: # lumen
        r_cat = np.random.uniform(0, dm/2, 500)
        
    theta_cat = np.random.uniform(0, 2*np.pi, 500)
    x_cat = r_cat * np.cos(theta_cat)
    y_cat = r_cat * np.sin(theta_cat)
    fig.add_trace(go.Scatter(x=x_cat, y=y_cat, mode='markers', marker=dict(color='green', size=3, opacity=0.6), name='Catalyst Pellets'))

    fig.update_layout(
        title=f'2D Cross Section ({module_name})',
        xaxis=dict(scaleanchor="y", scaleratio=1, showgrid=False, zeroline=False),
        yaxis=dict(showgrid=False, zeroline=False),
        template='plotly_white'
    )
    fig.write_image(f"figures/2d_cross_section_{module_name.lower().replace(' ', '_')}.png")

    # 3D Diagram (Cutaway)
    fig3 = go.Figure()

    z_mesh = np.linspace(0, L, 50)
    theta_mesh = np.linspace(0, np.pi, 30) # Only half cylinder for cutaway
    Z, Theta = np.meshgrid(z_mesh, theta_mesh)

    R_wall = (dw/2) * 5
    R_mem = (dm/2) * 5

    X_wall = R_wall * np.cos(Theta)
    Y_wall = R_wall * np.sin(Theta)

    X_mem = R_mem * np.cos(Theta)
    Y_mem = R_mem * np.sin(Theta)

    fig3.add_trace(go.Surface(x=Z, y=X_mem, z=Y_mem, colorscale='Blues', opacity=0.8, showscale=False, name="Membrane"))
    fig3.add_trace(go.Surface(x=Z, y=X_wall, z=Y_wall, colorscale='Greys', opacity=0.3, showscale=False, name="Outer Wall"))

    if catalyst_location == 'lumen':
        fig3.add_trace(go.Scatter3d(
            x=[-0.05, 0], y=[0, 0], z=[0, 0],
            mode='lines+text', line=dict(color='red', width=5),
            text=[feed_label, ""], textposition="middle left"
        ))
        fig3.add_trace(go.Scatter3d(
            x=[L/2, L/2], y=[R_mem, R_wall], z=[0, 0],
            mode='lines+text', line=dict(color='orange', width=3),
            text=["", perm_label], textposition="middle right"
        ))
        fig3.add_trace(go.Scatter3d(
            x=[L, L+0.05], y=[0, 0], z=[0, 0],
            mode='lines+text', line=dict(color='green', width=5),
            text=["", retentate_label], textposition="middle right"
        ))
    else:
        fig3.add_trace(go.Scatter3d(
            x=[-0.05, 0], y=[R_wall/2, R_wall/2], z=[0, 0],
            mode='lines+text', line=dict(color='red', width=5),
            text=[feed_label, ""], textposition="middle left"
        ))
        fig3.add_trace(go.Scatter3d(
            x=[L+0.05, L], y=[0, 0], z=[0, 0],
            mode='lines+text', line=dict(color='blue', width=5),
            text=[sweep_label, ""], textposition="middle right"
        ))

    fig3.update_layout(
        title=f"3D Reactor Cutaway ({module_name})",
        scene=dict(
            xaxis_title="Length (m)",
            yaxis_title="Radius (m)",
            zaxis_title="Radius (m)",
            aspectmode="data"
        ),
        template="plotly_white"
    )
    fig3.write_image(f"figures/3d_cutaway_{module_name.lower().replace(' ', '_')}.png")

generate_diagrams("Module A", "annulus", "CO2/H2 Feed", "N2 Sweep", "H2O Permeate", "Syngas Retentate")
generate_diagrams("Module B", "lumen", "NH3 Feed", "N/A", "H2 Permeate", "N2/H2 Retentate")

print("Generated all figures.")
