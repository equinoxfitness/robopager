# Email check function

import imaplib
import email
from datetime import datetime, date
import pytz
from datacoco_core.logger import Logger


log = Logger()


def convert_local_to_utc(t, timezone):
    # convert local time to utc (both are naive)
    local = pytz.timezone(timezone)
    local_dt = local.localize(t)
    utc_dt = local_dt.astimezone(pytz.utc)
    naive_utc = utc_dt.replace(tzinfo=None)
    return naive_utc


class CheckEmails:
    """
    scans and filters gmail inbox
    """

    def __init__(
        self,
        username,
        password,
        subjects,
        senders,
        timezone,
        received_after="00:00",
    ):
        """
        :param subjects:
        :param senders:
        :param received_after:  default is midnight
        :return:
        """

        self.imapSession = imaplib.IMAP4_SSL("imap.gmail.com")
        self.username = username
        self.password = password

        self.subjects = subjects
        self.senders = senders
        self.received_after = received_after
        self.emails_received = []
        self.timezone = timezone

    def login(self):
        log.l("connecting to gmail")
        typ, accountDetails = self.imapSession.login(
            self.username, self.password
        )
        if typ != "OK":
            log.l("Not able to sign in!")
            raise
            exit(1)

    def get_emails(self):
        """
        pulls down a list of emails, filters by time, subject, senders
        :return: emails recieved matching criteria
        """

        self.login()

        # select messages
        date_received = (date.today()).strftime("%d-%b-%Y")
        delivery_threshold = datetime.strptime(
            " ".join((date_received, self.received_after)), "%d-%b-%Y %H:%M"
        )
        utc_delivery_threshold = convert_local_to_utc(
            delivery_threshold, self.timezone
        )

        imap_search = '(SENTSINCE {date} FROM "{senders}")'.format(
            date=date_received, senders=",".join(self.senders)
        )
        self.imapSession.select('"[Gmail]/All Mail"')
        typ, data = self.imapSession.search(None, imap_search)
        if typ != "OK":
            log.l("Error searching Inbox.")
            raise
        log.l(str(len(data[0].split())) + " emails found")

        # Iterating over all emails
        for msgId in data[0].split():
            # typ, messageParts = imapSession.fetch(msgId, '(RFC822)')
            typ, messageParts = self.imapSession.fetch(
                msgId, "(BODY.PEEK[HEADER])"
            )
            msg = email.message_from_bytes(messageParts[0][1])
            # print msg['Subject']
            # print msg['Date']
            time_recieved = self.parse_gmail_dates(msg["Date"])
            if time_recieved < utc_delivery_threshold:
                continue
            self.emails_received.append(msg["Subject"].replace("\r\n", ""))
            if typ != "OK":
                log.l("Error fetching mail.")
                raise
                exit(1)
        log.l("emails recieved: " + ",".join(self.emails_received))
        return self.emails_received

    def check_missing_emails(self):
        """
        compares list of expected subjects to what is retrieved
        :return: failure_count, results
        """
        log.l("look for emails not received")
        results = []
        failure_count = 0
        for x in self.subjects:
            r = {}
            if x in self.emails_received:
                r[x] = "ok"
            else:
                r[x] = "not received"
                failure_count += 1
            results.append(r)

        return failure_count, results

    def close_session(self):
        """
        closes imap sesion
        """
        self.imapSession.close()
        self.imapSession.logout()
        log.l("disconnected from gmail")
