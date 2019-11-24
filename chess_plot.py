# use plotly to visualize the chess game in a line graph
import plotly
import plotly.graph_objs as go


def plot_graph(act_game, filename, counts):
    # plotly.tools.set_credentials_file(username='s1710629025', api_key='••••••••••')
    plotly.offline.init_notebook_mode(connected=True)

    check_color = ['red' if i else 'white' for i in counts["is_check"]]
    check_no = [i for (i, s) in enumerate(counts["is_check"]) if s]
    bubble = [s / 2 for s in counts["move_count"]]
    # best = [np.log(s+1) for s in counts["bestdiff"]]
    # best = [s for s in counts["bestdiff"]]
    best = counts["best_move_score_diff_category"]

    rook_color = ['blue' if i else 'white' for i in counts["rook_ending"]]
    pawn_color = ['green' if i else 'white' for i in counts["pawn_ending"]]
    capture_color = ['yellow' if i else 'white' for i in counts["is_capture"]]
    capture_no = [i for (i, s) in enumerate(counts["is_capture"]) if s]

    shapes = []
    lists = [check_color, capture_color, rook_color, pawn_color]
    for (i, list) in enumerate(lists):
        shapes = shapes + [
            dict(
                type='rect',
                # x-reference is assigned to the x-values
                xref='x',
                # y-reference is assigned to the plot paper [0,1]
                yref='paper',
                x0=i,
                y0=0,
                x1=i + 1,
                y1=1,
                fillcolor=s,
                opacity=0.2,
                line=dict(
                    width=0,
                )
            )
            for (i, s) in enumerate(list)]

    annotations = [dict(
        xref='x',
        yref='paper',
        x=s,
        y=(0.05 + i * 0.2) % 1,
        text='Check!',
        opacity=0.8,
        xanchor='left',
        showarrow=False,
        ax=20,
        ay=-30,
        font=dict(
            family='Courier New, monospace',
            size=16,
            color='red'
        ),
    )
        for (i, s) in enumerate(check_no)]

    trace1 = go.Scatter(
        mode='markers+lines',
        y=counts["score"],
        # y = score_history,
        name='Scores',

        line=dict(
            color=('black'),
            width=4,
        ),
        marker=dict(
            size=bubble,
            line=dict(color='rgb(231, 99, 250)', width=1),
            cmax=max(best),
            cmin=min(best),
            color=best,
            colorbar=dict(title='Mistakes'),
            colorscale='Jet'
        )
    )

    trace2 = go.Scatter(
        mode='markers+lines',
        y=counts["attack_defense_relation1"],
        # y = score_history,
        name='Attack/Defense',

        line=dict(
            color=('red'),
            width=4,
        )
    )

    data = [trace1, trace2]

    layout = dict(title=act_game.headers["Event"] + " / " + act_game.headers["White"] + " - "
                        + act_game.headers["Black"] + "  " + act_game.headers["Result"] + " / "
                        + act_game.headers["Date"],
                  xaxis=dict(title='Move'),
                  yaxis=dict(title='Score'),
                  shapes=shapes,
                  annotations=annotations
                  )

    fig = {
        'data': data,
        'layout': layout,
    }

    # plot chart in notebook as well as write it to html file
    plotly.offline.iplot(fig)
    plotly.offline.plot(fig, filename='output/' + filename + '/' + filename + '.html')