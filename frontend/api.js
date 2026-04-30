const API = "http://localhost:8000"

export const getSignals = (filter) =>
  fetch(`${API}/api/signals${filter ? `?sentiment=${filter}` : ""}`).then(r => r.json())

export const getSignal = (id) =>
  fetch(`${API}/api/signals/${id}`).then(r => r.json())

export const getEntities = () =>
  fetch(`${API}/api/entities`).then(r => r.json())

export const getRegions = () =>
  fetch(`${API}/api/regions`).then(r => r.json())

export const refreshSignals = () =>
  fetch(`${API}/api/signals/refresh`, { method: "POST" }).then(r => r.json())
