"use client"

import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
  DialogDescription,
} from "@/components/ui/dialog"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { useEffect, useState } from "react"
import { getDummyOpenings } from "@/lib/api-actions"

interface CreateDummyModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
}

export default function CreateDummyModal({
  open,
  onOpenChange,
}: CreateDummyModalProps) {
  const [selectedHour, setSelectedHour] = useState<string>("")
  const [numDummyToCreate, setNumDummyToCreate] = useState<number>(4)
  const [availableHours, setAvailableHours] = useState<
    Array<{
      value: string
      label: string
      openings: number
    }>
  >([])
  const [isLoading, setIsLoading] = useState(false)

  useEffect(() => {
    if (open) {
      setIsLoading(true)
      getDummyOpenings()
        .then((data) => {
          // Transform the API response into our hour format
          const hours = data.map((slot: any) => {
            const date = new Date(slot.time)
            const hour = date.getHours()
            const displayHour = hour > 12 ? hour - 12 : hour
            return {
              value: hour.toString(),
              label: `${displayHour}:00 ${hour >= 12 ? "PM" : "AM"}`,
              openings: slot.slotsAvailable || 0,
            }
          })
          setAvailableHours(hours)
        })
        .catch((error) => {
          console.error("Failed to fetch dummy openings:", error)
          setAvailableHours([])
        })
        .finally(() => {
          setIsLoading(false)
        })
    }
  }, [open])

  useEffect(() => {
    setNumDummyToCreate(
      Math.min(
        4,
        availableHours.find((h) => h.value === selectedHour)?.openings || 0
      )
    )
  }, [selectedHour, availableHours])

  const handleConfirm = () => {
    // TODO: Implement dummy appointment creation
    onOpenChange(false)
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent
        style={{
          position: "fixed",
          top: "50%",
          left: "50%",
          transform: "translate(-50%, -50%)",
        }}
      >
        <DialogHeader>
          <DialogTitle>Add Dummy Appointments</DialogTitle>
          <DialogDescription>
            Create dummy appointments to block the schedule.
          </DialogDescription>
        </DialogHeader>

        <div>
          {availableHours.length > 0 ? (
            <>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Hour</TableHead>
                    <TableHead className="text-center">Openings</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {availableHours.map((hour) => (
                    <TableRow key={hour.value}>
                      <TableCell>{hour.label}</TableCell>
                      <TableCell className="text-center">
                        {hour.openings}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>

              <div className="grid gap-2 mt-4">
                <label htmlFor="hour" className="text-sm font-medium">
                  Select Hour
                </label>
                <Select value={selectedHour} onValueChange={setSelectedHour}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select an hour" />
                  </SelectTrigger>
                  <SelectContent>
                    {availableHours.map((hour) => (
                      <SelectItem key={hour.value} value={hour.value}>
                        {hour.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </>
          ) : (
            <p>No openings today.</p>
          )}

          {selectedHour && (
            <div className="rounded-md bg-muted p-4 mt-4">
              <p>
                <strong>{numDummyToCreate}</strong> dummy appointments will be
                created for{" "}
                <strong>
                  {availableHours.find((h) => h.value === selectedHour)?.label}
                </strong>
              </p>
            </div>
          )}
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          <Button
            onClick={handleConfirm}
            disabled={!selectedHour}
            className="bg-blue-500 hover:bg-blue-600 text-white"
          >
            Create Appointments
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
