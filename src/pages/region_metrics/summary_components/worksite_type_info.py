import streamlit as st

from src.static.static_values_enum import worksite_type_mapping


def print_worksite_types(df):
    worksite_types = df['worksite_type'].value_counts().reset_index()
    worksite_types.columns = ['worksite_type', 'count']

    ordered_keys = list(worksite_type_mapping.keys())
    worksite_types = worksite_types[worksite_types['worksite_type'].isin(ordered_keys)].copy()

    worksite_types['sort_order'] = worksite_types['worksite_type'].apply(lambda x: ordered_keys.index(x))
    worksite_types = worksite_types.sort_values('sort_order')

    st.markdown("### Worksite Type Overview")

    total_html = """
        <style>
        .worksite-grid {
            display: flex;
            flex-wrap: wrap;
            gap: 1rem;
        }
        .worksite-item {
            border: 1px solid #ccc;
            border-radius: 8px;
            padding: 10px;
            text-align: center;
            min-width: 100px;
            max-width: 120px;
            flex-grow: 1;
            box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
        }
        </style>
        <div class="worksite-grid">
    """

    html_blocks = ""
    for _, row in worksite_types.iterrows():
        worksite_type = row['worksite_type']
        if worksite_type == '':
            worksite_type = 'Undeveloped'
        count = row['count']

        if worksite_type == 'KEEP' or worksite_type == "CASTLE":
            extra_style = 'style="width: 60px; max-height: 40px"'
        else:
            extra_style = 'style="max-width: 60px; max-height: 100px;"'
        image_url = worksite_type_mapping.get(worksite_type)
        html_blocks += f"""
        <div class="worksite-item">
            <img src="{image_url}" alt="{worksite_type}" {extra_style}>
            <div><strong>{worksite_type.replace('_', ' ').title()}</strong></div>
            <div>Count: {count}</div>
        </div>
        """

    total_html += html_blocks
    total_html += "</div>"

    st.markdown(total_html, unsafe_allow_html=True)
