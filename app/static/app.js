/* Dùng chung cho trang đăng nhập và 3 trang quản trị. Không cần framework/build. */
const ROLE_PAGES = { admin: "/admin", restaurant: "/restaurant", shipper: "/shipper" };
const ROLE_LABELS = {
  admin: "Quản trị",
  customer: "Khách hàng",
  restaurant: "Nhà hàng",
  shipper: "Shipper",
};
const STATUS_LABELS = {
  pending: "Chờ duyệt",
  confirmed: "Đã xác nhận",
  shipping: "Đang giao",
  completed: "Hoàn thành",
  cancelled: "Đã huỷ",
};

function getToken() {
  return localStorage.getItem("token");
}

function getSessionUser() {
  try {
    return JSON.parse(localStorage.getItem("user") || "null");
  } catch {
    return null;
  }
}

function saveSession(data) {
  localStorage.setItem("token", data.access_token);
  localStorage.setItem("user", JSON.stringify(data.user));
}

function clearSession() {
  localStorage.removeItem("token");
  localStorage.removeItem("user");
}

function logout() {
  clearSession();
  location.href = "/login";
}

/* Gọi API. Tự gắn token, tự chuyển về /login khi hết phiên. */
async function api(path, options = {}) {
  const headers = { "Content-Type": "application/json", ...(options.headers || {}) };
  const token = getToken();
  if (token) headers.Authorization = "Bearer " + token;

  const res = await fetch("/api" + path, { ...options, headers });
  if (res.status === 401) {
    clearSession();
    location.replace("/login");
    throw new Error("Phiên đăng nhập đã hết hạn");
  }
  const data = res.status === 204 ? null : await res.json().catch(() => null);
  if (!res.ok) {
    const detail = data && data.detail;
    throw new Error(typeof detail === "string" ? detail : "Có lỗi xảy ra, thử lại sau");
  }
  return data;
}

/* Kiểm tra đăng nhập + vai trò trước khi tải trang. Sai vai trò -> chuyển trang phù hợp. */
function requireRole(role) {
  const user = getSessionUser();
  if (!getToken() || !user) {
    location.replace("/login");
    return null;
  }
  if (user.role !== role && !(role === "admin" && user.is_admin)) {
    location.replace(ROLE_PAGES[user.role] || "/login");
    return null;
  }
  const nameEl = document.querySelector("[data-user-name]");
  if (nameEl) nameEl.textContent = user.full_name || user.username;
  const avatarEl = document.querySelector("[data-user-avatar]");
  if (avatarEl) {
    avatarEl.textContent = (user.full_name || user.username).trim().charAt(0).toUpperCase();
  }
  const roleEl = document.querySelector("[data-user-role]");
  if (roleEl) roleEl.textContent = ROLE_LABELS[user.role] || user.role;

  const logoutBtn = document.querySelector("[data-logout]");
  if (logoutBtn) logoutBtn.addEventListener("click", logout);
  return user;
}

function money(value) {
  return Number(value || 0).toLocaleString("vi-VN") + "đ";
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function formatDate(value) {
  if (!value) return "";
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return value;
  return d.toLocaleString("vi-VN", { hour: "2-digit", minute: "2-digit", day: "2-digit", month: "2-digit" });
}

function statusBadge(status) {
  return `<span class="badge badge-${escapeHtml(status)}">${escapeHtml(STATUS_LABELS[status] || status)}</span>`;
}

function orderItemsHtml(order) {
  const lines = (order.items || [])
    .map(
      (line) =>
        `<div class="line"><span>${escapeHtml(line.item_name)} <span class="muted">×${line.quantity}</span></span>` +
        `<span class="muted">${money(line.subtotal)}</span></div>`
    )
    .join("");
  const note = order.note
    ? `<div class="note">📝 ${escapeHtml(order.note)}</div>`
    : "";
  return `<div class="items">${lines}${note}</div>`;
}

function toast(message, type = "error") {
  let box = document.querySelector(".toast-box");
  if (!box) {
    box = document.createElement("div");
    box.className = "toast-box";
    document.body.appendChild(box);
  }
  const item = document.createElement("div");
  item.className = "toast " + type;
  item.textContent = message;
  box.appendChild(item);
  setTimeout(() => item.remove(), 3500);
}

function setText(selector, text) {
  const el = document.querySelector(selector);
  if (el) el.textContent = text;
}

/* Menu mobile trong header Savors. */
document.addEventListener("DOMContentLoaded", () => {
  const toggle = document.querySelector(".nav-toggle");
  const nav = document.querySelector(".header-nav");
  if (!toggle || !nav) return;
  toggle.addEventListener("click", () => {
    const open = nav.classList.toggle("open");
    toggle.classList.toggle("open", open);
    toggle.setAttribute("aria-expanded", String(open));
  });
});

/* Nút thao tác dùng event delegation: data-action + data-id (+ data-status). */
function bindActions(handler) {
  document.addEventListener("click", (event) => {
    const btn = event.target.closest("button[data-action]");
    if (!btn) return;
    handler(btn.dataset, btn);
  });
}
