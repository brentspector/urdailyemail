from .table import create_table, create_table_rows, create_market_mission_table
from urmarketscraper import market
from urcollectionmanager import api
from urcollectionmanager.purchase import Purchase
from requests import Session, get
from pathlib import Path
from itertools import islice
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
import os
import ssl
import smtplib
import re


def generate_email():
    """
    Run from command line via python -c "from urdailyemail import email; email.generate_email()"
    """
    with Session() as session:
        # Set up database and session initialization
        url = "https://ohbucketmybucket.s3-us-west-1.amazonaws.com/collection.sqlite"
        # file_path = Path(os.environ["USERPROFILE"] +
        #                  "\Desktop\database\collection.sqlite")
        file_path = os.environ["DB_FILE_PATH"]
        with get(url) as response, open(file_path, 'wb') as out_file:
            out_file.write(response.content)
        api.connect_and_initialize_database("sqlite",
                                            str(Path(file_path)))
        api.session_connect_to_ur(
            session, os.environ["UR_USER"], os.environ["UR_PASS"])

        # Get purchases from database to check against
        full_purchases = api.get_history_from_database()
        purchases = list(
            islice((purchase for purchase in full_purchases), int(os.environ["PURCHASE_COUNT"])))

        # Get market offers for purchases
        offers = market.get_market_offers(
            session, [purchase.id for purchase in purchases])

        # Get black market flash mission
        try:
            missions = api.convert_missions(
                api.get_missions_list(session, "black market"))
            bm_missions = [
                mission for mission in missions if "BLACK MARKET" in mission.name]
            bm_char_offers = {}
            for bm_mission in bm_missions:
                bm_mission_character = re.search(
                    '\\d(.+)(\\W)>', bm_mission.name)
                if bm_mission_character:
                    bm_mission_character = str(
                        bm_mission_character.group(1)).strip()
                else:
                    logging.error("Failed to process %s", bm_mission.name)
                try:
                    bm_offers = market.get_market_offers(
                        session, [bm_mission_character])
                    bm_char_offers[bm_mission.name] = bm_offers[bm_mission_character]
                except Exception as exception:
                    logging.error(
                        "Failed while generating black market offers: %s", str(exception))
        except Exception as exception:
            logging.exception(f"62 - {exception}")
            bm_missions = [api.get_missions_list(session, "black market").text]
            bm_char_offers = None

        # Create table for email
        table_rows = create_table_rows(purchases, offers)
        mission_table = create_market_mission_table(
            bm_missions, bm_char_offers)
        final_content = create_table(table_rows, mission_table)
        _send_email(final_content)
    return "OK"


def _populate_db():
    """
    Run with `python -c "from urdailyemail import email; email._populate_db()"`
    :return:
    """
    with Session() as session:
        api.session_connect_to_ur(
            session, os.environ["UR_USER"], os.environ["UR_PASS"])
        purchases_soup = api.get_purchase_history(session, 8)
        purchases = {item.id: item for sublist in api.convert_purchase_history(purchases_soup)
                     for item in sublist}
        api.connect_and_initialize_database("sqlite", str(
            Path(os.environ["USERPROFILE"] + "\Desktop\database\collection.sqlite")))
        # purchases = []
        # purchases.append(Purchase(name="Nameko", id=1540, price=3500, level=3))
        # purchases.append(Purchase(name="Guillotinette",
        #                           id=1638, price=1000, level=5))
        # purchases.append(
        #     Purchase(name="Gus Rope", id=1632, price=10000, level=3))
        # purchases.append(
        #     Purchase(name="Sopiket", id=1703, price=7000, level=3))
        # purchases.append(Purchase(name="Lucky", id=1338, price=2500, level=2))
        api.write_history_to_database([item for item in purchases.values()])


def _send_email(content):
    msg = MIMEMultipart("alternative")
    msg['Subject'] = "Daily UR Market Alert"
    msg['From'] = "brent.spector@yahoo.com"
    msg['To'] = "brent.spector@yahoo.com"
    textPart = MIMEText(content.render(), "text")
    msg.attach(textPart)
    htmlPart = MIMEText(content.render(), "html")
    msg.attach(htmlPart)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL('smtp.mail.yahoo.com', 465, context=context) as s:
        s.login(os.environ["EM_USER"], os.environ["EM_PASS"])
        s.sendmail(msg['From'], msg['To'], msg.as_string())
