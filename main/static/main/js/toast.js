function toast(text, type = "info") {
  const t = document.createElement("div")
  t.className = `toast ${type}`
  t.textContent = text
  document.body.appendChild(t)

  setTimeout(() => t.classList.add("show"), 10)
  setTimeout(() => {
    t.classList.remove("show")
    setTimeout(() => t.remove(), 300)
  }, 3200)
}

(function injectToastStyles() {
  if (document.getElementById("toast-style")) return
  const style = document.createElement("style")
  style.id = "toast-style"
  style.textContent = `
.toast {
  
}

`
  document.head.appendChild(style)
})()
