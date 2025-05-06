import { HourAppointments, HourCount } from "@/lib/types"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"

export default function AppointmentsTable({
  appointmentsByHour,
  nonDummyByHour,
}: {
  appointmentsByHour: HourAppointments[] | null
  nonDummyByHour: HourCount[] | null
}) {
  return (
    <div className="my-8">
      <h2 className="text-xl font-semibold mb-4">Appointments at 3:30pm</h2>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Hour</TableHead>
            <TableHead>Names</TableHead>
            <TableHead>Count</TableHead>
            <TableHead>Non-Dummy Count</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {appointmentsByHour?.map((hourData) => (
            <TableRow key={hourData.hour}>
              <TableCell className="font-medium">{hourData.hour}</TableCell>
              <TableCell>
                {hourData.appointments.map((appt) => (
                  <p key={appt.id}>
                    {appt.first_name} {appt.last_name}
                  </p>
                ))}
              </TableCell>
              <TableCell>{hourData.appointments.length}</TableCell>
              <TableCell>
                {(nonDummyByHour &&
                  nonDummyByHour.find((item) => item.hour === hourData.hour)
                    ?.count) ||
                  0}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  )
}
