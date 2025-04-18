from src.static.static_values_enum import biome_mapper

biome_style = """
<style>
    .pos_boost {
        color: green;
        font-weight: bold;
        font-family: monospace;
        font-size: 8pt;
        display: block;
        text-align: center;
    }
    .neg_boost {
        color: red;
        font-weight: bold;
        font-family: monospace;
        font-size: 8pt;
        display: block;
        text-align: center;
    }
    .biome_img {
        vertical-align: middle;
        height: 25px;
        padding: 2px;
        border: 1px solid white;
        box-sizing: border-box;
        display: block;
        margin-left: auto;
        margin-right: auto;
    }
    .biome_container {
        display: inline-block;
        text-align: center;
        margin: 1px;
    }
</style>
"""

color_map = {
    'red': 'red',
    'blue': 'blue',
    'white': 'gray',
    'black': 'purple',
    'green': 'green',
    'gold': "gold",
}


def add_biome(row):
    positives_html = ""
    negatives_html = ""

    for biome, color in color_map.items():
        modifier = row.get(f'{biome}_biome_modifier', 0)
        if modifier != 0:
            url = biome_mapper.get(biome)
            percent = modifier * 100
            css_class = 'pos_boost' if percent > 0 else 'neg_boost'

            html_block = f"""
            <div class="biome_container">
                <img src="{url}" class="biome_img" style="background-color:{color};" />
                <span class="{css_class}">{percent:+.0f}%</span>
            </div>"""

            if percent > 0:
                positives_html += html_block
            else:
                negatives_html += html_block

    final_html = ""
    if positives_html:
        final_html += f"<div>{positives_html}</div>"
    if negatives_html:
        final_html += f"<div style='margin-top: 10px;'>{negatives_html}</div>"

    return final_html
