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

export type HourAppointments = {
  hour: string
  appointments: SimpleAppointment[]
}

export type HourCount = {
  hour: string
  count: number
}

export enum EventAction {
  Schedule = "schedule",
  RescheduleIncoming = "reschedule_incoming",
  RescheduleSameDay = "reschedule_same_day",
  RescheduleOutgoing = "reschedule_outgoing",
  Cancel = "cancel",
}

export interface Event {
  id: string // UUID in string format
  action: EventAction
  created_at: Date // ISO datetime string
  old_time: Date | null // ISO datetime string
  new_time: Date | null // ISO datetime string
  appointment_id: string // UUID in string format
  appointment?: Appointment // Optional since we might not always include the related appointment
}

export interface Appointment {
  id: string // UUID in string format
  acuity_id: number
  first_name: string
  last_name: string
  start_time: Date // ISO datetime string
  duration: number
  acuity_created_at: Date // ISO datetime string
  acuity_deleted_at: Date | null // ISO datetime string
  is_canceled: boolean | null
  created_at_here: Date // ISO datetime string
  last_modified_here: Date // ISO datetime string
  events?: Event[] // Optional since we might not always include related events
}
