import unittest
from unittest.mock import patch
from datetime import datetime
from dateutil.tz import UTC

from scheduler import check_rrule_in_slot


class TestScheduler(unittest.TestCase):
    def setUp(self):
        # This will be used to patch datetime.now(UTC) in each test
        self.patcher = patch("scheduler.datetime")
        self.mock_datetime = self.patcher.start()

    def tearDown(self):
        # Stop patching after each test
        self.patcher.stop()

    def set_mock_now(self, mock_now_str):
        mock_now = datetime.strptime(mock_now_str, "%Y-%m-%dT%H:%M:%SZ").replace(
            tzinfo=UTC
        )
        self.mock_datetime.now.return_value = mock_now
        self.mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)

    def test_europe_zurich_monthly(self):
        # This test is for a job scheduled at 08:00 on 26th October 2024 in Europe/Zurich time
        rrule_str = (
            "DTSTART;TZID=Europe/Zurich:20240101T090000 RRULE:FREQ=MONTHLY;BYDAY=1MO"
        )

        # Set the mock current time to 06:59 UTC, which is 08:59 in Europe/Zurich on the 26th October 2024
        self.set_mock_now("2024-09-02T07:00:00Z")

        result = check_rrule_in_slot(rrule_str, exrule_str=None, exdates=None)

        # Expect the job to be scheduled within the 07:00-07:30 UTC time slot
        self.assertEqual(result, 0)

    def test_europe_zurich_quarterly(self):
        # This test is for a job scheduled at 08:00 on 26th October 2024 in Europe/Zurich time
        rrule_str = "DTSTART;TZID=Europe/Zurich:20240101T090000 RRULE:FREQ=MONTHLY;INTERVAL=3;BYDAY=1MO"

        # Set the mock current time to 06:59 UTC, which is 08:59 in Europe/Zurich on the 26th October 2024
        self.set_mock_now("2024-10-07T07:00:00Z")

        result = check_rrule_in_slot(rrule_str, exrule_str=None, exdates=None)

        # Expect the job to be scheduled within the 07:00-07:30 UTC time slot
        self.assertEqual(result, 0)

    def test_europe_zurich_biannual(self):
        # This test is for a job scheduled at 08:00 on 26th October 2024 in Europe/Zurich time
        rrule_str = "DTSTART;TZID=Europe/Zurich:20240101T090000 RRULE:FREQ=MONTHLY;INTERVAL=6;BYDAY=1MO"

        # Set the mock current time to 06:59 UTC, which is 08:59 in Europe/Zurich on the 26th October 2024
        self.set_mock_now("2024-07-01T07:00:00Z")

        result = check_rrule_in_slot(rrule_str, exrule_str=None, exdates=None)

        # Expect the job to be scheduled within the 07:00-07:30 UTC time slot
        self.assertEqual(result, 0)

    def test_europe_zurich_annual(self):
        # This test is for a job scheduled at 09:00 on 1st January 2024 (the first Monday) in Europe/Zurich time
        rrule_str = "DTSTART;TZID=Europe/Zurich:20230101T090000 RRULE:FREQ=YEARLY;BYMONTH=1;BYDAY=1MO"

        # Set the mock current time to just before 09:00 on 1st January 2024
        self.set_mock_now("2024-01-01T08:00:00Z")

        result = check_rrule_in_slot(rrule_str, exrule_str=None, exdates=None)

        # Expect the job to be scheduled within the 08:59-09:30 UTC time slot
        self.assertEqual(result, 0)

    def test_europe_zurich_before_fall_dst_transition(self):
        # This test is for a job scheduled at 08:00 on 26th October 2024 in Europe/Zurich time
        rrule_str = "DTSTART;TZID=Europe/Zurich:20241026T080000 RRULE:FREQ=DAILY;INTERVAL=1;COUNT=1"

        # Set the mock current time to 06:59 UTC, which is 08:59 in Europe/Zurich on the 26th October 2024
        self.set_mock_now("2024-10-26T06:00:00Z")

        result = check_rrule_in_slot(rrule_str, exrule_str=None, exdates=None)

        # Expect the job to be scheduled within the 07:00-07:30 UTC time slot
        self.assertEqual(result, 0)

    def test_europe_zurich_before_fall_dst_transition_exdate_skip(self):
        # This test is for a job scheduled at 08:00 on 26th October 2024 in Europe/Zurich time
        rrule_str = "DTSTART;TZID=Europe/Zurich:20241026T080000 RRULE:FREQ=DAILY;INTERVAL=1;COUNT=1"

        # Set the mock current time to 06:00 UTC, which is 08:00 in Europe/Zurich on the 26th October 2024
        self.set_mock_now("2024-10-26T06:00:00Z")

        # Exclude the exact time when the job is supposed to run
        exdates = [
            datetime.strptime("2024-10-26T06:00:00Z", "%Y-%m-%dT%H:%M:%SZ").replace(
                tzinfo=UTC
            )
        ]

        result = check_rrule_in_slot(rrule_str, exrule_str=None, exdates=exdates)

        # Expect the job to not be scheduled due to the exclusion date, returning 1
        self.assertEqual(result, 1)

    def test_europe_zurich_before_fall_dst_transition_exdate_noskip(self):
        # This test is for a job scheduled at 08:00 on 26th October 2024 in Europe/Zurich time
        rrule_str = "DTSTART;TZID=Europe/Zurich:20241026T080000 RRULE:FREQ=DAILY;INTERVAL=1;COUNT=1"

        # Set the mock current time to 06:00 UTC, which is 08:00 in Europe/Zurich on the 26th October 2024
        self.set_mock_now("2024-10-26T06:00:00Z")

        # Exclude the exact time when the job is supposed to run
        exdates = [
            datetime.strptime("2024-10-25T06:00:00Z", "%Y-%m-%dT%H:%M:%SZ").replace(
                tzinfo=UTC
            )
        ]

        result = check_rrule_in_slot(rrule_str, exrule_str=None, exdates=exdates)

        # Expect the job to not be scheduled due to the exclusion date, returning 1
        self.assertEqual(result, 0)

    def test_europe_zurich_after_fall_dst_transition(self):
        # This test is for a job scheduled at 08:00 on 27th October 2024 in Europe/Zurich time
        rrule_str = "DTSTART;TZID=Europe/Zurich:20241027T080000 RRULE:FREQ=DAILY;INTERVAL=1;COUNT=1"

        # Set the mock current time to 06:59 UTC, which is 07:59 in Europe/Zurich on the 27th October 2024 (after DST ends)
        self.set_mock_now("2024-10-27T07:00:00Z")

        result = check_rrule_in_slot(rrule_str, exrule_str=None, exdates=None)

        # Expect the job to be scheduled within the 07:00-07:30 UTC time slot
        self.assertEqual(result, 0)

    def test_europe_zurich_before_fall_dst_transition_exrule_skip(self):
        # This test is for a job scheduled at 08:00 on 26th December 2024 in Europe/Zurich time
        rrule_str = "DTSTART;TZID=Europe/Zurich:20241226T080000 RRULE:FREQ=DAILY;INTERVAL=1;COUNT=1"

        # Set the mock current time to 07:00 UTC, which is 08:00 in Europe/Zurich on 26th December 2024
        self.set_mock_now("2024-12-26T07:00:00Z")

        # Exclusion rule to skip the last two weeks of December
        exrule_str = "DTSTART;TZID=Europe/Zurich:20240101T080000 RRULE:FREQ=DAILY;BYMONTH=12;BYMONTHDAY=17,18,19,20,21,22,23,24,25,26,27,28,29,30,31"

        result = check_rrule_in_slot(rrule_str, exrule_str=exrule_str, exdates=None)

        # Expect the job to not be scheduled due to the exclusion rule, returning 1
        self.assertEqual(result, 1)

    def test_europe_zurich_before_fall_dst_transition_exrule_no_skip(self):
        # This test is for a job scheduled at 08:00 on 26th December 2024 in Europe/Zurich time
        rrule_str = "DTSTART;TZID=Europe/Zurich:20241226T080000 RRULE:FREQ=DAILY;INTERVAL=1;COUNT=1"

        # Set the mock current time to 07:00 UTC, which is 08:00 in Europe/Zurich on 26th December 2024
        self.set_mock_now("2024-12-26T07:00:00Z")

        # Exclusion rule to skip the last two weeks of December
        exrule_str = "DTSTART;TZID=Europe/Zurich:20240101T080000 RRULE:FREQ=DAILY;BYMONTH=12;BYMONTHDAY=1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20"

        result = check_rrule_in_slot(rrule_str, exrule_str=exrule_str, exdates=None)

        # Expect the job to not be scheduled due to the exclusion rule, returning 1
        self.assertEqual(result, 0)

    def test_europe_zurich_before_fall_dst_transition_exrule_exdate_skip(self):
        # This test is for a job scheduled at 08:00 on 26th December 2024 in Europe/Zurich time
        rrule_str = "DTSTART;TZID=Europe/Zurich:20241226T080000 RRULE:FREQ=DAILY;INTERVAL=1;COUNT=1"

        # Set the mock current time to 07:00 UTC, which is 08:00 in Europe/Zurich on 26th December 2024
        self.set_mock_now("2024-12-26T07:00:00Z")

        # Exclusion rule to skip the last two weeks of December
        exrule_str = "DTSTART;TZID=Europe/Zurich:20240101T080000 RRULE:FREQ=DAILY;BYMONTH=12;BYMONTHDAY=1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20"
        exdates = [
            datetime.strptime("2024-12-26T07:00:00Z", "%Y-%m-%dT%H:%M:%SZ").replace(
                tzinfo=UTC
            )
        ]
        result = check_rrule_in_slot(rrule_str, exrule_str=exrule_str, exdates=exdates)

        # Expect the job to not be scheduled due to the exclusion rule, returning 1
        self.assertEqual(result, 1)

    def test_europe_zurich_before_fall_dst_transition_exrule_exdate_no_skip(self):
        # This test is for a job scheduled at 08:00 on 26th December 2024 in Europe/Zurich time
        rrule_str = "DTSTART;TZID=Europe/Zurich:20241226T080000 RRULE:FREQ=DAILY;INTERVAL=1;COUNT=1"

        # Set the mock current time to 07:00 UTC, which is 08:00 in Europe/Zurich on 26th December 2024
        self.set_mock_now("2024-12-26T07:00:00Z")

        # Exclusion rule to skip the last two weeks of December
        exrule_str = "DTSTART;TZID=Europe/Zurich:20240101T080000 RRULE:FREQ=DAILY;BYMONTH=12;BYMONTHDAY=1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20"
        # exdate does not match the second so we won't skip
        exdates = [
            datetime.strptime("2024-12-26T07:00:01Z", "%Y-%m-%dT%H:%M:%SZ").replace(
                tzinfo=UTC
            )
        ]
        result = check_rrule_in_slot(rrule_str, exrule_str=exrule_str, exdates=exdates)

        # Expect the job to not be scheduled due to the exclusion rule, returning 1
        self.assertEqual(result, 0)

    def test_europe_zurich_before_spring_dst_transition(self):
        # This test is for a job scheduled at 08:00 on 30th March 2024 in Europe/Zurich time
        rrule_str = "DTSTART;TZID=Europe/Zurich:20240330T080000 RRULE:FREQ=DAILY;INTERVAL=1;COUNT=1"

        # Set the mock current time to 07:00 UTC, which is 08:00 in Europe/Zurich on 30th March 2024
        self.set_mock_now("2024-03-30T07:00:00Z")

        result = check_rrule_in_slot(rrule_str, exrule_str=None, exdates=None)

        # Expect the job to be scheduled within the 07:00-07:30 UTC time slot
        self.assertEqual(result, 0)

    def test_europe_zurich_after_spring_dst_transition(self):
        # This test is for a job scheduled at 08:00 on 31st March 2024 in Europe/Zurich time
        rrule_str = "DTSTART;TZID=Europe/Zurich:20240331T080000 RRULE:FREQ=DAILY;INTERVAL=1;COUNT=1"

        # Set the mock current time to 06:00 UTC, which is 08:00 in Europe/Zurich on 31st March 2024 (after DST begins)
        self.set_mock_now("2024-03-31T06:00:00Z")

        result = check_rrule_in_slot(rrule_str, exrule_str=None, exdates=None)

        # Expect the job to be scheduled within the 06:00-06:30 UTC time slot
        self.assertEqual(result, 0)

    def test_chicago_before_spring_dst_transition(self):
        # This test is for a job scheduled at 08:00 on 05th March 2024 in Chicago time
        rrule_str = "DTSTART;TZID=America/Chicago:20240305T080000 RRULE:FREQ=DAILY;INTERVAL=1;COUNT=1"

        # Set the mock current time to 14:00 UTC, which is 08:00 in Chicago on 05th March 2024
        self.set_mock_now("2024-03-05T14:00:00Z")

        result = check_rrule_in_slot(rrule_str, exrule_str=None, exdates=None)

        # Expect the job to be scheduled within the 14:00-14:30 UTC time slot
        self.assertEqual(result, 0)

    def test_chicago_after_spring_dst_transition(self):
        # This test is for a job scheduled at 08:00 on 11th March 2024 in Chicago time
        rrule_str = "DTSTART;TZID=America/Chicago:20240311T080000 RRULE:FREQ=DAILY;INTERVAL=1;COUNT=1"

        # Set the mock current time to 13:00 UTC, which is 08:00 in Chicago on 11th March 2024 (after DST begins)
        self.set_mock_now("2024-03-11T13:00:00Z")

        result = check_rrule_in_slot(rrule_str, exrule_str=None, exdates=None)

        # Expect the job to be scheduled within the 13:00-13:30 UTC time slot
        self.assertEqual(result, 0)

    def test_chicago_before_fall_dst_transition(self):
        # This test is for a job scheduled at 08:00 on 1st November 2024 in Chicago time
        rrule_str = "DTSTART;TZID=America/Chicago:20241101T080000 RRULE:FREQ=DAILY;INTERVAL=1;COUNT=1"

        # Set the mock current time to 13:00 UTC, which is 08:00 in Chicago on 1st November 2024
        self.set_mock_now("2024-11-01T13:00:00Z")

        result = check_rrule_in_slot(rrule_str, exrule_str=None, exdates=None)

        # Expect the job to be scheduled within the 13:00-13:30 UTC time slot
        self.assertEqual(result, 0)

    def test_chicago_after_fall_dst_transition(self):
        # This test is for a job scheduled at 08:00 on 4th November 2024 in Chicago time
        rrule_str = "DTSTART;TZID=America/Chicago:20241104T080000 RRULE:FREQ=DAILY;INTERVAL=1;COUNT=1"

        # Set the mock current time to 14:00 UTC, which is 08:00 in Chicago on 4th November 2024 (after DST ends)
        self.set_mock_now("2024-11-04T14:00:00Z")

        result = check_rrule_in_slot(rrule_str, exrule_str=None, exdates=None)

        # Expect the job to be scheduled within the 14:00-14:30 UTC time slot
        self.assertEqual(result, 0)

    # Tokyo does not observer DST
    def test_tokyo_february(self):
        # This test is for a job scheduled at 08:00 on 1st February 2024 in Tokyo time
        rrule_str = "DTSTART;TZID=Asia/Tokyo:20240201T080000 RRULE:FREQ=DAILY;INTERVAL=1;COUNT=1"

        # Set the mock current time to 23:00 UTC on 31st January 2024, which is 08:00 in Tokyo on 1st February 2024
        self.set_mock_now("2024-01-31T23:00:00Z")

        result = check_rrule_in_slot(rrule_str, exrule_str=None, exdates=None)

        # Expect the job to be scheduled within the 23:00-23:30 UTC time slot
        self.assertEqual(result, 0)

    def test_tokyo_october(self):
        # This test is for a job scheduled at 08:00 on 1st October 2024 in Tokyo time
        rrule_str = "DTSTART;TZID=Asia/Tokyo:20241001T080000 RRULE:FREQ=DAILY;INTERVAL=1;COUNT=1"

        # Set the mock current time to 23:00 UTC on 30th September 2024, which is 08:00 in Tokyo on 1st October 2024
        self.set_mock_now("2024-09-30T23:00:00Z")

        result = check_rrule_in_slot(rrule_str, exrule_str=None, exdates=None)

        # Expect the job to be scheduled within the 23:00-23:30 UTC time slot
        self.assertEqual(result, 0)

    # We use tokyo to verify slotting logic, since it does not observe DST
    def test_tokyo_slot_30_mismatch(self):
        # This test is for a job scheduled at 08:00 on 1st October 2024 in Tokyo time
        rrule_str = "DTSTART;TZID=Asia/Tokyo:20241001T080000 RRULE:FREQ=DAILY;INTERVAL=1;COUNT=1"

        # Set the mock current time to 22:30 UTC on 30th September 2024, which is 07:30 in Tokyo on 1st October 2024
        self.set_mock_now("2024-09-30T22:30:00Z")

        result = check_rrule_in_slot(rrule_str, exrule_str=None, exdates=None)

        # Expect the job to not be scheduled within the 23:00-23:30 UTC time slot since the end is not inclusive
        self.assertEqual(result, 1)

    def test_tokyo_slot_30_match(self):
        # This test is for a job scheduled at 08:00 on 1st October 2024 in Tokyo time
        rrule_str = "DTSTART;TZID=Asia/Tokyo:20241001T073000 RRULE:FREQ=DAILY;INTERVAL=1;COUNT=1"

        # Set the mock current time to 22:30 UTC on 30th September 2024, which is 07:30 in Tokyo on 1st October 2024
        self.set_mock_now("2024-09-30T22:30:00Z")

        result = check_rrule_in_slot(rrule_str, exrule_str=None, exdates=None)

        # Expect the job to not be scheduled within the 23:00-23:30 UTC time slot since the end is not inclusive
        self.assertEqual(result, 0)

    def test_tokyo_slot_00_mismatch(self):
        # This test is for a job scheduled at 08:00 on 1st October 2024 in Tokyo time
        rrule_str = "DTSTART;TZID=Asia/Tokyo:20241001T083000 RRULE:FREQ=DAILY;INTERVAL=1;COUNT=1"

        # Set the mock current time to 23:00 UTC on 30th September 2024, which is 08:00 in Tokyo on 1st October 2024
        self.set_mock_now("2024-09-30T22:00:00Z")

        result = check_rrule_in_slot(rrule_str, exrule_str=None, exdates=None)

        # Expect the job to not be scheduled within the 22:30-23:00 UTC time slot since the end is not inclusive
        self.assertEqual(result, 1)

    def test_30_slotting_logic(self):
        # This test is for a job scheduled at 08:00 on 1st October 2024 in Tokyo time
        rrule_str = "DTSTART;TZID=Asia/Tokyo:20241001T075500 RRULE:FREQ=HOURLY;INTERVAL=1;COUNT=1"

        # Set the mock current time to 22:30 UTC on 30th September 2024, which is 07:30 in Tokyo on 1st October 2024
        self.set_mock_now("2024-09-30T22:54:55Z")

        result = check_rrule_in_slot(rrule_str, exrule_str=None, exdates=None)

        # Expect the job to not be scheduled within the 23:00-23:30 UTC time slot since the end is not inclusive
        self.assertEqual(result, 0)

    def test_00_slotting_logic(self):
        # This test is for a job scheduled at 08:00 on 1st October 2024 in Tokyo time
        rrule_str = "DTSTART;TZID=Asia/Tokyo:20241001T072900 RRULE:FREQ=HOURLY;INTERVAL=1;COUNT=1"

        # Set the mock current time to 22:30 UTC on 30th September 2024, which is 07:30 in Tokyo on 1st October 2024
        self.set_mock_now("2024-09-30T22:28:55Z")

        result = check_rrule_in_slot(rrule_str, exrule_str=None, exdates=None)

        # Expect the job to not be scheduled within the 23:00-23:30 UTC time slot since the end is not inclusive
        self.assertEqual(result, 0)


if __name__ == "__main__":
    unittest.main()
