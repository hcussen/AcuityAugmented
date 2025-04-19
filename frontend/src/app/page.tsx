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

  useEffect(() => {
    const fetchDiff = async () => {
      try {
        const data = await apiClient.getScheduleDiff()
        setScheduleDiff(data)
      } catch (error) {
        console.error("Error fetching schedule diff:", error)
      }
    }

    fetchDiff()
  }, [])

  return (
    <div className="min-h-screen p-8 font-[family-name:var(--font-geist-sans)]">
      <main className="max-w-4xl mx-auto">
        <h1 className="text-2xl font-bold mb-6">Today's Schedule Changes</h1>
        <pre>{JSON.stringify(scheduleDiff, null, 2)}</pre>
        <Table>
          <TableCaption>A list of your recent invoices.</TableCaption>
          <TableHeader>
            <TableRow>
              <TableHead className="w-[100px]">Hour</TableHead>
              <TableHead>
                <PlusCircle className="w-5 h-5" /> Additions
              </TableHead>
              <TableHead>
                <MinusCircle className="w-5 h-5" /> Cancellations
              </TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {scheduleDiff?.map((diff) => (
              <TableRow key={diff.hour}>
                <TableCell className="font-medium">{diff.hour}</TableCell>
                <TableCell>
                  {diff.added.length > 0 && (
                    <div className="flex items-center gap-2">
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
                    <div className="flex items-center gap-2">
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
