"use client"

import { Button } from "@/components/ui/button"
import { Plus } from "lucide-react"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"

interface CreateDummyModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
}

export default function CreateDummyModal({
  open,
  onOpenChange,
}: CreateDummyModalProps) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogTrigger asChild>
        <Button
          variant="outline"
          className="mt-4 bg-blue-500 hover:bg-blue-600 text-white"
        >
          <Plus className="mr-2 h-4 w-4" />
          Add Dummy Appointments
        </Button>
      </DialogTrigger>
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
        </DialogHeader>
      </DialogContent>
    </Dialog>
  )
}
