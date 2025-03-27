import streamlit as st

from src.static.icons import grain_icon_url, wood_icon_url, stone_icon_url, iron_icon_url, dec_icon_url, sps_icon_url

transaction_fee = 0.90  # 10% fee

default_width = 150
sing_style = """
    display: flex;
    justify-content: center;
    align-items: center;
    height: 220px;
    font-size: 32px;
    font-weight: bold;
"""

def resource_input(resource: str, icon_url: str):
        st.image(icon_url, width=default_width)
        return st.number_input(f"{resource}", min_value=0.0, step=1.0, key=f"input_{resource.lower()}")

# Helper to show image and output label
def resource_output(resource: str, icon_url: str, value: str):
    st.image(icon_url, width=default_width/2)
    st.markdown(f"**{resource}: {value}**")

def get_container(metrics_df, prices_df):
    # Inputs
    cols = st.columns([1, 0.3, 1, 0.3, 1, 0.3, 1, 0.3, 1.5])
    with cols[0]:
        grain = resource_input("GRAIN", grain_icon_url)
    with cols[1]:
        st.markdown(f'<p style="{sing_style}">+</div>', unsafe_allow_html=True)
    with cols[2]:
        wood = resource_input("WOOD", wood_icon_url)
    with cols[3]:
        st.markdown(f'<div style="{sing_style}">+</div>', unsafe_allow_html=True)
    with cols[4]:
        stone = resource_input("STONE", stone_icon_url)
    with cols[5]:
        st.markdown(f'<div style="{sing_style}">+</div>', unsafe_allow_html=True)
    with cols[6]:
        iron = resource_input("IRON", iron_icon_url)
    with cols[7]:
        st.markdown(f'<div style="{sing_style}">=</div>', unsafe_allow_html=True)
    with cols[8]:
        # Perform conversion
        if not metrics_df.empty and not prices_df.empty:
            # Safe defaults if None
            grain = grain or 0
            wood = wood or 0
            stone = stone or 0
            iron = iron or 0

            def get_price(token: str) -> float:
                return metrics_df[metrics_df['token_symbol'] == token]['dec_price'].values[0]

            dec_total = (
                    (grain / get_price('GRAIN')) * transaction_fee +
                    (wood / get_price('WOOD')) * transaction_fee +
                    (stone / get_price('STONE')) * transaction_fee +
                    (iron / get_price('IRON')) * transaction_fee
            )

            usd_value = dec_total * prices_df['dec'].values[0]
            sps_amount = usd_value / prices_df['sps'].values[0]
        else:
            st.warning("Market data not available.")

        resource_output("DEC", dec_icon_url, f"{dec_total:.2f}")
        resource_output("SPS", sps_icon_url, f"{sps_amount:.2f}")
