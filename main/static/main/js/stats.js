document.addEventListener("DOMContentLoaded", loadStats)

async function loadStats() {
  try {
    const res = await fetch("/api/stats/")
    if (!res.ok) throw new Error()
    const data = await res.json()

    document.getElementById("stat-servers").textContent = data.servers
    document.getElementById("stat-channels").textContent = data.channels
    document.getElementById("stat-roles").textContent = data.roles
  } catch {
    toast("Ошибка загрузки статистики", "error")
  }
}
