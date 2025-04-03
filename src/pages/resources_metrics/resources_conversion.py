import logging

import pandas as pd
import streamlit as st

from src.api import spl
from src.static.icons import grain_icon_url, wood_icon_url, stone_icon_url, iron_icon_url, dec_icon_url, sps_icon_url, \
    research_icon_url, land_hammer_icon_url
from src.static.static_values_enum import production_rates, consume_rates, resource_list

log = logging.getLogger("Resource conversion")

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
    st.markdown(f'''
        <div style="text-align: center;">
            <img src="{icon_url}" width="{default_width}" tabindex="-1">
        </div>
    ''', unsafe_allow_html=True)
    return st.number_input(
        f'{resource}',
        min_value=0.0,
        step=1.0,
        key=f"input_{resource.lower()}",
        label_visibility='hidden'
    )


# Helper to show image and output label
def resource_output(resource: str, icon_url: str, value: str):
    st.markdown(f'''
        <div style="text-align: left;">
            <img src="{icon_url}" width="{default_width/2}" tabindex="-1">
        </div>
    ''', unsafe_allow_html=True)

    st.markdown(f"**{resource}: {value}**")


def get_price(metrics_df: pd.DataFrame, token: str,) -> float:
    return metrics_df[metrics_df['token_symbol'] == token]['dec_price'].values[0]


def get_container(metrics_df, prices_df):
    with st.container(border=True):
        cols = st.columns([1, 0.3, 1, 0.3, 1, 0.3, 1, 0.3, 1.5])
        with cols[0]:
            grain = resource_input("GRAIN", grain_icon_url)
        with cols[1]:
            st.markdown(f'<div style="{sing_style}" tabindex="-1">+</div>', unsafe_allow_html=True)
        with cols[2]:
            wood = resource_input("WOOD", wood_icon_url)
        with cols[3]:
            st.markdown(f'<div style="{sing_style}" tabindex="-1">+</div>', unsafe_allow_html=True)
        with cols[4]:
            stone = resource_input("STONE", stone_icon_url)
        with cols[5]:
            st.markdown(f'<div style="{sing_style}" tabindex="-1">+</div>', unsafe_allow_html=True)
        with cols[6]:
            iron = resource_input("IRON", iron_icon_url)
        with cols[7]:
            st.markdown(f'<div style="{sing_style}" tabindex="-1">=</div>', unsafe_allow_html=True)
        with cols[8]:
            # Perform conversion
            if not metrics_df.empty and not prices_df.empty:
                # Safe defaults if None
                grain = grain or 0
                wood = wood or 0
                stone = stone or 0
                iron = iron or 0

                dec_total = (
                        (grain / get_price(metrics_df, 'GRAIN')) * transaction_fee +
                        (wood / get_price(metrics_df, 'WOOD')) * transaction_fee +
                        (stone / get_price(metrics_df, 'STONE')) * transaction_fee +
                        (iron / get_price(metrics_df, 'IRON')) * transaction_fee
                )

                usd_value = dec_total * prices_df['dec'].values[0]
                sps_amount = usd_value / prices_df['sps'].values[0]
            else:
                st.warning("Market data not available.")

            resource_output("DEC", dec_icon_url, f"{dec_total:.2f}")
            resource_output("SPS", sps_icon_url, f"{sps_amount:.2f}")


# Initialize session state for selections
for key in ['region_uid', 'tract_number', 'plot_number']:
    if key not in st.session_state:
        st.session_state[key] = None


# Reset logic
def reset_on_change(key):
    def reset():
        if key == "region_uid":
            st.session_state.tract_number = None
            st.session_state.plot_number = None
        elif key == "tract_number":
            st.session_state.plot_number = None
    return reset


def by_select():
    player = st.text_input("Enter account name")
    base_pp = 0
    boosted_pp = 0
    token_symbol = None

    if player:
        log.info(f"By select for {player}")
        deeds, worksite_details, staking_details = spl.get_land_region_details_player(player)

        if deeds.empty:
            st.warning(f'No deeds found for player {player}')
        else:
            regions = deeds.region_uid.unique().tolist()
            st.selectbox("Select your region", regions,
                         key="region_uid", on_change=reset_on_change("region_uid"))

            if st.session_state.region_uid:
                selected_region = deeds[deeds.region_uid == st.session_state.region_uid]
                tracts = selected_region.tract_number.unique().tolist()
                st.selectbox("Select your tract", tracts,
                             key="tract_number", on_change=reset_on_change("tract_number"))

                if st.session_state.tract_number:
                    selected_tract = selected_region[selected_region.tract_number == st.session_state.tract_number]
                    plots = selected_tract.plot_number.unique().tolist()
                    st.selectbox("Select your plot", plots, key="plot_number")

                    if st.session_state.plot_number:
                        selected_plot = selected_tract[selected_tract.plot_number == st.session_state.plot_number]
                        details = staking_details[staking_details.deed_uid == selected_plot.deed_uid.iloc[0]]
                        base_pp = details['total_base_pp_after_cap'].iloc[0]
                        boosted_pp = details['total_harvest_pp'].iloc[0]
                        worksite = worksite_details[worksite_details.deed_uid == selected_plot.deed_uid.iloc[0]]
                        token_symbol = worksite.token_symbol.iloc[0]

    return base_pp, boosted_pp, token_symbol


def get_container_2(resource_pool_metric):
    st.markdown("## Calculate research cost")
    with st.container(border=True):
        choice = st.radio("Select method", options=["By PP", "By select", "By plot id list"])

        if choice == "By PP":
            base_pp, boosted_pp, resource = by_pp()
            add_research_production_cost(base_pp, boosted_pp, resource_pool_metric, resource)
        elif choice == "By select":
            base_pp, boosted_pp, resource = by_select()
            add_research_production_cost(base_pp, boosted_pp, resource_pool_metric, resource)
        elif choice == "By plot id list":
            base_pp, boosted_pp, resources = by_deed_list()
            add_research_production_cost(base_pp, boosted_pp, resource_pool_metric, resources)


def by_deed_list():
    with st.expander("How to find deed id", expanded=False):
        st.image('https://support.splinterlands.com/hc/article_attachments/21403360782228')
    deed_ids = st.text_input("Enter plot ids space separated")
    df = pd.DataFrame()
    base_pp = 0
    boosted_pp = 0
    resources = None

    if deed_ids:
        deed_list = deed_ids.split(" ")
        for plot_id in deed_list:
            deed_df = spl.get_land_deeds_uid(plot_id)
            if not deed_df.empty:
                detailed_df = spl.get_land_stake_deed_details(deed_df['deed_uid'].iloc[0])
                merged_df = pd.merge(
                    deed_df,
                    detailed_df,
                    how='left',
                    on=['region_uid', 'deed_uid'],
                    suffixes=('', '_xxx_details')
                )

                df = pd.concat([df, merged_df], ignore_index=True)
            else:
                st.warning(f"No information found for plot id: {plot_id}... break")
                return base_pp, boosted_pp, resources
        base_pp = df.total_base_pp_after_cap.sum()
        boosted_pp = df.total_harvest_pp.sum()
        resources = df.resource_symbol.unique().tolist()
    return base_pp, boosted_pp, resources


def by_pp():
    col1, col2 = st.columns(2)
    with col1:
        base_pp = st.number_input("Base PP", value=0)
    with col2:
        boosted_pp = st.number_input("Boosted PP", value=0)
    resource = st.selectbox("Select resource",  resource_list)
    return base_pp, boosted_pp, resource


def add_research_production_cost(base_pp, boosted_pp, metrics_df, resource):
    consume_list = ['GRAIN']
    # There is always a grain cost
    costs = {
        'GRAIN': base_pp * consume_rates.get('GRAIN'),
    }

    if not resource:
        st.warning("No resource found...")
        return

    if isinstance(resource, list):
        if len(resource) > 1:
            st.warning("Selected plots have different resources that it produces. Unable to continue...")
            return
        elif not resource[0]:
            st.warning("No producing resource found...")
            return
        else:
            resource = resource[0]


    if resource == 'RESEARCH':
        costs['STONE'] =  base_pp * consume_rates.get('WOOD')
        costs['WOOD'] = base_pp * consume_rates.get('WOOD')
        costs['IRON'] =  base_pp * consume_rates.get('IRON')
        consume_list.append('WOOD')
        consume_list.append('STONE')
        consume_list.append('IRON')
        production = boosted_pp * production_rates.get('RESEARCH')
    else:
        production = boosted_pp * production_rates.get(resource)


    # DEC equivalents
    dec_costs = {
        res: costs[res] / get_price(metrics_df, res)
        for res in costs
    }

    # Total DEC
    total_dec_cost = sum(dec_costs.values())


    # Production output

    # Icons (adjust paths as needed)
    icons = {
        'PP': land_hammer_icon_url,
        'DEC': dec_icon_url,
        'GRAIN': grain_icon_url,
        'STONE': stone_icon_url,
        'WOOD': wood_icon_url,
        'IRON': iron_icon_url,
        'RESEARCH': research_icon_url
    }

    def icon_html(icon_url):
        return f"<img src='{icon_url}' width='40' height='40' style='vertical-align:middle;'/>"


    if resource != "SPS" and  resource != 'RESEARCH':
        total_dec_earning = production / get_price(metrics_df, resource)
        earning_txt = f"""
        <h4>{icon_html(icons['DEC'])} {resource} DEC earning/ hr: {round(total_dec_earning*transaction_fee, 3)}*</h4>
        <span style='color:gray'>* Including transaction fees</span><br>
        """
    else:
        earning_txt = ""

    # Markdown output
    st.markdown(f"""
        <h3>{icon_html(icons['PP'])} BASE PP: {base_pp}</h3>
        <h3>{icon_html(icons['PP'])} BOOSTED PP: {boosted_pp}</h3>

        <table>
            <tr>
                <th>Resource</th>
                <th>Cost / hr</th>
                <th>DEC / hr</th>
            </tr>
            {''.join([
                f"<tr>"
                f"<td>{icon_html(icons[res])} {res}</td>"
                f"<td>{round(costs[res], 3)}</td>"
                f"<td>{round(dec_costs[res], 3)}</td>"
                f"</tr>"
                for res in consume_list
            ])}
        </table>

        <h4>{icon_html(icons[resource])} {resource} Production / hr: {round(production, 3)}</h4>
        {earning_txt}
        <h4>{icon_html(icons['DEC'])} Total DEC cost / hr: {round(total_dec_cost, 3)}</h4>
    """, unsafe_allow_html=True)
