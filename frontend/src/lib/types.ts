export interface SimpleAppointment {
  id: number
  first_name: string
  last_name: string
}

export interface HourlyDiff {
  hour: string
  added: SimpleAppointment[]
  deleted: SimpleAppointment[]
}
