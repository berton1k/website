const SETTINGS = [
  { key: "nickname", label: "Никнейм" },
  { key: "activity", label: "Полоска активности" },
  { key: "score", label: "Очки" },
  { key: "messages", label: "Сообщения" },
  { key: "reactions", label: "Реакции" },
  { key: "replies", label: "Ответы" },
  { key: "voice", label: "Время в голосовом канале" },
  { key: "factions", label: "Курируемые фракции" }
];

function isEnabled(key) {
  return localStorage.getItem("s_" + key) !== "off";
}

function setEnabled(key, value) {
  localStorage.setItem("s_" + key, value ? "on" : "off");
}
