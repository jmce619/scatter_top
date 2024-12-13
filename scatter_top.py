import streamlit as st
import pandas as pd
import geopandas as gpd
import plotly.graph_objs as go

# Load the data from a pickle file
map_df = pd.read_pickle('map_df.pkl')
map_gdf = gpd.GeoDataFrame(map_df, geometry='geometry')

def plot_3d_scatter():
    # The rest of your plotting code from before...
    map_gdf['centroid'] = map_gdf['geometry'].centroid
    map_gdf['height'] = map_gdf['winner_votes'] / 1000

    def color_with_intensity(row):
        base_colors = {
            'Democrat': (0, 0, 255),
            'Republican': (255, 0, 0),
            'Green': (0, 255, 0),
            None: (128, 128, 128)
        }
        r, g, b = base_colors.get(row['winner_party'], (128, 128, 128))
        intensity = row['winner_percentage'] / 100
        intensity = max(0.3, min(intensity, 1.0))

        r = int(r * intensity + (1 - intensity) * 255)
        g = int(g * intensity + (1 - intensity) * 255)
        b = int(b * intensity + (1 - intensity) * 255)

        opacity = intensity
        return f"rgba({r}, {g}, {b}, {opacity})"

    map_gdf['dynamic_color'] = map_gdf.apply(color_with_intensity, axis=1)

    x = map_gdf['centroid'].x
    y = map_gdf['centroid'].y
    z = map_gdf['height']

    fig = go.Figure()

    fig.add_trace(go.Scatter3d(
        x=x,
        y=y,
        z=z,
        mode='markers',
        marker=dict(size=8, color=map_gdf['dynamic_color']),
        text=map_gdf.apply(lambda row: f"State: {row['state_name']}<br>District: {row['district']}<br>Party: {row['winner_party']}<br>Votes: {row['winner_votes']}<br>Percentage: {row['winner_percentage']}%", axis=1),
        hovertemplate="%{text}<br>Height: %{z}<extra></extra>"
    ))

    for _, row in map_gdf.iterrows():
        x_coords, y_coords = map(list, row['geometry'].exterior.xy)
        z_coords = [0] * len(x_coords)
        fig.add_trace(go.Scatter3d(
            x=x_coords,
            y=y_coords,
            z=z_coords,
            mode='lines',
            line=dict(color='black', width=1),
            hoverinfo='skip'
        ))

    fig.update_layout(
        scene=dict(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            zaxis=dict(visible=False),
            aspectratio=dict(x=2, y=1, z=0.5)
        ),
        margin=dict(l=0, r=0, b=0, t=0),
        paper_bgcolor='white',
        showlegend=False
    )

    return fig

st.title("3D Geospatial Visualization")
fig = plot_3d_scatter()
st.plotly_chart(fig, use_container_width=True)
