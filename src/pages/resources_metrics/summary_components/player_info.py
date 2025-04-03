import streamlit as st


def print_player_info(df):
    unique_players = df.player.unique().size
    top_ten_holders = df['player'].value_counts().head(10)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Top 10 Holders")
        html = "<div style='line-height:1.6;'>"
        for i, (player, count) in enumerate(top_ten_holders.items(), start=1):
            html += f"<strong>{i}.</strong> {player} <span style='color:gray'>({count})</span><br>"
        html += "</div>"

        st.markdown(html, unsafe_allow_html=True)
    with col2:
        st.markdown("### Unique owners")
        st.markdown(f"{unique_players}")
