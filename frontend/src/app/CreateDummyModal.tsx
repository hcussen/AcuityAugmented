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
import { getDummyOpenings, createDummyAppointments } from "@/lib/api-actions"
import { Loader } from "@/components/ui/loader"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Check } from "lucide-react"

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
  const [isLoading, setIsLoading] = useState<boolean>(false)
  const [isCreating, setIsCreating] = useState<boolean>(false)
  const [error, setError] = useState<string | null>(null)
  const [isSuccess, setIsSuccess] = useState<boolean>(false)

  useEffect(() => {
    // reset states whenever open state changes
    setIsCreating(false)
    setError(null)
    setIsSuccess(false)
    setSelectedHour("")

    // if open, fetch data
    if (open) {
      setIsLoading(true)
      const fetchData = async () => {
        try {
          const data = await getDummyOpenings()
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
        } catch (error) {
          console.error("Failed to fetch dummy openings:", error)
          setAvailableHours([])
        } finally {
          setIsLoading(false)
        }
      }
      fetchData()
    }
  }, [open])

  useEffect(() => {
    setNumDummyToCreate(
      Math.min(
        4,
        availableHours.find((h) => h.value === selectedHour)?.openings || 0
      )
    )
    console.log(selectedHour)
  }, [selectedHour, availableHours])

  const handleConfirm = async () => {
    setIsCreating(true)
    setError(null) // Clear any previous errors
    setIsSuccess(false) // Clear any previous success state
    const today = new Date(2025, 4, 27)
    try {
      const res = await createDummyAppointments(
        numDummyToCreate,
        new Date(
          today.getFullYear(),
          today.getMonth(),
          today.getDate(),
          parseInt(selectedHour),
          0,
          0
        )
      )
      console.log(res)
      setIsSuccess(true)
      // setTimeout(() => {
      //   onOpenChange(false)
      // }, 1500) // Give user time to see success message
    } catch (error) {
      console.error("Failed to create dummy appointments:", error)
      setError("Failed to create appointments.")
    } finally {
      setIsCreating(false)
    }
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
        <div>
          <DialogHeader>
            <DialogTitle>Add Dummy Appointments</DialogTitle>
            <DialogDescription>
              Create 4 dummy appointments at a time to block the schedule. If
              there are less than 4 slots available, only that many will be
              created.
            </DialogDescription>
          </DialogHeader>

          {isLoading ? (
            <div className="flex justify-center items-center min-h-[100px]">
              <Loader size="lg" />
            </div>
          ) : (
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
                    <Select
                      value={selectedHour}
                      onValueChange={setSelectedHour}
                    >
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
                <p className="text-center py-8">No openings today.</p>
              )}

              {selectedHour && (
                <div className="rounded-md bg-muted p-4 mt-4">
                  <p>
                    <strong>{numDummyToCreate}</strong> dummy appointments will
                    be created for{" "}
                    <strong>
                      {
                        availableHours.find((h) => h.value === selectedHour)
                          ?.label
                      }
                    </strong>
                  </p>
                </div>
              )}
            </div>
          )}
        </div>

        <DialogFooter>
          <Button
            disabled={isCreating}
            variant="outline"
            onClick={() => onOpenChange(false)}
          >
            Cancel
          </Button>

          <Button
            onClick={handleConfirm}
            disabled={!selectedHour || isCreating || isSuccess}
            className="bg-blue-500 hover:bg-blue-600 text-white"
          >
            {isCreating && <Loader size="sm" />}
            {isCreating ? "Creating..." : "Create Appointments"}
          </Button>
        </DialogFooter>
        {error && (
          <Alert variant="destructive" className="w-full mt-4">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}
        {isSuccess && (
          <Alert
            className="w-full mt-4 flex items-center border-emerald-500"
            variant="default"
          >
            <Check className="h-6 w-6" color="green" />
            <AlertDescription>
              Successfully created appointments!
            </AlertDescription>
          </Alert>
        )}
      </DialogContent>
    </Dialog>
  )
}
