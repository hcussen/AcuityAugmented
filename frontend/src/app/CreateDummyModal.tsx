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

  useEffect(() => {
    setNumDummyToCreate(
      Math.min(
        4,
        availableHours.find((h) => h.value === selectedHour)?.openings || 0
      )
    )
  }, [selectedHour])

  // Generate available hours (4pm to 7pm)
  const availableHours = Array.from({ length: 4 }, (_, i) => {
    const hour = i + 16 // 16 is 4pm in 24-hour format
    const displayHour = hour > 12 ? hour - 12 : hour
    return {
      value: hour.toString(),
      label: `${displayHour}:00 PM`,
      appointments: 11, // Dummy data
      openings: 3, // Dummy data
    }
  })

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
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Hour</TableHead>
                <TableHead className="text-right">Real Appointments</TableHead>
                <TableHead className="text-right">Openings</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {availableHours.map((hour) => (
                <TableRow key={hour.value}>
                  <TableCell>{hour.label}</TableCell>
                  <TableCell className="text-center">
                    {hour.appointments}
                  </TableCell>
                  <TableCell className="text-center">{hour.openings}</TableCell>
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

          {selectedHour && (
            <div className="rounded-md bg-muted p-4 mt-4">
              {/* <h4 className="text-sm font-medium mb-2">Preview</h4> */}
              <p>
                <strong>{numDummyToCreate}</strong> dummy appointments will be
                created for{" "}
                <strong>
                  {availableHours.find((h) => h.value === selectedHour)?.label}
                </strong>
              </p>
              {/* <ul className="text-sm space-y-1">
                <li>4 dummy appointments will be created</li>
                <li>
                  Scheduled for{" "}
                  {availableHours.find((h) => h.value === selectedHour)?.label}
                </li>
              </ul> */}
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
