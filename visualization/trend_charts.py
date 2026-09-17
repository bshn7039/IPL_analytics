"""
Trend Visualizations Module
Renders win/loss donuts, match run trajectories, and multi-season performance lines.
"""
import plotly.express as px
import plotly.graph_objects as go

def plot_win_loss_donut(wins, losses):
    """Renders sleek donut chart of team win-loss record."""
    total = wins + losses
    if total == 0:
        return go.Figure()

    labels = ["Wins", "Losses"]
    values = [wins, losses]
    colors = ["#10B981", "#EF4444"]

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.55,
        marker=dict(colors=colors),
        textinfo="percent+label",
        hoverinfo="label+value+percent"
    )])
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#11151F",
        plot_bgcolor="#11151F",
        showlegend=False,
        margin=dict(l=20, r=20, t=30, b=20),
        annotations=[dict(text=f"{round(wins/total*100, 1)}%<br>Win Rate", x=0.5, y=0.5, font_size=14, font_color="white", showarrow=False)]
    )
    return fig

def plot_match_run_trend(match_df, team):
    """Line chart tracking team run scores across matches with victory annotations."""
    if match_df.empty:
        return go.Figure()

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=match_df["match_num"],
        y=match_df["team_score"],
        mode="lines+markers",
        name="Runs Scored",
        line=dict(color="#38BDF8", width=3),
        marker=dict(
            size=10,
            color=["#10B981" if r == "Won" else "#EF4444" for r in match_df["result"]]
        ),
        text=[f"Match {m}: {score} vs {opp} ({res})" for m, score, opp, res in zip(match_df["match_num"], match_df["team_score"], match_df["opponent"], match_df["result"])],
        hoverinfo="text"
    ))

    # Average baseline reference
    avg_score = match_df["team_score"].mean()
    fig.add_hline(y=avg_score, line_dash="dash", line_color="#F59E0B", annotation_text=f"Season Avg ({round(avg_score, 1)})")

    fig.update_layout(
        title=f"{team} Match-by-Match Run Progression",
        xaxis_title="Match Sequence",
        yaxis_title="Innings Runs",
        template="plotly_dark",
        plot_bgcolor="#11151F",
        paper_bgcolor="#11151F",
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig
