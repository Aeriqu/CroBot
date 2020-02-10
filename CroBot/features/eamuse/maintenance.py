#
# maintenance.py
# Contains all the functions needed for the maintenance related functionality
# Currently assumes that the machine uses JST as time zone
#

import datetime


MAINTENANCE_EXTENDED_START_HOUR = 2
MAINTENANCE_STANDARD_START_HOUR = 5
MAINTENANCE_END_HOUR = 7


async def check_dst():
    """
    check_dst: Checks if it is currently daylight savings in America (well, most places in America)
                - Starts on the 2nd Sunday in March
                - Ends on the 1st Sunday in November
    :return: - True if it is daylight savings
             - False if it is not daylight savings
    """
    date_month = datetime.date.today().month

    # If the month is outside of the range
    if date_month < 3 or date_month > 11:
        return False

    # If the month is inside of the guaranteed range
    if date_month > 3 and date_month < 11:
        return True

    # Otherwise, it is either March or November
    else:
        # Grab the week number for this given month
        date_week_number = (datetime.datetime.now().isocalendar()[1] -
                            datetime.datetime.now().replace(day=1).isocalendar()[1]) + 1
        # Grab the day number, with Monday being 1 and Sunday being 7
        date_day_number = datetime.datetime.now().isoweekday()

        # If the month is March
        if date_month == 3:
            # The start is at the second Sunday of March
            if date_week_number == 2 and date_day_number == 7:
                return True
            return date_week_number > 2

        # If the month is November, then anything past the first iso week should be fine
        else:
            # The end is at the first Sunday in November
            if date_week_number == 1 and date_day_number == 7:
                return False
            return date_week_number == 1


async def calculate_maintenance_times():
    """
    calculate_maintenance_times: Calculates the proper times for maintenance and
    :return: - If there's maintenance, a list of the times as tuples as follows:
                [
                    (JST_START_TIME, JST_END_TIME),
                    (PST/PDT_START_TIME, PST/PDT_END_TIME),
                    (CST/CDT_START_TIME, CST/CDT_END_TIME),
                    (EST/EDT_START_TIME, EST/EDT_END_TIME)
                ]
             - If there isn't maintenance: None
    """
    # Grab the week number for this given month
    date_week_number = (datetime.datetime.now().isocalendar()[1] -
                        datetime.datetime.now().replace(day=1).isocalendar()[1]) + 1
    # Grab the day number, with Monday being 1 and Sunday being 7
    date_day_number = datetime.datetime.now().isoweekday()
    # Hour offset is 1 if it's currently daylight savings
    hour_offset = 1 if await check_dst() else 0

    # If it's Saturday or Sunday, then there isn't maintenance
    if date_day_number == 6 or date_day_number == 7:
        return None

    # If it is the third Tuesday then it is extended maintenance
    if date_week_number == 4 and date_day_number == 2:
        japan_start_time = MAINTENANCE_EXTENDED_START_HOUR

    # Otherwise, it's regular maintenance
    else:
        japan_start_time = MAINTENANCE_STANDARD_START_HOUR

    return [
        (str(japan_start_time), str(MAINTENANCE_END_HOUR)),
        (str((japan_start_time + 7) + hour_offset), str((MAINTENANCE_END_HOUR + 7) + hour_offset)),
        (str((japan_start_time + 9) + hour_offset), str((MAINTENANCE_END_HOUR + 9) + hour_offset)),
        (str((japan_start_time + 10) + hour_offset), str((MAINTENANCE_END_HOUR + 10) + hour_offset))
    ]

