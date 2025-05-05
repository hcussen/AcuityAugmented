"use server"

// Create standalone server functions that don't rely on the API client class
export async function getScheduleDiff() {
  try {
    const baseUrl = process.env.API_BASE_URL || "http://localhost:8000"
    const response = await fetch(`${baseUrl}/schedule/diff`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        "X-API-Key": process.env.API_KEY || "",
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

export async function getSchedule() {
  try {
    const baseUrl = process.env.API_BASE_URL || "http://localhost:8000"
    const response = await fetch(`${baseUrl}/schedule`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        "X-API-Key": process.env.API_KEY || "",
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

export async function takeSnapshot() {
  try {
    const baseUrl = process.env.API_BASE_URL || "http://localhost:8000"
    const response = await fetch(`${baseUrl}/acuity/snapshot`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-API-Key": process.env.API_KEY || "",
      },
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    return await response.json()
  } catch (error) {
    console.error("Error taking snapshot:", error)
    throw error
  }
}
