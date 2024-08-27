import argparse
import logging
from datetime import datetime, timedelta
from dateutil.rrule import rrulestr, rruleset
from dateutil.tz import UTC

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def check_rrule_in_slot(rrule_str, exrule_str=None, exdates=None):
    try:
        # Get the current UTC time and log it
        now_utc = datetime.now(UTC)
        logger.info(f"Current UTC time: {now_utc}")

        # Create rruleset and add the inclusion rule
        rules = rruleset()
        rules.rrule(rrulestr(rrule_str, forceset=True))
        logger.info(f"Inclusion rule applied: {rrule_str}")

        # Add exclusion rule if provided
        if exrule_str:
            rules.exrule(rrulestr(exrule_str, forceset=True))
            logger.info(f"Exclusion rule applied: {exrule_str}")

        # Add exclusion dates if provided
        if exdates:
            for exdate in exdates:
                # Ensure exdate is in UTC
                if exdate.tzinfo is None:
                    exdate = exdate.replace(tzinfo=UTC)
                else:
                    exdate = exdate.astimezone(UTC)
                rules.exdate(exdate)
                logger.info(f"Exclusion date added: {exdate}")

        # Round down the current UTC time to the nearest 30 minutes
        slot_start_utc = now_utc.replace(
            minute=(now_utc.minute // 30) * 30, second=0, microsecond=0
        )
        slot_end_utc = slot_start_utc + timedelta(minutes=30)
        logger.info(f"Slot start: {slot_start_utc}, Slot end: {slot_end_utc}")

        # Find the next occurrence after the current UTC time
        next_occurrence = rules.after(now_utc, inc=True)

        # Convert next_occurrence to UTC if it has a timezone and log it
        if next_occurrence:
            logger.info(f"Next occurrence (original): {next_occurrence}")
            if next_occurrence.tzinfo is not None:
                next_occurrence = next_occurrence.astimezone(UTC)
            logger.info(f"Next occurrence (UTC): {next_occurrence}")

        # Check if the next occurrence is within the current slot
        if next_occurrence and slot_start_utc <= next_occurrence < slot_end_utc:
            logger.info("Job is within the slot and will be scheduled.")
            return 0  # Next occurrence is within the slot
        else:
            logger.info("Job is not within the slot and will not be scheduled.")
            return 1  # Next occurrence is not within the slot

    except Exception as e:
        logger.error(f"Error: {e}")
        return -1  # Return -1 on error


def main():
    parser = argparse.ArgumentParser(
        description="Check if the next occurrence of an rrule is within the current 30-minute slot."
    )
    parser.add_argument(
        "--include-rule", required=True, help="The inclusion rrule string."
    )
    parser.add_argument(
        "--exclude-rule", required=False, help="The exclusion rrule string."
    )
    parser.add_argument(
        "--exclude-datetimes",
        required=False,
        nargs="+",
        help="A list of datetimes to exclude (in ISO format).",
    )

    args = parser.parse_args()

    # Parse exclude datetimes from strings to datetime objects
    exdates = []
    if args.exclude_datetimes:
        for dt_str in args.exclude_datetimes:
            exdates.append(datetime.fromisoformat(dt_str))

    # Call the check_rrule_in_slot function
    status = check_rrule_in_slot(args.include_rule, args.exclude_rule, exdates)
    exit(status)


if __name__ == "__main__":
    main()
