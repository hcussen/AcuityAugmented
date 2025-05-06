import { PlusCircle, MinusCircle } from "lucide-react"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { HourlyDiff } from "@/lib/types"

export default function DiffTable({
  scheduleDiff,
}: {
  scheduleDiff: HourlyDiff[] | null
}) {
  return (
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
    </div>
  )
}
