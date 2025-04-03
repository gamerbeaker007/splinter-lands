import pandas as pd
import streamlit as st

from src.static.icons import SPL_WEB_URL

rarity_order = ['natural', 'magical', 'occupied', 'kingdom']


def print_plot_status(df):
    grouped = df.groupby('plot_status').size().reset_index(name='count')
    grouped['plot_status_cat'] = pd.Categorical(grouped['plot_status'], categories=rarity_order, ordered=True)
    grouped = grouped.sort_values('plot_status_cat')

    st.markdown("### Plot status Overview")

    # Start flex container
    total_html = """
        <style>
        .plot-status-grid {
            display: flex;
            flex-wrap: wrap;
            gap: 1rem;
        }
        .plot-status-item {
            border: 1px solid #ccc;
            border-radius: 8px;
            padding: 10px;
            text-align: center;
            min-width: 120px;
            max-width: 120px;
            min-height: 150px;
            flex-grow: 1;
            box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
        }
        .plot-status-item img {
            max-width: 80px;
            height: auto;
        }
        </style>
        <div class="plot-status-grid">
        """

    html_blocks = ""
    for _, row in grouped.iterrows():
        plot_status = row['plot_status']
        count = row['count']

        if plot_status == 'Unknown':
            image_html = '<div style="font-size: 24px;">❓</div>'
        else:
            image_url = f"{SPL_WEB_URL}assets/lands/sideMenu/{plot_status.lower()}Off.svg"
            image_html = f'<img src="{image_url}" alt="{plot_status}">'

        html_blocks += f"""
        <div class="plot-status-item">
            {image_html}
            <div><strong>{plot_status.title()}</strong></div>
            <div>Count: {count}</div>
        </div>
        """

    total_html += html_blocks
    total_html += '</div>'
    # Close container and render
    st.markdown(total_html, unsafe_allow_html=True)
