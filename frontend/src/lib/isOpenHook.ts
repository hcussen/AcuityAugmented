import { openingHours } from "./settings"

/**
 * Use this function to return if the center is currently open
 */

const snapshotTime = Object.entries(openingHours).map(([key, value]) => {
  // todo: finish the timedelta of value[0] - 30 min
  return { key: value[0] }
})

export function wasSnapshotTaken(): boolean {
  // look at settings timing config
  // return true if the current time is after open time - 30 min
  return false
}

export function todaySnapshotTime(): string {
  return ""
}
