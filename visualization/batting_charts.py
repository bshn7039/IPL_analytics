"""
Batting Visualizations Module
Renders interactive Plotly charts and static Matplotlib figures for batting statistics.
"""
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt

def plot_runs_by_player(top_batsmen_df):
    """Horizontal bar chart showing top run scorers."""
    if top_batsmen_df.empty:
        return go.Figure()
    
    df_sorted = top_batsmen_df.sort_values(by="runs", ascending=True)
    fig = px.bar(
        df_sorted,
        x="runs",
        y="player",
        orientation="h",
        text="runs",
        color="runs",
        color_continuous_scale="Blues",
        title="Top Run Scorers"
    )
    fig.update_layout(
        template="plotly_dark",
        plot_bgcolor="#11151F",
        paper_bgcolor="#11151F",
        xaxis_title="Total Runs",
        yaxis_title="Player",
        margin=dict(l=20, r=20, t=50, b=20)
    )
    fig.update_traces(textposition="outside")
    return fig

def plot_runs_vs_strike_rate(batting_df):
    """Scatter plot: Runs vs Strike Rate identifying high-volume aggressive batsmen."""
    if batting_df.empty:
        return go.Figure()
    
    fig = px.scatter(
        batting_df,
        x="runs",
        y="strike_rate",
        size="innings" if "innings" in batting_df.columns else None,
        hover_name="player",
        color="strike_rate",
        color_continuous_scale="Viridis",
        title="Runs vs Strike Rate Matrix",
        labels={"runs": "Total Runs", "strike_rate": "Strike Rate (%)"}
    )
    fig.update_layout(
        template="plotly_dark",
        plot_bgcolor="#11151F",
        paper_bgcolor="#11151F",
        margin=dict(l=20, r=20, t=50, b=20)
    )
    return fig

def plot_boundary_distribution_mpl(fours, sixes, total_runs):
    """Matplotlib pie chart illustrating boundary vs running distribution."""
    fig, ax = plt.subplots(figsize=(6, 4), facecolor="#11151F")
    ax.set_facecolor("#11151F")

    four_runs = fours * 4
    six_runs = sixes * 6
    running_runs = max(0, total_runs - (four_runs + six_runs))

    labels = [f"Fours ({fours})", f"Sixes ({sixes})", "Singles / 2s / 3s"]
    values = [four_runs, six_runs, running_runs]
    colors = ["#3B82F6", "#F97316", "#10B981"]

    if sum(values) == 0:
        values = [1, 1, 1]

    wedges, texts, autotexts = ax.pie(
        values, labels=labels, autopct="%1.1f%%",
        startangle=140, colors=colors, textprops=dict(color="white")
    )
    for at in autotexts:
        at.set_color("white")
        at.set_fontsize(10)
    ax.set_title("Boundary Run Share", color="white", fontsize=12, pad=15)
    plt.tight_layout()
    return fig
