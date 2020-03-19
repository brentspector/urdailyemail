from .table import create_table, create_table_rows
from urmarketscraper import market
from urcollectionmanager import api
from requests import Session
from pathlib import Path
from itertools import islice
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import ssl
import smtplib


def generate_email():
    with Session() as session:
        # TODO - Get this from S3 not Desktop
        api.connect_and_initialize_database("sqlite",
                                            str(Path(os.environ["USERPROFILE"] + "\Desktop\database\collection.sqlite")))
        api.session_connect_to_ur(
            session, os.environ["UR_USER"], os.environ["UR_PASS"])
        full_purchases = api.get_history_from_database()
        purchases = list(islice((purchase for purchase in full_purchases), 10))
        offers = market.get_market_offers(
            session, [purchase.id for purchase in purchases])
        table_rows = create_table_rows(purchases, offers)
        final_content = create_table(table_rows)
        _send_email(final_content)
    return "OK"


def _populate_db():
    with Session() as session:
        api.session_connect_to_ur(
            session, os.environ["UR_USER"], os.environ["UR_PASS"])
        purchases_soup = api.get_purchase_history(session, 19)
        purchases = [item for sublist in api.convert_purchase_history(purchases_soup)
                     for item in sublist]
        api.connect_and_initialize_database("sqlite", str(
            Path(os.environ["USERPROFILE"] + "\Desktop\database\collection.sqlite")))
        api.write_history_to_database(purchases)


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
