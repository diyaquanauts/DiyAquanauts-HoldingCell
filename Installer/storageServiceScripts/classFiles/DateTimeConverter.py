class DateTimeConverter:
    @staticmethod
    def nanosecondsToBaseX(nanoseconds, alphabet="abcdefghijklmnopqrstuvwxyz"):
        # Convert nanoseconds to base26
        timeToBaseX = ""

        xBase = len(alphabet) + 1

        while nanoseconds > 0:
            remainder = nanoseconds % xBase
            timeToBaseX = alphabet[remainder - 1] + timeToBaseX
            nanoseconds //= xBase
        return timeToBaseX


