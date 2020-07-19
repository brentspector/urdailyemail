from .table_row import TableRow
from dominate.tags import html, body, table, thead, tbody, tr, th, td
import logging


def create_table(table_rows, *content):
    html_table = table(cellspacing="0", cellpadding="5", width="100%",
                       margin="0 auto", border="1", style="white-space:nowrap;")
    with html_table.add(thead()).add(tr()):
        for val in ["name", "purchase_price", "purchase_level", "min_price", "min_level", "min_profit",
                    "min_percent", "relevant_price", "relevant_level", "relevant_profit", "relevant_percent"]:
            th(val)
    with html_table:
        tbody(table_rows)
    return html(body(table(tr(td(html_table, *content)))))


def create_table_rows(purchases, offers):
    obj_table_rows = [
        _create_obj_table_row(purchase, offers[purchase.id])
        for purchase
        in purchases
    ]

    obj_table_rows = sorted(obj_table_rows, key=lambda o: o.min_percent)

    html_table_rows = [
        _create_html_table_row(tr_obj)
        for tr_obj
        in obj_table_rows
    ]

    html_table_rows.append(_summate_values(obj_table_rows))
    return html_table_rows


def create_market_mission_table(missions, offers):
    html_table = table(cellspacing="0", cellpadding="5", width="30%",
                       margin="0 auto", border="1", style="white-space:nowrap;")
    with html_table.add(thead()).add(tr()):
        for val in ["mission", "value"]:
            th(val)
    with html_table:
        if not offers:
            name_val = missions[0] if missions else "N/A"
            tbody(tr(td(name_val), td("N/A")))
        else:
            for mission in missions:
                try:
                    offer_price = offers[mission.name].get_min_price()
                except Exception as exception:
                    logging.error("Failed to tabulate %s", mission.name)
                    logging.error(str(exception))
                    offer_price = "N/A"
                tbody(tr(td(mission.name), td(offer_price)))
    return html_table


def _create_obj_table_row(purchase, offer):
    return TableRow(**{'name': purchase.name, 'purchase_price': purchase.price,
                       'purchase_level': purchase.level,
                       'min_price': offer.get_min_price(), 'min_level': offer.get_min_level(),
                       'relevant_price': offer.get_rel_price(purchase.level),
                       'relevant_level': offer.get_rel_level(purchase.level)})


def _create_html_table_row(tr_obj):
    evaluated_row = tr()
    with evaluated_row:
        td(f'{tr_obj.name}', id='name',
           style=f'color:{_get_property_color("name", tr_obj.name)}')
        td(f'{tr_obj.purchase_price:,d}', id='purchase_price',
           style=f'color:{_get_property_color("purchase_price", tr_obj.purchase_price)}')
        td(f'{tr_obj.purchase_level}', id='purchase_level',
           style=f'color:{_get_property_color("level", tr_obj.purchase_level)}')
        td(f'{tr_obj.min_price:,d}', id='min_price',
           style=f'color:{_get_property_color("price", tr_obj.min_price)}')
        td(f'{tr_obj.min_level}', id='min_level',
           style=f'color:{_get_property_color("level", tr_obj.min_level)}')
        td(f'{tr_obj.min_profit:,d}', id='min_profit',
           style=f'color:{_get_property_color("profit", tr_obj.min_profit)}')
        td(f'{tr_obj.min_percent:.2f}', id='min_percent',
           style=f'color:{_get_property_color("percent", tr_obj.min_percent)}')
        td(f'{tr_obj.relevant_price:,d}', id='relevant_price',
           style=f'color:{_get_property_color("price", tr_obj.relevant_price)}')
        td(f'{tr_obj.relevant_level}', id='relevant_level',
           style=f'color:{_get_property_color("level", tr_obj.relevant_level)}')
        td(f'{tr_obj.relevant_profit:,d}', id='relevant_profit',
           style=f'color:{_get_property_color("profit", tr_obj.relevant_profit)}')
        td(f'{tr_obj.relevant_percent:.2f}', id='relevant_percent',
           style=f'color:{_get_property_color("percent", tr_obj.relevant_percent)}')

    return evaluated_row


def _get_property_color(property, value):
    return {
        'profit': lambda value: 'yellowgreen' if value > 0 else 'crimson',
        'name': lambda value: 'blue',
        'percent': lambda value: 'darkgreen' if value > 0 else 'maroon',
        'purchase_price': lambda vale: 'chocolate'
    }.get(property, lambda value: 'black')(value)


def _summate_values(table_rows):
    purchase_sum = sum(row.purchase_price for row in table_rows)
    min_price_sum = sum(row.min_price for row in table_rows)
    relevant_price_sum = sum(row.relevant_price for row in table_rows)
    return _create_html_table_row(TableRow(**{'name': '',
                                              'purchase_price': purchase_sum, 'purchase_level': 0,
                                              'min_price': min_price_sum, 'min_level': 0,
                                              'relevant_price': relevant_price_sum, 'relevant_level': 0}))
