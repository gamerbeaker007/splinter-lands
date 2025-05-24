from src.graphs.land_ranking_graphs import add_ranking_barchart


def add_ranking_overview(df, player):
    df = df[['player', 'deed_uid', 'total_harvest_pp', 'total_base_pp_after_cap', 'rewards_per_hour']].copy()

    df = df.groupby(['player']).agg(
        {
            'deed_uid': 'count',
            'total_harvest_pp': 'sum',
            'total_base_pp_after_cap': 'sum',
            'rewards_per_hour': 'sum'
        }).reset_index()
    df = df.rename(
        columns={
            'deed_uid': 'amount deeds',
            'total_harvest_pp': 'Boosted PP',
            'total_base_pp_after_cap': 'Raw PP',
        }
    )

    add_ranking_barchart(df, player, 'amount deeds')
    add_ranking_barchart(df, player, 'Boosted PP')
    add_ranking_barchart(df, player, 'Raw PP')
