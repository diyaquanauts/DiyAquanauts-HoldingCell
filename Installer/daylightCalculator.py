from suntime import Sun
from geopy.geocoders import Nominatim
import json
from datetime import datetime, timedelta


def calculateHoursOff(city_name, start_date, end_date, sbc_wattage):
    geolocator = Nominatim(user_agent="my_geocoder")
    location = geolocator.geocode(city_name)
    if not location:
        return None
    latitude = location.latitude
    longitude = location.longitude

    def getSunriseSunsetTimes(date):
        sun = Sun(latitude, longitude)
        sunrise = sun.get_sunrise_time(date)
        sunset = sun.get_sunset_time(date)
        return sunrise, sunset

    def calculateHoursOff(sunrise, sunset):
        return (sunset - sunrise).seconds / 3600

    result = []

    current_date = start_date

    while current_date <= end_date:
        sunrise, sunset = getSunriseSunsetTimes(current_date)
        hours_off = calculateHoursOff(sunrise, sunset)
        total_hours_in_day = 24

        result.append(
            {
                "date": current_date.strftime("%Y-%m-%d"),
                "sunrise": sunrise.strftime("%H:%M:%S"),
                "sunset": sunset.strftime("%H:%M:%S"),
                "totalHoursDaylight": total_hours_in_day - hours_off,
                "totalHoursDarkness": hours_off,
                "usableDaylightHours": max(0, total_hours_in_day - hours_off),
                "minRequiredWattage": sbc_wattage
                * (
                    total_hours_in_day - hours_off
                ),  # Minimally required wattage for usable daylight hours
            }
        )

        current_date += timedelta(days=1)

    totalDays = len(result)
    averageHoursOn = sum(day["usableDaylightHours"] for day in result) / totalDays
    averageHoursOff = 24 - averageHoursOn

    jsonData = {
        "averageHoursOn": averageHoursOn,
        "averageHoursOff": averageHoursOff,
        "dailyEstimates": result,
    }

    return json.dumps(jsonData, indent=2)


# Example usage
city_name = "Kona, Hawaii"
start_date = datetime(2024, 3, 1)
end_date = datetime(2024, 6, 1)
sbc_wattage = 12.5  # Example SBC wattage
result = calculateHoursOff(city_name, start_date, end_date, sbc_wattage)
print(result)
