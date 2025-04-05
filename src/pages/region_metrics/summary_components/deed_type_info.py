import streamlit as st

from src.static.icons import SPL_WEB_URL


def print_deed_types(df):
    grouped = df.groupby('deed_type').size().reset_index(name='count')
    grouped = grouped.sort_values(by='deed_type', ascending=True)

    st.markdown("### Deed Type Overview")

    # Start flex container
    total_html = """
        <style>
        .deed-grid {
            display: flex;
            flex-wrap: wrap;
            gap: 1rem;
        }
        .deed-item {
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
        .deed-item img {
            max-width: 80px;
            height: auto;
        }
        </style>
        <div class="deed-grid">
        """

    html_blocks = ""
    for _, row in grouped.iterrows():
        deed_type = row['deed_type']
        count = row['count']

        path = "assets/lands/deedAssets/"
        extra_style = """style="width: 50px; min-height: 50px" """

        if deed_type == 'Unsurveyed Deed':
            image_html = '<div style="font-size: 30px;">❓</div>'
        else:
            image_url = f"{SPL_WEB_URL}{path}img_geography-emblem_{deed_type.lower()}.svg"
            image_html = f'<img src="{image_url}" alt="{deed_type}" {extra_style}>'

        html_blocks += f"""
        <div class="deed-item">
            {image_html}
            <div><strong>{deed_type}</strong></div>
            <div>Count: {count}</div>
        </div>
        """

    total_html += html_blocks
    total_html += '</div>'
    # Close container and render
    st.markdown(total_html, unsafe_allow_html=True)
