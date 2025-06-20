"use server"
type Method = "GET" | "POST" | "PUT" | "PATCH"

/**
 * A utility function to make API requests with a specified HTTP method and endpoint.
 *
 * @param endpoint - The API endpoint to send the request to, relative to the base URL. Without leading slash.
 * @param verb - The HTTP method to use for the request (e.g., "GET", "POST", "PUT", "DELETE").
 * @returns A promise that resolves to the parsed JSON response from the API.
 * @throws An error if the response status is not OK (status code outside the range 200-299).
 *
 * @remarks
 * - The base URL for the API is determined by the `API_BASE_URL` environment variable.
 *   If not set, it defaults to `http://localhost:8000`.
 * - The `X-API-Key` header is included in the request, using the value of the `API_KEY`
 *   environment variable, or an empty string if not set.
 */
async function apiWrapper(
  endpoint: string,
  verb: Method,
  queryParams?: Record<string, string | number | boolean>
): Promise<Response> {
  const baseUrl =
    process.env.NODE_ENV === "production"
      ? process.env.API_BASE_URL
      : "http://localhost:8000"

  let url = `${baseUrl}/${endpoint}`

  if (queryParams && Object.keys(queryParams).length > 0) {
    const params = new URLSearchParams()
    for (const [key, value] of Object.entries(queryParams)) {
      params.append(key, String(value))
    }
    url += `?${params.toString()}`
  }

  const response = await fetch(url, {
    method: verb,
    headers: {
      "Content-Type": "application/json",
      "X-API-Key": process.env.API_KEY || "",
    },
  })

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`)
  }

  return response
}

export async function getScheduleDiff() {
  try {
    const response = await apiWrapper("schedule/diff", "GET")
    return await response.json()
  } catch (error) {
    console.error("Error fetching schedule diff:", error)
    throw error
  }
}

export async function getSchedule() {
  try {
    const response = await apiWrapper("schedule", "GET")
    return await response.json()
  } catch (error) {
    console.error("Error fetching schedule:", error)
    throw error
  }
}

export async function takeSnapshot() {
  try {
    const response = await apiWrapper("acuity/snaphot", "POST")
    return await response.json()
  } catch (error) {
    console.error("Error taking snapshot:", error)
    throw error
  }
}

export type Openings = {
  time: string
  slotsAvailable: number
}

export async function getDummyOpenings(): Promise<Openings[]> {
  try {
    const response = await apiWrapper("acuity/openings/dummy", "GET", {
      // date: "2025-05-27",
      today: true,
    })
    return await response.json()
  } catch (error) {
    console.error("Error fetching dummy openings:", error)
    throw error
  }
}

export async function createDummyAppointments(num: number, datetime: Date) {
  try {
    const response = await apiWrapper("acuity/openings/dummy", "POST", {
      date_time: datetime.toISOString(),
      num_appointments: num,
    })
    return await response.json()
  } catch (error) {
    console.error("Error creating dummy openings:", error)
    throw error
  }
}
