import { SimpleAppointment, HourlyDiff } from "./types"

export class ApiClient {
  private baseUrl: string

  constructor(baseUrl: string = "http://localhost:8000") {
    this.baseUrl = baseUrl
  }

  async getScheduleDiff(): Promise<HourlyDiff[]> {
    try {
      const response = await fetch(`${this.baseUrl}/schedule/diff`, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      return await response.json()
    } catch (error) {
      console.error("Error fetching schedule diff:", error)
      throw error
    }
  }

  async getSchedule(): Promise<SimpleAppointment[]> {
    try {
      const response = await fetch(`${this.baseUrl}/schedule`, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      return await response.json()
    } catch (error) {
      console.error("Error fetching schedule:", error)
      throw error
    }
  }
}

// Export a default instance
export const apiClient = new ApiClient()
