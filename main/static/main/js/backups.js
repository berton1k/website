document.addEventListener("DOMContentLoaded", () => {
  let selectedServerId = null
  let selectedBackupId = null

  const serverSelect = document.getElementById("backupServerSelect")
  const serverHead = serverSelect.querySelector(".select-head")
  const serverValue = serverSelect.querySelector(".value-text")
  const serverDropdown = serverSelect.querySelector(".select-dropdown")

  const backupSelect = document.getElementById("backupSelect")
  const backupHead = backupSelect.querySelector(".select-head")
  const backupValue = backupSelect.querySelector(".value-text")
  const backupDropdown = backupSelect.querySelector(".select-dropdown")

  serverHead.onclick = e => {
    e.stopPropagation()
    serverSelect.classList.toggle("open")
    backupSelect.classList.remove("open")
  }

  backupHead.onclick = e => {
    e.stopPropagation()
    backupSelect.classList.toggle("open")
    serverSelect.classList.remove("open")
  }

  document.addEventListener("click", () => {
    serverSelect.classList.remove("open")
    backupSelect.classList.remove("open")
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
        loadBackups()
      }

      serverDropdown.appendChild(el)
    })
  }

  async function loadBackups() {
    backupDropdown.innerHTML = `<div class="select-option">Загрузка...</div>`

    const res = await fetch(`/api/backups/?server_id=${selectedServerId}`)
    const data = await res.json()

    backupDropdown.innerHTML = ""

    if (!data.backups.length) {
      backupDropdown.innerHTML = `<div class="select-option">Бэкапов нет</div>`
      return
    }

    data.backups.forEach(b => {
      const el = document.createElement("div")
      el.className = "select-option"
      el.textContent = new Date(b.created_at).toLocaleString()

      el.onclick = () => {
        selectedBackupId = b.backup_id
        backupValue.textContent = el.textContent
        backupSelect.classList.remove("open")
      }

      backupDropdown.appendChild(el)
    })
  }

  window.createBackup = async () => {
    const res = await fetch("/api/backup/create/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ server_id: String(selectedServerId) })
    })

    if (!res.ok) {
      toast("Ошибка создания бэкапа", "error")
      return
    }

    toast("Бэкап создан", "success")
    loadBackups()
  }

 window.restoreBackup = async () => {
  const res = await fetch("/api/backup/restore/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      backup_id: selectedBackupId,
      server_id: String(selectedServerId)
    })
  });

  if (res.status === 409) {
    toast("⚠ Бэкап уже загружается", "warn");
    return;
  }

  if (!res.ok) {
    const t = await res.text();
    toast("❌ Ошибка: " + t, "error");
    return;
  }

  toast("⏳ Восстановление запущено", "info");

  await waitForBackupFinish(String(selectedServerId));

  toast("✅ Восстановление завершено", "success");
}
async function waitForBackupFinish(serverId, timeout = 300000, interval = 5000) {
  const start = Date.now();

  while (true) {
    const res = await fetch("/api/backup/status/");
    const data = await res.json();

    if (data.finished) return;

    if (Date.now() - start > timeout) {
      toast("⚠ Время ожидания восстановления истекло", "warn");
      throw new Error("Restore timeout");
    }

    await new Promise(res => setTimeout(res, interval));
  }
}

  loadServers()
})
