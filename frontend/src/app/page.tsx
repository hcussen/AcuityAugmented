"use client"

import { useEffect, useState } from "react"
import { HourlyDiff } from "@/lib/types"
import { apiClient } from "@/lib/api-client"
import { PlusCircle, MinusCircle } from "lucide-react"

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
        <div className="border rounded-lg overflow-hidden">
          <table className="w-full">
            <thead>
              <tr className="bg-gray-50 dark:bg-gray-800">
                <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900 dark:text-gray-100">
                  Hour
                </th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-green-600 dark:text-green-400">
                  <div className="flex items-center gap-2">
                    <PlusCircle className="w-5 h-5" />
                    Additions
                  </div>
                </th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-red-600 dark:text-red-400">
                  <div className="flex items-center gap-2">
                    <MinusCircle className="w-5 h-5" />
                    Subtractions
                  </div>
                </th>
              </tr>
            </thead>
          </table>
        </div>
      </main>
    </div>
  )
}
