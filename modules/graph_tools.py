import plotly.graph_objects as go

# Heatmap function to convert the data into a heat map
def heatmap(values, x, y, x_label="", y_label="", title=""):
    """Create a heatmap chart."""
    # values should be a 2D array-like (list of lists or 2D numpy array)
    fig = go.Figure(data=go.Heatmap(
        z=values,
        x=x,
        y=y,
        transpose=True,
        colorscale='Hot',
        colorbar=dict(title=title)
    ))
    fig.update_layout(
        title=title,
        xaxis_title=x_label,
        yaxis_title=y_label,
        yaxis_autorange='reversed'
    )
    return fig