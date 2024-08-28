import unittest
from datetime import datetime
from dateutil.tz import UTC

from scheduler import check_rrule_in_slot


class TestScheduler(unittest.TestCase):
    def test_europe_zurich_spring_dst_transition(self):
        rrule_str = "DTSTART;TZID=Europe/Zurich:20300331T020000 RRULE:FREQ=WEEKLY;BYDAY=SU;INTERVAL=1;COUNT=3"
        utc_now_str_before = "2030-03-31T00:25:00Z"
        utc_now = datetime.strptime(utc_now_str_before, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)

        result = check_rrule_in_slot(rrule_str, exrule_str=None, exdates=None)
        self.assertEqual(result, 0)  # Expected to be within the slot

    def test_europe_zurich_fall_dst_transition(self):
        rrule_str = "DTSTART;TZID=Europe/Zurich:20301027T030000 RRULE:FREQ=WEEKLY;BYDAY=SU;INTERVAL=1;COUNT=3"
        utc_now_str_before = "2030-10-27T00:25:00Z"
        utc_now = datetime.strptime(utc_now_str_before, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)

        result = check_rrule_in_slot(rrule_str, exrule_str=None, exdates=None)
        self.assertEqual(result, 0)  # Expected to be within the slot

    def test_us_central_spring_dst_transition(self):
        rrule_str = "DTSTART;TZID=US/Central:20300309T090000 RRULE:FREQ=DAILY;INTERVAL=1;COUNT=3"
        utc_now_str_before = "2030-03-09T15:00:00Z"
        utc_now = datetime.strptime(utc_now_str_before, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)

        result = check_rrule_in_slot(rrule_str, exrule_str=None, exdates=None)
        self.assertEqual(result, 0)  # Expected to be within the slot

    def test_us_central_fall_dst_transition(self):
        rrule_str = "DTSTART;TZID=US/Central:20301102T090000 RRULE:FREQ=DAILY;INTERVAL=1"
        utc_now_str_before = "2030-11-02T14:00:00Z"
        utc_now = datetime.strptime(utc_now_str_before, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)

        result = check_rrule_in_slot(rrule_str, exrule_str=None, exdates=None)
        self.assertEqual(result, 0)  # Expected to be within the slot

    def test_asia_tokyo_spring_dst_transition(self):
        rrule_str = "DTSTART;TZID=Asia/Tokyo:20300331T020000 RRULE:FREQ=WEEKLY;BYDAY=SU;INTERVAL=1;COUNT=3"
        utc_now_str_before = "2030-03-31T00:25:00Z"
        utc_now = datetime.strptime(utc_now_str_before, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)

        result = check_rrule_in_slot(rrule_str, exrule_str=None, exdates=None)
        self.assertEqual(result, 0)  # Expected to be within the slot

    def test_asia_tokyo_fall_dst_transition(self):
        rrule_str = "DTSTART;TZID=Asia/Tokyo:20301027T030000 RRULE:FREQ=WEEKLY;BYDAY=SU;INTERVAL=1;COUNT=3"
        utc_now_str_before = "2030-10-27T00:25:00Z"
        utc_now = datetime.strptime(utc_now_str_before, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)

        result = check_rrule_in_slot(rrule_str, exrule_str=None, exdates=None)
        self.assertEqual(result, 0)  # Expected to be within the slot

    def test_asia_singapore_spring_transition(self):
        rrule_str = "DTSTART;TZID=Asia/Singapore:20300331T020000 RRULE:FREQ=WEEKLY;BYDAY=SU;INTERVAL=1;COUNT=3"
        utc_now_str_before = "2030-03-31T00:25:00Z"
        utc_now = datetime.strptime(utc_now_str_before, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)

        result = check_rrule_in_slot(rrule_str, exrule_str=None, exdates=None)
        self.assertEqual(result, 0)  # Expected to be within the slot

    def test_asia_singapore_fall_transition(self):
        rrule_str = "DTSTART;TZID=Asia/Singapore:20301027T030000 RRULE:FREQ=WEEKLY;BYDAY=SU;INTERVAL=1;COUNT=3"
        utc_now_str_before = "2030-10-27T00:25:00Z"
        utc_now = datetime.strptime(utc_now_str_before, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)

        result = check_rrule_in_slot(rrule_str, exrule_str=None, exdates=None)
        self.assertEqual(result, 0)  # Expected to be within the slot


if __name__ == '__main__':
    unittest.main()
