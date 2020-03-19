# Intraday latency check function

from datetime import datetime
import pytz
from datacoco_batch.batch import Batch
from datacoco_core.logger import Logger


log = Logger()


def convert_time(t):
    # convert naive datetime object to utc aware datetime
    utc = pytz.utc
    timetz = utc.localize(t)
    return timetz


class CheckWF:
    """
    Calls batchy endpoint to get job status.
    """

    def __init__(self, wf, batchy_server, batchy_port):

        self.b = Batch(wf, batchy_server, batchy_port)
        log.l("Checking wf: {}".format(wf))

    def check_batchy_wf(self, max_latency):

        status = self.b.get_status().get("global")
        if status:
            failure_count, result = self.calc_latency_tests(
                status, max_latency
            )
        else:
            raise ValueError("Could not find wf")
        return failure_count, result

    @staticmethod
    def calc_latency_tests(result, max_latency):
        """
        run business logic on result to create alerts
        :param result:
        :param max_latency:
        :return:
        """
        failure_count = 0

        # use batch start, not end
        batch_start = result.get("batch_start")
        latency = (
            datetime.now(pytz.utc)
            - convert_time(
                datetime.strptime(batch_start, "%Y-%m-%dT%H:%M:%S.%f")
            )
        ).seconds / 60

        if latency >= max_latency:
            log.l(
                "latency: {} is greater than max latency: {}".format(
                    latency, max_latency
                )
            )
            failure_count = 1
            result["alert_level"] = "FAILURE"
            result["alert_message"] = "latency issue"
        elif result["status"] == "failure":
            log.l("failure b/c of job failure")
            result["alert_level"] = "FAILURE"
            result["alert_message"] = "job failure"
        elif latency >= max_latency * 0.8:
            log.l(
                "latency: {} is greater than 80% of max latency: {}".format(
                    latency, max_latency
                )
            )
            result["alert_level"] = "WARNING"
            result["alert_message"] = "passed 80% of latency threshold"
        else:
            result["alert_level"] = "SUCCESS"
            log.l("Success")
        result["latency"] = latency
        return failure_count, result
