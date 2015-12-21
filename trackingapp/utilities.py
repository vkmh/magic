from django.db import connection


def get_card_price_points(source_id, expansion_id, start_date=None, end_date=None):
    cursor = connection.cursor()

    sql_filter = ''
    if start_date and end_date:
        sql_filter = "AND s.date BETWEEN '{start_date}' AND '{end_date}'".format(start_date=start_date, end_date=end_date)

    query = '''
        SELECT  c.id, c.name, e.id, date, high, medium, low

        FROM    trackingapp_card AS c

        JOIN    trackingapp_expansion AS e
        ON      e.id = c.expansion_id

        JOIN    trackingapp_sourceexpansion AS se
        ON      se.expansion_id = e.id

        JOIN    trackingapp_stock AS s
        ON      c.id = s.card_id

        WHERE   e.id = 1
        AND     is_active = 1
        {sql_filter}
        ORDER BY    s.date
    '''.format(source_id=source_id, sql_filter=sql_filter)
    cursor.execute(query)

    cards_dictionary = {}
    dates = []
    for card_id, name, expansion_id, date, high, medium, low in cursor.fetchall():
        if card_id not in cards_dictionary:
            cards_dictionary[card_id] = {}
            cards_dictionary[card_id]['name'] = name
            cards_dictionary[card_id]['expansion_id'] = expansion_id
            cards_dictionary[card_id]['dates'] = {}
        if date not in dates:
            dates.append(date)

        cards_dictionary[card_id]['dates'][date] = [low, medium, high]

    card_details = []
    for card_id in cards_dictionary:
        card_detail = {}
        card_detail['id'] = card_id
        card_detail['name'] = cards_dictionary[card_id]['name']
        card_detail['source_id'] = source_id
        card_detail['expansion_id'] = expansion_id
        card_detail['price_points'] = []

        for date in dates:
            card_detail['price_points'].append(cards_dictionary[card_id]['dates'][date][1])

        card_details.append(card_detail)

    return card_details, dates
