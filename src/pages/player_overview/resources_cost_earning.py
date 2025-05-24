import streamlit as st

from src.static.static_values_enum import consume_rates, resource_icon_map, MULTIPLE_CONSUMING_RESOURCE
from src.utils.log_util import configure_logger
from src.utils.resource_util import reorder_column, get_price

log = configure_logger(__name__)

conversion_fee = 0.90  # 10% conversion fee
tax_fee = 0.90  # 10% fee

# Initialize session state for selections
for key in ['region_uid', 'tract_number', 'plot_number']:
    if key not in st.session_state:
        st.session_state[key] = None


# Reset logic
def reset_on_change(_key):
    def reset():
        if _key == "region_uid":
            st.session_state.tract_number = None
            st.session_state.plot_number = None
        elif _key == "tract_number":
            st.session_state.plot_number = None

    return reset


def get_resource_cost(df, resource_pool_metric, prices_df):
    max_cols = 3
    total_net_dec = 0

    st.markdown("## Calculate DEC cost/earnings")

    df = df.groupby(['token_symbol']).agg(
        {
            'total_harvest_pp': 'sum',
            'total_base_pp_after_cap': 'sum',
            'rewards_per_hour': 'sum'
        }).reset_index()

    if 'taxes_fee' not in st.session_state:
        st.session_state.taxes_fee = True
    st.session_state.taxes_fee = st.checkbox(
        "Include taxes(10%)",
        value=st.session_state.taxes_fee,
        help="10% Taxes are deducted from the produced amount"
    )

    if 'conversion_fee' not in st.session_state:
        st.session_state.conversion_fee = True
    st.session_state.conversion_fee = st.checkbox(
        "Conversion fees (10%)",
        value=st.session_state.conversion_fee,
        help="10% conversion fees are applied when converting the produced resource to DEC (Trade Hub fee)"
    )

    placeholder = st.empty()

    cols = st.columns(max_cols)
    df = reorder_column(df)
    for idx, (_, row) in enumerate(df.iterrows()):
        col_idx = idx % max_cols
        with cols[col_idx]:
            resource = row['token_symbol']
            base_pp = row['total_base_pp_after_cap']
            boosted_pp = row['total_harvest_pp']
            rewards_per_hour = row['rewards_per_hour']
            net_dec = add_research_production_cost(base_pp,
                                                   boosted_pp,
                                                   rewards_per_hour,
                                                   resource,
                                                   resource_pool_metric,
                                                   prices_df,
                                                   st.session_state.taxes_fee,
                                                   st.session_state.conversion_fee)
            if net_dec:
                total_net_dec += net_dec

    placeholder.markdown(f"""
    <div style='font-size: 1.5em; font-weight: bold; margin-bottom: 5px;'>
        {icon_html(resource_icon_map['DEC'], width=75, height=75)}
        Total Net Positive DEC: {round(total_net_dec, 3)} /hr</div>
    """, unsafe_allow_html=True)


def calculate_conversion_fees(include_conversion_fee, total_dec_earning):
    if include_conversion_fee:
        total_dec_earning = total_dec_earning * conversion_fee
        extra_txt = "<span style='color:gray'>(incl. fees)</span><br>"
    else:
        extra_txt = "<br>"
    return extra_txt, total_dec_earning


def calculate_tax_fee(production, include_tax_fee):
    if include_tax_fee:
        production = production * tax_fee
        extra_txt = "<span style='color:gray'>(incl. taxes)</span><br>"
    else:
        extra_txt = "<br>"
    return extra_txt, production


def icon_html(icon_url, width=20, height=20):
    return f"<img src='{icon_url}' width='{width}' height='{height}' style='vertical-align:middle;'/>"


def add_research_production_cost(base_pp,
                                 boosted_pp,
                                 rewards_per_hour,
                                 resource,
                                 metrics_df,
                                 priced_df,
                                 include_tax_fee,
                                 include_conversion_fee):
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

    if resource in MULTIPLE_CONSUMING_RESOURCE:
        costs['STONE'] = base_pp * consume_rates.get('STONE')
        costs['WOOD'] = base_pp * consume_rates.get('WOOD')
        costs['IRON'] = base_pp * consume_rates.get('IRON')
        consume_list.append('WOOD')
        consume_list.append('STONE')
        consume_list.append('IRON')

    # DEC equivalents
    dec_costs = {
        res: get_price(metrics_df, priced_df, res, costs[res])
        for res in costs
    }

    # Total DEC
    total_dec_cost = sum(dec_costs.values())
    total_dec_earning = get_price(metrics_df, priced_df, resource, rewards_per_hour)
    extra_txt, total_dec_earning = calculate_conversion_fees(include_conversion_fee, total_dec_earning)

    earning_txt = (f"<h8>{icon_html(resource_icon_map['DEC'])} DEC Earning: {round(total_dec_earning, 3)} /hr"
                   f"{extra_txt}</h8>")

    production_txt = ""
    if rewards_per_hour:
        extra_txt, production = calculate_tax_fee(rewards_per_hour, include_tax_fee)
        production_txt = (f"<h8>{icon_html(resource_icon_map[resource])}"
                          f" {resource} Production {round(production, 3)} /hr"
                          f"{extra_txt}</h8>")

    # Markdown output
    with st.container(border=True):
        st.markdown(f"""
        <img src='{resource_icon_map[resource]}' width='50' height='50' style='display: block; margin-left: auto; margin-right: auto;'/>
        <br>
        
        <h7>{icon_html(resource_icon_map['PP'])} BASE PP: {base_pp}</h7>
        
        <h7>{icon_html(resource_icon_map['PP'])} BOOSTED PP: {boosted_pp}</h7>

        <table>
            <tr>
                <th>Resource</th>
                <th>Cost / hr</th>
                <th>DEC / hr</th>
            </tr>
            {''.join([
            f"<tr>"
            f"<td>{icon_html(resource_icon_map[res])} {res}</td>"
            f"<td>{round(costs[res], 3)}</td>"
            f"<td>{round(dec_costs[res], 3)}</td>"
            f"</tr>"
            for res in consume_list
        ])}
        </table>
        {production_txt}
        {earning_txt}
        <h8>{icon_html(resource_icon_map['DEC'])}Net Positive DEC: {round(total_dec_earning - total_dec_cost, 3)} /hr
        <span style='color:gray'>(earn-cost)</span><br></h8>
        """, unsafe_allow_html=True)
    return total_dec_earning - total_dec_cost
