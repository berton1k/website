document.addEventListener("DOMContentLoaded", () => {
  let selectedServerId = null

  const serverSelect = document.getElementById("clearServerSelect")
  const serverHead = serverSelect.querySelector(".select-head")
  const serverValue = serverSelect.querySelector(".value-text")
  const serverDropdown = serverSelect.querySelector(".select-dropdown")

  serverHead.onclick = e => {
    e.stopPropagation()
    serverSelect.classList.toggle("open")
  }

  document.addEventListener("click", () => {
    serverSelect.classList.remove("open")
  })

  async function loadServers() {
    serverDropdown.innerHTML = `<div class="select-option">Загрузка...</div>`

    const res = await fetch("/api/servers/")
    const data = await res.json()

    serverDropdown.innerHTML = ""

    data.servers.forEach(s => {
      const el = document.createElement("div")
      el.className = "select-option"
      el.textContent = s.name

      el.onclick = () => {
        selectedServerId = String(s.discord_id)
        serverValue.textContent = s.name
        serverSelect.classList.remove("open")
      }

      serverDropdown.appendChild(el)
    })
  }

  window.clearServer = async () => {
    if (!selectedServerId) {
      toast("❗ Выберите сервер", "warn")
      return
    }

    toast("⏳ Проверка условий...", "info")

    const res = await fetch("/api/clear/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ guild_id: selectedServerId })
    })

    const data = await res.json()

    if (data.blocked) {
      toast("⛔ Этот сервер нельзя очистить", "error")
      return
    }

    if (data.leader_exists) {
      toast("⚠ Есть активный лидер", "warn")
      return
    }

    if (data.error) {
      toast("❌ Ошибка очистки", "error")
      return
    }

    toast("🔥 Очистка сервера началась", "success")

    setTimeout(() => {
      toast("✅ Очистка сервера завершена", "success")
    }, 4000)
  }

  loadServers()
})
