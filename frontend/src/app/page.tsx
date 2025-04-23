"use client"

import { useEffect, useState } from "react"
import { HourlyDiff } from "@/lib/types"
import { apiClient } from "@/lib/api-client"
import { PlusCircle, MinusCircle } from "lucide-react"
import {
  Table,
  TableBody,
  TableCaption,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"

export default function Home() {
  const [scheduleDiff, setScheduleDiff] = useState<Array<HourlyDiff> | null>(
    null
  )
  const [schedule, setSchedule] = useState<any>(null)

  const fetchSchedule = async () => {
    try {
      const scheduleData = await apiClient.getSchedule()
      setSchedule(scheduleData)
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
      </main>
    </div>
  )
}
