import { openingHours } from "./settings"

/**
 * JS Date.getDay() is indexed at 0 = Sunday.
 * But Python datetime.weekday() is indexed at 0 = Monday.
 * This function wraps the JS getDay so that it's compatible with the
 * 0-indexed Python version.
 */
type DayOfWeek = 0 | 1 | 2 | 3 | 4 | 5 | 6

function getWeekday(date: Date): DayOfWeek {
  return ((((date.getDay() - 1) % 7) + 7) % 7) as DayOfWeek
}

/**
 * Calculate snapshot times (30 minutes before opening) for each day
 */
const snapshotTimes = Object.entries(openingHours).reduce(
  (acc, [key, value]) => {
    const [hours, minutes] = value[0].split(":").map(Number)
    const openTime = new Date()
    openTime.setHours(hours, minutes, 0)

    // Subtract 30 minutes
    const snapshotTime = new Date(openTime)
    snapshotTime.setMinutes(openTime.getMinutes() - 30)

    return {
      ...acc,
      [key]: snapshotTime.toLocaleTimeString("en-US", {
        hour12: false,
        hour: "2-digit",
        minute: "2-digit",
      }),
    }
  },
  {} as Record<string, string>
)

/**
 * Returns true if the current time is after today's snapshot time
 */
export function wasSnapshotTaken(): boolean {
  const now = new Date()
  const dayOfWeek = getWeekday(now)

  // If center is closed (Sunday), no snapshot needed
  if (
    openingHours[dayOfWeek][0] === "00:00" &&
    openingHours[dayOfWeek][1] === "00:00"
  ) {
    return false
  }

  const todaySnapshot = snapshotTimes[dayOfWeek]
  const [snapshotHours, snapshotMinutes] = todaySnapshot.split(":").map(Number)

  const snapshotTime = new Date(now)
  snapshotTime.setHours(snapshotHours, snapshotMinutes, 0)

  return now >= snapshotTime
}

/**
 * Returns today's snapshot time
 */
export function todaySnapshotTime(): string {
  const now = new Date()
  if (getWeekday(now) === 6) {
    return "Closed"
  }
  return snapshotTimes[getWeekday(now)]
}

export function militaryToStandard(time: string): string {
  if (time === "Closed") {
    return "Closed"
  }
  const [hours, minutes] = time.split(":").map(Number)
  if (hours < 12) {
    return `${hours}:${minutes} AM`
  } else {
    return `${hours % 12}:${minutes} PM`
  }
}
