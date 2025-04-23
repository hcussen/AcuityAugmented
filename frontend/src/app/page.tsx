"use client"

import { useEffect, useState, useMemo } from "react"
import { HourlyDiff, Appointment } from "@/lib/types"
import { apiClient } from "@/lib/api-client"
import { PlusCircle, MinusCircle } from "lucide-react"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"

export default function Home() {
  const [scheduleDiff, setScheduleDiff] = useState<Array<HourlyDiff> | null>(
    null
  )
  const [schedule, setSchedule] = useState<Appointment[] | null>(null)

  const appointmentsByHour = useMemo(() => {
    if (!schedule) return null

    const hourCounts = new Map<string, number>()
    schedule.forEach((appointment) => {
      const hour = appointment.start_time.getHours().toString()
      const existingCount = hourCounts.get(hour) || 0
      hourCounts.set(hour, existingCount + 1)
    })

    return Array.from(hourCounts.entries()).map(([hour, count]) => ({
      hour,
      count,
    }))
  }, [schedule])

  const nonDummyByHour = useMemo(() => {
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

  const fetchSchedule = async () => {
    try {
      const scheduleData = await apiClient.getSchedule()
      // Parse date strings into Date objects
      const parsedSchedule = scheduleData.map((appointment) => ({
        ...appointment,
        start_time: new Date(appointment.start_time),
        acuity_created_at: new Date(appointment.acuity_created_at),
        acuity_deleted_at: appointment.acuity_deleted_at
          ? new Date(appointment.acuity_deleted_at)
          : null,
        created_at_here: new Date(appointment.created_at_here),
        last_modified_here: new Date(appointment.last_modified_here),
      }))
      setSchedule(parsedSchedule)
    } catch (error) {
      console.error("Error fetching schedule:", error)
    }
  }

  useEffect(() => {
    const fetchDiff = async () => {
      try {
        const diffData = await apiClient.getScheduleDiff()
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
    console.log(appointmentsByHour)
    console.log(nonDummyByHour)
  }, [schedule])

  return (
    <div className="min-h-screen p-8 font-[family-name:var(--font-geist-sans)]">
      <main className="max-w-4xl mx-auto">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-2xl font-bold">Today's Schedule Changes</h1>
          <button
            onClick={fetchSchedule}
            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
          >
            Fetch Schedule
          </button>
        </div>
        <div className="space-y-8">
          <div>
            <h2 className="text-xl font-semibold mb-4">Schedule Changes</h2>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-[100px]">Hour</TableHead>
                  <TableHead>
                    <div className="flex items-center gap-2">
                      <PlusCircle className="w-5 h-5" />
                      <span>Additions</span>
                    </div>
                  </TableHead>
                  <TableHead>
                    <div className="flex items-center gap-2">
                      <MinusCircle className="w-5 h-5" />
                      <span>Cancellations</span>
                    </div>
                  </TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {scheduleDiff &&
                  scheduleDiff.length > 0 &&
                  scheduleDiff.map((diff) => (
                    <TableRow key={diff.hour}>
                      <TableCell className="font-medium">{diff.hour}</TableCell>
                      <TableCell>
                        {diff.added.length > 0 && (
                          <div>
                            {diff.added.map((appointment) => (
                              <div key={appointment.id}>
                                {appointment.first_name} {appointment.last_name}
                              </div>
                            ))}
                          </div>
                        )}
                      </TableCell>
                      <TableCell>
                        {diff.deleted.length > 0 && (
                          <div>
                            {diff.deleted.map((appointment) => (
                              <div key={appointment.id}>
                                {appointment.first_name} {appointment.last_name}
                              </div>
                            ))}
                          </div>
                        )}
                      </TableCell>
                    </TableRow>
                  ))}
              </TableBody>
            </Table>
          </div>

          <div>
            <h2 className="text-xl font-semibold mb-4">
              Appointments per Hour
            </h2>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Hour</TableHead>
                  <TableHead>Count</TableHead>
                  <TableHead>Non-Dummy Count</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {appointmentsByHour?.map((hourData, idx) => (
                  <TableRow key={hourData.hour}>
                    <TableCell className="font-medium">
                      {hourData.hour}
                    </TableCell>
                    <TableCell>{hourData.count}</TableCell>
                    <TableCell>{nonDummyByHour[idx].count}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </div>
      </main>
    </div>
  )
}
