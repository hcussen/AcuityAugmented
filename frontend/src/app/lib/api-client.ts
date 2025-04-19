interface SimpleAppointment {
  id: number
  first_name: string
  last_name: string
}

interface HourlyDiff {
  hour: string
  added: SimpleAppointment[]
  deleted: SimpleAppointment[]
}

interface ScheduleDiffResponse {
  differences: HourlyDiff[]
}

export class ApiClient {
  private baseUrl: string

  constructor(baseUrl: string = "http://localhost:8000") {
    this.baseUrl = baseUrl
  }

  async getScheduleDiff(): Promise<ScheduleDiffResponse> {
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
}

// Export a default instance
export const apiClient = new ApiClient()
