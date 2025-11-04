import random
import copy
import smtplib
from email.message import EmailMessage
import json

with open("email_auth.json") as f:
    # Read in the auth for your mail account (tested with gmail app password only)
    email_auth = json.load(f)
    gmail_username = email_auth['gmail_username']
    gmail_app_password = email_auth['gmail_app_password']

def mailer(recipient, message, sender="santabot9000", subject="Secret Santa"):
    """
    Utility script for sending emails. You shouldn't need to change anything here
    :param recipient: email recipient
    :param message: email message
    :param sender: sender name
    :param subject: email subject
    :return: None
    """
    msg = EmailMessage()
    msg.set_content(message)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = recipient
    server = smtplib.SMTP('smtp.gmail.com', 25)
    server.connect('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(gmail_username, gmail_app_password)
    server.send_message(msg)
    server.quit()
    

def make_matches(email_dict, blocked_matches=()):
    """
    Randomise a list of participants and match them into giver:receiver pairs, ensuring that no-one is assigned
    themselves and that (optionally) certain pairings are blocked
    :param email_dict: Dictionary of participants and their details. We only use the keys of this dict
    :param blocked_matches: optional list of sets of blocked pairs in format ({'alice', 'bob'}) where we don't want
    Alice or Bob to be assigned each other
    :return: list of tuples in format [(giver, receiver)]
    """
    candidates = list(email_dict.keys())
    receivers = copy.copy(candidates)
    random.shuffle(receivers)
    pairs = []
    for giver, receiver in zip(candidates, receivers):
        if giver == receiver:
            # we can't have someone send a gift to themselves!
            print(f"self santa detected! {giver} buys for {receiver}. Retrying")
            return False
        if {giver, receiver} in blocked_matches:
            # note that blocked_matches is empty by default. Santa only cheats if you tell him to!
            print(f"undesirable secret santa detected! {giver} buys for {receiver}. Retrying")
            return False
        pairs.append((giver, receiver))
    return pairs


  
def mail_invites(email_dict, matches, dry_run=True):
    """
    Function to send emails to secret santa participants. You may wish to make some edits to the msg format string
    :param email_dict: A dictionary of participant names, emails and (optionally) wishlists
    :param matches: A list of tuples matching participants in format ((giver, receiver))
    :param dry_run: if True, does not send emails, just prints them. If False will send emails and not print (for anonymity)
    :return: None
    """
    if dry_run:
        print("matches successful!")
        for giver, receiver in matches:
            print(f"{giver.capitalize()} will buy for {receiver.capitalize()}")
    for giver, receiver in matches:
        giver_dict = email_dict[giver]
        receiver_dict = email_dict[receiver]
        msg = f"Ho ho ho {giver.capitalize()} 🎄\n\nYour assigned secret santa is {receiver.capitalize()} 🎅."
        if 'wishlist' in receiver_dict.keys():
            msg += f"\n\nThey have requested the following: {receiver_dict['wishlist']}"
        if dry_run:
            print(f"DRY RUN Would send email to {giver_dict['email']}, message:\n\n{msg}\n\n")
        else:
            mailer(giver_dict['email'], msg)
            print(f"sent mail to {giver_dict['email']}")



def secret_santa():
    dry_run = True

    participants = {
        'alice': {'email': 'alice@foo.com', 'wishlist': 'anchovies, bread, capers'},
        'bob': {'email': 'bob@bar.com'},
        'chris': {'email': 'chris@baz.com', 'wishlist': 'donuts'},
        'dina': {'email': 'dina@fizz.com'},
        'evan': {'email': 'evan@buzz.com', 'wishlist': 'ersatz'},
    }

    undesired_matches = (
        {'chris', 'evan'},
    )

    matches = False
    while not matches:
        matches = make_matches(participants, blocked_matches=undesired_matches)
    if matches:
        mail_invites(participants, matches, dry_run=dry_run)
    else:
        print("Could not make matches from list!")

if __name__ == '__main__':
    mailer("callum.rollo94@gmail.com", "test mail")
    secret_santa()
