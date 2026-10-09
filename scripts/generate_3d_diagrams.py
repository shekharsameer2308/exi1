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
    fig.add_trace(go.Scatter(x=x_wall, y=y_wall, mode='lines', line=dict(color='gray', width=6), name='Outer Wall', fill='toself', fillcolor='rgba(200,200,200,0.1)'))

    # Membrane
    x_mem = dm/2 * np.cos(theta)
    y_mem = dm/2 * np.sin(theta)
    fig.add_trace(go.Scatter(x=x_mem, y=y_mem, mode='lines', line=dict(color='black' if catalyst_location == 'lumen' else 'blue', width=6), name='Membrane (Pd/Zeolite)', fill='toself', fillcolor='rgba(100,150,255,0.05)'))

    # Catalyst (Closely Packed Bed Grid)
    pellet_radius_2d = dm / 30
    x_grid = np.arange(-dw/2, dw/2, pellet_radius_2d * 2.2)
    y_grid = np.arange(-dw/2, dw/2, pellet_radius_2d * 2.2)
    xx, yy = np.meshgrid(x_grid, y_grid)
    
    # Offset every other row for hexagonal close packing look
    for i in range(yy.shape[0]):
        if i % 2 == 1:
            xx[i] += pellet_radius_2d * 1.1
            
    xx_flat, yy_flat = xx.flatten(), yy.flatten()
    
    x_cat, y_cat = [], []
    for x, y in zip(xx_flat, yy_flat):
        r = np.sqrt(x**2 + y**2)
        if catalyst_location == 'annulus':
            if r > dm/2 + pellet_radius_2d and r < dw/2 - pellet_radius_2d:
                x_cat.append(x)
                y_cat.append(y)
        else: # lumen
            if r < dm/2 - pellet_radius_2d:
                x_cat.append(x)
                y_cat.append(y)
                
    fig.add_trace(go.Scatter(x=x_cat, y=y_cat, mode='markers', 
                             marker=dict(color='#0284c7' if catalyst_location=='lumen' else '#10b981', 
                                         size=10, opacity=1.0, line=dict(color='#0c4a6e', width=1)), 
                             name='Closely Packed Catalyst Pellets'))

    fig.update_layout(
        title=f'2D Cross Section ({module_name})',
        xaxis=dict(scaleanchor="y", scaleratio=1, showgrid=False, zeroline=False),
        yaxis=dict(showgrid=False, zeroline=False),
        template='plotly_white',
        plot_bgcolor='white'
    )
    fig.write_image(f"figures/2d_cross_section_{module_name.lower().replace(' ', '_')}.png")

    # 3D Diagram (Cutaway)
    fig3 = go.Figure()

    z_mesh = np.linspace(0, L, 50)
    theta_mesh = np.linspace(0, np.pi, 30) # Only bottom half for cutaway
    Z, Theta = np.meshgrid(z_mesh, theta_mesh)

    R_wall = (dw/2) * 5
    R_mem = (dm/2) * 5

    X_wall = R_wall * np.cos(Theta)
    Y_wall = R_wall * np.sin(Theta)

    X_mem = R_mem * np.cos(Theta)
    Y_mem = R_mem * np.sin(Theta)

    fig3.add_trace(go.Surface(x=Z, y=X_mem, z=Y_mem, colorscale='Greys' if catalyst_location == 'lumen' else 'Blues', opacity=1.0, showscale=False, name="Membrane"))
    fig3.add_trace(go.Surface(x=Z, y=X_wall, z=Y_wall, colorscale='Greys', opacity=0.2, showscale=False, name="Outer Wall"))

    # 3D Catalyst (Ordered Packed Bed)
    z_cat_grid = np.linspace(L*0.05, L*0.95, 45)
    
    if catalyst_location == 'lumen':
        r_grid = np.linspace(0.01, R_mem * 0.85, 5)
    else:
        r_grid = np.linspace(R_mem * 1.15, R_wall * 0.9, 6)
        
    theta_cat_grid = np.linspace(0, np.pi, 20) 
    
    X3, Y3, Z3 = [], [], []
    for z in z_cat_grid:
        for r in r_grid:
            for t in theta_cat_grid:
                if r == 0 and t > 0: continue 
                X3.append(r * np.cos(t))
                Y3.append(r * np.sin(t))
                Z3.append(z)
                
    fig3.add_trace(go.Scatter3d(
        x=Z3, y=X3, z=Y3,
        mode='markers',
        marker=dict(
            color='#0284c7' if catalyst_location=='lumen' else '#10b981',
            size=6,
            opacity=1.0,
            line=dict(color='#0c4a6e', width=2)
        ),
        name="Packed Catalyst Bed"
    ))

    # Flow Arrows
    if catalyst_location == 'lumen':
        # Feed inside lumen
        fig3.add_trace(go.Scatter3d(
            x=[-0.05, 0], y=[0, 0], z=[0, 0],
            mode='lines+text', line=dict(color='cyan', width=8),
            text=[feed_label, ""], textposition="middle left", name="Feed"
        ))
        # Permeate escaping lumen to annulus radially
        fig3.add_trace(go.Scatter3d(
            x=[L/2, L/2], y=[R_mem*1.2, R_wall*1.2], z=[0, 0],
            mode='lines+text', line=dict(color='red', width=5),
            text=["", perm_label], textposition="middle right", name="Permeate"
        ))
        fig3.add_trace(go.Scatter3d(
            x=[L/3, L/3], y=[R_mem*1.2, R_wall*1.2], z=[0, 0],
            mode='lines', line=dict(color='red', width=5), showlegend=False
        ))
        fig3.add_trace(go.Scatter3d(
            x=[2*L/3, 2*L/3], y=[R_mem*1.2, R_wall*1.2], z=[0, 0],
            mode='lines', line=dict(color='red', width=5), showlegend=False
        ))
        # Retentate from lumen and sweep from annulus
        fig3.add_trace(go.Scatter3d(
            x=[L, L+0.05], y=[0, 0], z=[0, 0],
            mode='lines+text', line=dict(color='cyan', width=8),
            text=["", retentate_label], textposition="middle right", name="Retentate"
        ))
    else:
        # Catalyst in annulus (Module A)
        fig3.add_trace(go.Scatter3d(
            x=[-0.05, 0], y=[R_wall*0.7, R_wall*0.7], z=[0, 0],
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
