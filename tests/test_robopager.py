import unittest
from robopager.robopager import parse_checklist, PDInteraction
from robopager.check_type.daily_email_check import CheckEmails
from robopager.check_type.intraday_latency_check import CheckWF
from robopager.check_type import intraday_latency_check
from datetime import datetime
import pytz
from unittest.mock import patch, MagicMock
from datacoco_core.config import config


class TestCommon(unittest.TestCase):
    def test_parse_checklist(self):
        """
        test reading of config yaml file and its output format
        :return:
        """

        config = "tests/test_data/test.yaml"
        expected = {
            "checklist_parse_test": {
                "type": "batchy",
                "pd_description": "Test for parsing checklist",
                "pd_service": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
                "wf_name": "checklist_parse_test",
                "check_time": "09:00",
                "poll_sec": 180,
                "latency_min": 60,
            }
        }
        found = parse_checklist(config)
        self.assertDictEqual(expected, found)


class TestBatchyWF(unittest.TestCase):
    def setUp(self):
        self.b = CheckWF("test_robopager", "0.0.0.0", "8050")

    @patch("datacoco_batch.batch.Batch.get_status")
    @patch.object(
        intraday_latency_check, "datetime", MagicMock(wraps=datetime)
    )
    def test_check_batchy_wf_success(self, mock_get_status):
        mock_get_status.return_value = {
            "global": {
                "batch_start": "2020-03-04T11:20:00.00",
                "status": "success",
            }
        }

        naive_time = datetime(2020, 3, 4, 11, 22, 0, 0)
        intraday_latency_check.datetime.now.return_value = pytz.utc.localize(
            naive_time
        )
        failure_count, result = self.b.check_batchy_wf(max_latency=3)
        self.assertEqual(failure_count, 0)
        self.assertEqual(result["alert_level"], "SUCCESS")


class TestPDInteraction(unittest.TestCase):
    def setUp(self):

        conf = config("tests/test_data/test_etl.cfg")
        sub_domain = conf["pager_duty"]["subdomain"]
        api_access_key = conf["pager_duty"]["api_access_key"]
        self.pd_service = conf["pager_duty"]["test_pd_service"]

        self.pd = PDInteraction(sub_domain, api_access_key)

    def test_trigger_incident(self):
        with patch("robopager.robopager.ri", create=True) as ri:
            resp = self.pd.trigger_incident(
                self.pd_service,
                "test_robopager",
                "test_robopager",
                check="test",
                override=True,
            )
            print("resp: {}".format(resp))
            self.assertEqual(resp, 200)


class TestCheckEmails(unittest.TestCase):
    def setUp(self):

        self.e = CheckEmails(
            "username",
            "password",
            "Successful - Job1 Completed",
            ["address@gmail.com"],
            "US/Easter",
        )
        self.e.subjects = ["Successful - Job1 Completed"]
        self.e.emails_received = [
            "Successful - Job2 Completed",
            "Successful - Job3 Completed",
            "Successful - Job4 Completed",
            "Successful - Job1 Completed",
        ]

        print(self.e.subjects)

    def test_check_missing_emails(self):

        failure_count, results = self.e.check_missing_emails()

        self.assertEqual(failure_count, 0)
        self.assertEqual(results, [{"Successful - Job1 Completed": "ok"}])

    def test_parse_gmail_dates(self):
        gdate = "Wed, 2 Jan 2019 01:47:40 -0500"
        date = self.e.parse_gmail_dates(gdate)
        self.assertEqual(date, datetime(2019, 1, 2, 1, 47, 40))


if __name__ == "__main__":
    unittest.main()
