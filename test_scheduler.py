import unittest
from unittest.mock import patch
from scheduler import check_rrule_in_slot
from datetime import datetime
from dateutil.tz import UTC


class TestRRuleCheckerLogging(unittest.TestCase):

    @patch("scheduler.logger")
    def test_logging_inclusion_only(self, mock_logger):
        rrule_str = (
            "DTSTART;TZID=UTC:20240101T090000\nRRULE:FREQ=DAILY;BYHOUR=9;BYMINUTE=0"
        )
        status = check_rrule_in_slot(rrule_str)
        mock_logger.info.assert_any_call(f"Current UTC time: {datetime.now(UTC)}")
        mock_logger.info.assert_any_call(
            "Job is within the slot and will be scheduled."
        )
        self.assertIn(status, [0, 1])

    @patch("scheduler.logger")
    def test_logging_with_exrule(self, mock_logger):
        rrule_str = (
            "DTSTART;TZID=UTC:20240101T090000\nRRULE:FREQ=DAILY;BYHOUR=9;BYMINUTE=0"
        )
        exrule_str = "RRULE:FREQ=YEARLY;BYMONTH=12;BYMONTHDAY=25"
        status = check_rrule_in_slot(rrule_str, exrule_str=exrule_str)
        mock_logger.info.assert_any_call(f"Exclusion rule applied: {exrule_str}")
        mock_logger.info.assert_any_call(
            "Job is within the slot and will be scheduled."
        )
        self.assertIn(status, [0, 1])

    @patch("scheduler.logger")
    def test_logging_with_exdate(self, mock_logger):
        rrule_str = (
            "DTSTART;TZID=UTC:20240101T090000\nRRULE:FREQ=DAILY;BYHOUR=9;BYMINUTE=0"
        )
        exdates = [datetime(2024, 8, 30, 9, 0, tzinfo=UTC)]
        status = check_rrule_in_slot(rrule_str, exdates=exdates)
        mock_logger.info.assert_any_call(f"Exclusion date added: {exdates[0]}")
        mock_logger.info.assert_any_call(
            "Job is within the slot and will be scheduled."
        )
        self.assertIn(status, [0, 1])

    @patch("scheduler.logger")
    def test_logging_job_not_scheduled(self, mock_logger):
        rrule_str = (
            "DTSTART;TZID=UTC:20240101T230000\nRRULE:FREQ=DAILY;BYHOUR=23;BYMINUTE=0"
        )
        status = check_rrule_in_slot(rrule_str)
        mock_logger.info.assert_any_call(
            "Job is not within the slot and will not be scheduled."
        )
        self.assertIn(status, [0, 1])

    @patch("scheduler.logger")
    def test_logging_error(self, mock_logger):
        rrule_str = "INVALID_RRULE_STRING"
        status = check_rrule_in_slot(rrule_str)
        mock_logger.error.assert_called_once()
        self.assertEqual(status, -1)


if __name__ == "__main__":
    unittest.main()
