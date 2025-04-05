import logging

import pandas as pd
import streamlit as st

from src.api import spl
from src.static.icons import grain_icon_url, wood_icon_url, stone_icon_url, iron_icon_url, dec_icon_url, \
    research_icon_url, land_hammer_icon_url, sps_icon_url, land_plot_icon_url, land_region_icon_url, land_tract_icon_url
from src.static.static_values_enum import consume_rates

log = logging.getLogger("Resource cost/earning")

transaction_fee = 0.90  # 10% fee
taxes_fee = 0.90  # 10% fee

# Initialize session state for selections
for key in ['region_uid', 'tract_number', 'plot_number']:
    if key not in st.session_state:
        st.session_state[key] = None


def get_price(metrics_df: pd.DataFrame, token: str, ) -> float:
    return metrics_df[metrics_df['token_symbol'] == token]['dec_price'].values[0]


# Reset logic
def reset_on_change(_key):
    def reset():
        if _key == "region_uid":
            st.session_state.tract_number = None
            st.session_state.plot_number = None
        elif _key == "tract_number":
            st.session_state.plot_number = None

    return reset


def get_resource_cost(resource_pool_metric):
    st.markdown("## Calculate DEC cost/earnings")
    max_cols = 3
    with st.container(border=True):
        choice = st.radio("Select method", options=["By player", "By select", "By plot id list"])

        taxes_fee_txt = "Include taxes(10%) and fees (10%)"
        if choice == "By player":
            df = by_player()
            tax_fee = st.checkbox(taxes_fee_txt)
            cols = st.columns(max_cols)
            for idx, (_, row) in enumerate(df.iterrows()):
                col_idx = idx % max_cols
                with cols[col_idx]:
                    resource = row['token_symbol']
                    base_pp = row['total_base_pp_after_cap']
                    boosted_pp = row['total_harvest_pp']
                    rewards_per_hour = row['rewards_per_hour']
                    add_research_production_cost(base_pp,
                                                 boosted_pp,
                                                 rewards_per_hour,
                                                 resource,
                                                 resource_pool_metric,
                                                 tax_fee)

        elif choice == "By select":
            base_pp, boosted_pp, rewards_per_hour, resource = by_select()
            tax_fee = st.checkbox(taxes_fee_txt)
            cols = st.columns(max_cols)
            with cols[0]:
                add_research_production_cost(base_pp,
                                             boosted_pp,
                                             rewards_per_hour,
                                             resource,
                                             resource_pool_metric,
                                             tax_fee)

        elif choice == "By plot id list":
            base_pp, boosted_pp, rewards_per_hour, resources = by_deed_list()
            tax_fee = st.checkbox(taxes_fee_txt)
            cols = st.columns(max_cols)
            with cols[0]:
                add_research_production_cost(base_pp,
                                             boosted_pp,
                                             rewards_per_hour,
                                             resources,
                                             resource_pool_metric,
                                             tax_fee)


def by_player():
    player = st.text_input("Enter account name")
    if player:
        log.info(f"By select for {player}")
        deeds, worksite_details, staking_details = spl.get_land_region_details_player(player)

        if worksite_details.empty:
            st.warning(f'No worksites found for player {player}')
        else:
            merged_df = pd.merge(
                worksite_details,
                staking_details,
                how='left',
                on=['region_uid', 'deed_uid'],
                suffixes=('', '_staking_xxx_details')
            )
            grouped_df = merged_df.groupby(['token_symbol']).agg(
                {'total_harvest_pp': 'sum', 'total_base_pp_after_cap': 'sum', 'rewards_per_hour': 'sum'}).reset_index()
            return grouped_df
    return pd.DataFrame()


def add_selection_text(text, icon):
    st.markdown(
        f"""
        <span style="font-size:16px;">
            <strong>{text}</strong>
            <img src="{icon}" width="20" style="vertical-align:middle; margin-bottom:6px; margin-left:6px;">
        </span>
        """,
        unsafe_allow_html=True
    )


def by_select():
    player = st.text_input("Enter account name")
    base_pp = 0
    boosted_pp = 0
    rewards_per_hour = 0
    token_symbol = None

    if player:
        log.info(f"By select for {player}")
        deeds, worksite_details, staking_details = spl.get_land_region_details_player(player)

        if deeds.empty:
            st.warning(f'No deeds found for player {player}')
        else:
            columns = st.columns([1, 1, 1])
            regions = deeds.region_uid.unique().tolist()
            with columns[0]:
                add_selection_text("Select your region", land_region_icon_url)
                st.selectbox("",
                             regions,
                             key="region_uid",
                             label_visibility='collapsed',
                             on_change=reset_on_change("region_uid"))

                if st.session_state.region_uid:
                    selected_region = deeds[deeds.region_uid == st.session_state.region_uid]
                    tracts = selected_region.tract_number.unique().tolist()
                    with columns[1]:
                        add_selection_text("Select your tract", land_tract_icon_url)
                        st.selectbox("",
                                     tracts,
                                     label_visibility="collapsed",
                                     key="tract_number",
                                     on_change=reset_on_change("tract_number"))

                        if st.session_state.tract_number:
                            selected_tract = selected_region[
                                selected_region.tract_number == st.session_state.tract_number
                            ]
                            plots = selected_tract.plot_number.unique().tolist()
                            with columns[2]:
                                add_selection_text("Select your plot", land_plot_icon_url)
                                st.selectbox("",
                                             plots,
                                             label_visibility="collapsed",
                                             key="plot_number")

                                if st.session_state.plot_number:
                                    selected_plot = selected_tract[
                                        selected_tract.plot_number == st.session_state.plot_number
                                    ]
                                    details = staking_details[
                                        staking_details.deed_uid == selected_plot.deed_uid.iloc[0]
                                    ]
                                    worksite_details = worksite_details[
                                        worksite_details.deed_uid == selected_plot.deed_uid.iloc[0]
                                    ]
                                    base_pp = details['total_base_pp_after_cap'].iloc[0]
                                    boosted_pp = details['total_harvest_pp'].iloc[0]
                                    if worksite_details.empty:
                                        rewards_per_hour = 0
                                        token_symbol = None
                                    else:
                                        rewards_per_hour = worksite_details['rewards_per_hour'].iloc[0]
                                        worksite = worksite_details[
                                            worksite_details.deed_uid == selected_plot.deed_uid.iloc[0]
                                            ]
                                        token_symbol = worksite.token_symbol.iloc[0]

    return base_pp, boosted_pp, rewards_per_hour, token_symbol


def by_deed_list():
    with st.expander("How to find plot id", expanded=False):
        st.image('https://support.splinterlands.com/hc/article_attachments/21403360782228')
    plot_ids = st.text_input("Enter plot ids space separated")
    df = pd.DataFrame()
    base_pp = 0
    boosted_pp = 0
    rewards_per_hour = 0
    resources = None

    if plot_ids:
        plot_list = plot_ids.split(" ")
        for plot_id in plot_list:
            deed_df = spl.get_land_deeds_uid(plot_id)
            if not deed_df.empty:
                _, worksite_details, staking_details = spl.get_land_region_details_player(deed_df.player.iloc[0])
                if worksite_details.empty:
                    st.warning('No worksites found....')
                else:
                    merged_df = pd.merge(
                        worksite_details,
                        staking_details,
                        how='left',
                        on=['region_uid', 'deed_uid'],
                        suffixes=('', '_staking_xxx_details')
                    )
                    grouped_df = merged_df.groupby(['token_symbol', 'deed_uid']).agg(
                        {'total_harvest_pp': 'sum', 'total_base_pp_after_cap': 'sum',
                         'rewards_per_hour': 'sum'}).reset_index()
                    grouped_df = grouped_df.loc[grouped_df.deed_uid == deed_df.deed_uid.iloc[0]]

                    df = pd.concat([df, grouped_df], ignore_index=True)
            else:
                st.warning(f"No information found for plot id: {plot_id}... break")
                return base_pp, boosted_pp, resources
        base_pp = df.total_base_pp_after_cap.sum()
        boosted_pp = df.total_harvest_pp.sum()
        rewards_per_hour = df.rewards_per_hour.sum()
        resources = df.token_symbol.unique().tolist()
    return base_pp, boosted_pp, rewards_per_hour, resources


def calculate_fees(tax_fee, total_dec_earning):
    if tax_fee:
        total_dec_earning = total_dec_earning * transaction_fee
        extra_txt = "<span style='color:gray'>(incl. fees)</span><br>"
    else:
        extra_txt = "<br>"
    return extra_txt, total_dec_earning


def calculate_taxes(production, tax_fee):
    if tax_fee:
        production = production * taxes_fee
        extra_txt = "<span style='color:gray'>(incl. taxes)</span><br>"
    else:
        extra_txt = "<br>"
    return extra_txt, production


def add_research_production_cost(base_pp,
                                 boosted_pp,
                                 rewards_per_hour,
                                 resource,
                                 metrics_df,
                                 tax_fee):
    consume_list = ['GRAIN']
    # There is always a grain cost
    costs = {
        'GRAIN': base_pp * consume_rates.get('GRAIN'),
    }

    if not resource:
        st.warning("No resource found...")
        return

    if resource == 'TAX':
        st.warning("Resource TAX (Castle/Keep) not implemented")
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

    if resource in ['RESEARCH', 'SPS']:
        costs['STONE'] = base_pp * consume_rates.get('STONE')
        costs['WOOD'] = base_pp * consume_rates.get('WOOD')
        costs['IRON'] = base_pp * consume_rates.get('IRON')
        consume_list.append('WOOD')
        consume_list.append('STONE')
        consume_list.append('IRON')

    # DEC equivalents
    dec_costs = {
        res: costs[res] / get_price(metrics_df, res)
        for res in costs
    }

    # Total DEC
    total_dec_cost = sum(dec_costs.values())

    # Icons (adjust paths as needed)
    icons = {
        'PP': land_hammer_icon_url,
        'DEC': dec_icon_url,
        'GRAIN': grain_icon_url,
        'STONE': stone_icon_url,
        'WOOD': wood_icon_url,
        'IRON': iron_icon_url,
        'RESEARCH': research_icon_url,
        'SPS': sps_icon_url
    }

    def icon_html(icon_url):
        return f"<img src='{icon_url}' width='20' height='20' style='vertical-align:middle;'/>"

    total_dec_earning = 0
    earning_txt = ""

    if resource not in ['RESEARCH', 'SPS']:
        total_dec_earning = rewards_per_hour / get_price(metrics_df, resource)
        extra_txt, total_dec_earning = calculate_fees(tax_fee, total_dec_earning)

        earning_txt = (f"<h8>{icon_html(icons['DEC'])} DEC Earning/ hr: {round(total_dec_earning, 3)} "
                       f"{extra_txt}</h8>")

    production_txt = ""
    if rewards_per_hour:
        extra_txt, production = calculate_taxes(rewards_per_hour, tax_fee)
        production_txt = (f"<h8>{icon_html(icons[resource])} {resource} Production / hr RR: {round(production, 3)} "
                          f"{extra_txt}</h8>")

    # Markdown output
    with st.container(border=True):
        st.markdown(f"""
        <img src='{icons[resource]}' width='50' height='50' style='display: block; margin-left: auto; margin-right: auto;'/>
        <br>
        
        <h7>{icon_html(icons['PP'])} BASE PP: {base_pp}</h7>
        
        <h7>{icon_html(icons['PP'])} BOOSTED PP: {boosted_pp}</h7>

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
        {production_txt}
        {earning_txt}
        <h8>{icon_html(icons['DEC'])}Net Positive DEC / hr: {round(total_dec_earning - total_dec_cost, 3)}
        <span style='color:gray'>(earn-cost)</span><br></h8>
        """, unsafe_allow_html=True)
