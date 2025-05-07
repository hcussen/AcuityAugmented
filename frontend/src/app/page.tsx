"use client"

import { useEffect, useState, useMemo } from "react"
import { HourlyDiff, HourCount, Appointment } from "@/lib/types"
import { Button } from "@/components/ui/button"
import DiffTable from "./DiffTable"
import AppointmentsTable from "./AppointmentsTable"
import { getScheduleDiff, getSchedule } from "@/lib/api-actions"
import { wasSnapshotTaken } from "@/lib/snaphotTimingUtils"
import { logout } from "./login/actions"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Clock } from "lucide-react"

export default function Home() {
  const dayOfWeek = new Date().getDay()
  const [scheduleDiff, setScheduleDiff] = useState<Array<HourlyDiff> | null>(
    null
  )
  const [schedule, setSchedule] = useState<Appointment[] | null>(null)
  // eslint-disable-next-line
  const [isLoading, setIsLoading] = useState<boolean>(false)

  const appointmentsByHour = useMemo(() => {
    if (!schedule) return null

    // Create a map where keys are hours and values are arrays of appointments
    const hourAppointments = new Map<string, Array<Appointment>>()

    schedule.forEach((appt: Appointment) => {
      const hour = appt.start_time.getHours().toString()
      const existingAppts = hourAppointments.get(hour) || []
      hourAppointments.set(hour, [...existingAppts, appt])
    })

    // Convert the map to array of objects with hour and appointments
    return Array.from(hourAppointments.entries()).map(
      ([hour, appointments]) => ({
        hour,
        appointments,
      })
    )
  }, [schedule])

  const nonDummyByHour: Array<HourCount> | null = useMemo(() => {
    if (!schedule) return null

    const hourCounts = new Map<string, number>()
    schedule
      .filter((appointment) => appointment.first_name !== "Dummy")
      .forEach((appointment) => {
        const hour = appointment.start_time.getHours().toString()
        const existingCount = hourCounts.get(hour) || 0
        hourCounts.set(hour, existingCount + 1)
      })

    return Array.from(hourCounts.entries()).map(([hour, count]) => ({
      hour,
      count,
    }))
  }, [schedule])

  const fetchScheduleData = async () => {
    try {
      setIsLoading(true)
      const scheduleData = await getSchedule()
      // Parse date strings into Date objects
      const parsedSchedule = scheduleData.map((appointment: Appointment) => ({
        ...appointment,
        start_time: new Date(appointment.start_time),
        acuity_created_at: new Date(appointment.acuity_created_at),
        acuity_deleted_at: appointment.acuity_deleted_at
          ? new Date(appointment.acuity_deleted_at)
          : null,
        created_at_here: new Date(appointment.created_at_here),
        last_modified_here: new Date(appointment.last_modified_here),
      }))
      console.log(`found ${parsedSchedule.length} appts`)
      setSchedule(parsedSchedule)
    } catch (error) {
      console.error("Error fetching schedule:", error)
    } finally {
      setIsLoading(false)
    }
  }

  // const handleTakeSnapshot = async () => {
  //   try {
  //     setIsLoading(true)
  //     const message = await takeSnapshot()
  //     console.log(message)
  //   } catch (error) {
  //     console.error("Error taking snapshot", error)
  //   } finally {
  //     setIsLoading(false)
  //   }
  // }

  useEffect(() => {
    const fetchDiff = async () => {
      try {
        const diffData = await getScheduleDiff()
        setScheduleDiff(diffData)
      } catch (error) {
        console.error("Error fetching diff:", error)
      }
    }

    // Initial fetch
    fetchDiff()

    // Set up polling every 120 seconds
    const pollInterval = setInterval(fetchDiff, 120 * 1000)

    // Cleanup on unmount
    return () => clearInterval(pollInterval)
  }, [])

  useEffect(() => {
    fetchScheduleData()
  }, [])

  return (
    <div className="min-h-screen p-8 font-[family-name:var(--font-geist-sans)]">
      <main className="max-w-4xl mx-auto">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-2xl font-bold">Acuity Augmented</h1>
          <p>Aurora Mathnasium</p>

          <div className="flex gap-2">
            {/* <Button
              onClick={handleTakeSnapshot}
              variant="outline"
              disabled={isLoading}
            >
              {isLoading ? "Processing..." : "Take Snapshot"}
            </Button>
            <Button
              className="bg-blue-500 text-white hover:bg-blue-600 transition-colors"
              onClick={fetchScheduleData}
              disabled={isLoading}
            >
              {isLoading ? "Loading..." : "Fetch Schedule"}
            </Button> */}
            <Button
              onClick={() => logout()}
              variant="outline"
              className="text-amber-500 hover:text-amber-600 transition-colors"
            >
              Logout
            </Button>
          </div>
        </div>
        {dayOfWeek === 6 && (
          <p className="my-8">
            The center is closed today, so these are blank.
          </p>
        )}
        {wasSnapshotTaken() ? (
          <>
            <DiffTable scheduleDiff={scheduleDiff} />
            <AppointmentsTable
              appointmentsByHour={appointmentsByHour}
              nonDummyByHour={nonDummyByHour}
            />
          </>
        ) : (
          <>
            <Alert className="my-8">
              <Clock className="mt-1 h-8 w-8" />
              <AlertTitle>Center isn&apos;t open yet.</AlertTitle>
              <AlertDescription>
                Data will populate 30 minutes before the center opens.
              </AlertDescription>
            </Alert>
            <DiffTable scheduleDiff={null} />
            <AppointmentsTable
              appointmentsByHour={null}
              nonDummyByHour={null}
            />
          </>
        )}
      </main>
    </div>
  )
}
