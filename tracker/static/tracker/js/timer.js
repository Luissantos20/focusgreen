// ========================================================
// TIMER JAVASCRIPT - FocusGreen 🌿
// ========================================================

let timerInterval = null;
let seconds = 0;
let running = false;

// ------------------------------------------------------
// Utilidades
// ------------------------------------------------------
function byId(id) {
    return document.getElementById(id);
}

// ------------------------------------------------------
// Formata o tempo em HH:MM:SS (exibe horas se > 60min)
// ------------------------------------------------------
function formatTime(totalSeconds) {
    const h = Math.floor(totalSeconds / 3600);
    const m = Math.floor((totalSeconds % 3600) / 60);
    const s = totalSeconds % 60;
    return h > 0
        ? `${String(h).padStart(2, "0")}:${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`
        : `${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
}

// ------------------------------------------------------
// Formata minutos para string legível (para histórico)
// ------------------------------------------------------
function formatMinutes(mins) {
    if (mins < 60) return `${mins} min`;
    const h = Math.floor(mins / 60);
    const m = mins % 60;
    return m > 0 ? `${h}h ${m}min` : `${h}h`;
}

// ------------------------------------------------------
// Atualiza display do timer
// ------------------------------------------------------
function updateDisplay() {
    const el = byId("fg-timer-display");
    if (el) el.textContent = formatTime(seconds);
}

// ------------------------------------------------------
// Coleta o CSRF Token (requerido pelo Django)
// ------------------------------------------------------
function getCSRFToken() {
    const name = "csrftoken=";
    const cookies = document.cookie.split(";");
    for (let c of cookies) {
        c = c.trim();
        if (c.startsWith(name)) return c.substring(name.length);
    }
    return null;
}

// ------------------------------------------------------
// Funções do Timer
// ------------------------------------------------------
function startTimer() {
    if (running) return;
    running = true;

    const display = byId("fg-timer-display");
    display.classList.add("active-timer");

    timerInterval = setInterval(() => {
        seconds++;
        updateDisplay();

        // Segurança: pausa automática após 10h
        if (seconds >= 36000) {
            pauseTimer();
            showFlashMessage("info", "⏸️ Timer pausado automaticamente após 10 horas.");
        }
    }, 1000);
}

function pauseTimer() {
    running = false;
    clearInterval(timerInterval);

    const display = byId("fg-timer-display");
    display.classList.remove("active-timer");
}

function resetTimer() {
    pauseTimer();
    seconds = 0;
    updateDisplay();
}

// ------------------------------------------------------
// Mostra alertas visuais (Bootstrap)
// ------------------------------------------------------
function showFlashMessage(type, text) {
    const container = byId("flash-messages");
    if (!container) return;

    const alertDiv = document.createElement("div");
    alertDiv.className = `alert alert-${type} alert-dismissible fade show shadow-sm`;
    alertDiv.setAttribute("role", "alert");
    alertDiv.innerHTML = `
        ${text}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;

    container.appendChild(alertDiv);

    // Remove automaticamente após 5 segundos
    setTimeout(() => {
        alertDiv.classList.remove("show");
        alertDiv.classList.add("fade");
        setTimeout(() => alertDiv.remove(), 500);
    }, 5000);
}

// ------------------------------------------------------
// Envia o tempo via AJAX (fetch → Django)
// ------------------------------------------------------
async function stopAndSave() {
    pauseTimer();
    const minutes = Math.floor(seconds / 60);

    if (minutes <= 0) {
        showFlashMessage("warning", "⏱️ Registre ao menos 1 minuto antes de salvar.");
        return;
    }

    const category = byId("fg-category").value;
    const note = byId("fg-note").value;

    try {
        const resp = await fetch(window.FG_ADD_ENTRY_URL, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken(),
            },
            body: JSON.stringify({ minutes, category, note }),
        });

        const data = await resp.json();

        if (!data.success) {
            showFlashMessage("danger", data.error || "Erro ao salvar o tempo.");
            return;
        }

        // ✅ Mostra mensagem de sucesso
        showFlashMessage("success", data.message || "Tempo adicionado com sucesso! 🌿");

        // Atualiza histórico dinâmico
        const tbody = byId("fg-history-body");
        if (tbody) {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td>${data.entry.started_at}</td>
                <td>${formatMinutes(data.entry.minutes)}</td>
                <td>${
                    data.entry.category === "Produtivo"
                        ? '<span class="badge bg-success">Produtivo</span>'
                        : '<span class="badge bg-danger">Não Produtivo</span>'
                }</td>
                <td>${data.entry.note || "—"}</td>`;
            tbody.prepend(tr);
        }

        resetTimer();
    } catch (err) {
        showFlashMessage("danger", "Erro: " + err.message);
    }
}

// ------------------------------------------------------
// Inicialização
// ------------------------------------------------------
document.addEventListener("DOMContentLoaded", () => {
    updateDisplay();

    byId("fg-start").addEventListener("click", startTimer);
    byId("fg-pause").addEventListener("click", pauseTimer);
    byId("fg-stop").addEventListener("click", stopAndSave);
    byId("fg-reset").addEventListener("click", resetTimer);
});
