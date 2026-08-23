const state = {
  lang: "en",
  market: "uae",
  direction: "transparency",
  view: "choose",
  phone: "trip",
  learned: false,
  large: false,
};

const markets = {
  uae: { cur: "AED", city: "Dubai", dest: "Marina", name: { en: "Ahmed", ar: "أحمد" }, fee: 8, fare: "27.50", plate: "RAK 48291" },
  ksa: { cur: "SAR", city: "Riyadh", dest: "Olaya", name: { en: "Mohammed", ar: "محمد" }, fee: 12, fare: "28", plate: "KSA 2201" },
  egy: { cur: "EGP", city: "Cairo", dest: "Zamalek", name: { en: "Omar", ar: "عمر" }, fee: 35, fare: "145", plate: "CAI 908" },
};

const i18n = {
  en: {
    arriving: "is 3 min away",
    car: "White Camry",
    call: "Call",
    share: "Share",
    cancel: "Cancel",
    cancelQ: "Cancel this ride?",
    keep: "Keep this trip",
    pay: (m, n) => `Cancel and pay ${m} ${n}`,
    fee: (m, n) => `${m} ${n} if you cancel now`,
    why: "Captain already accepted.",
    kept: "You’re still on the way",
    gone: "Ride cancelled",
    undo: "Undo",
    arrived: "Captain is outside",
    pending: "Payment pending · not charged",
  },
  ar: {
    arriving: "يبعد 3 دقائق",
    car: "كامري بيضاء",
    call: "اتصال",
    share: "مشاركة",
    cancel: "إلغاء",
    cancelQ: "تلغي المشوار؟",
    keep: "خلّ المشوار",
    pay: (m, n) => `ألغِ وادفع ${n} ${m}`,
    fee: (m, n) => `${n} ${m} إذا ألغيت الآن`,
    why: "الكابتن قبل الطلب.",
    kept: "مشوارك ما زال جاري",
    gone: "تم إلغاء المشوار",
    undo: "تراجع",
    arrived: "الكابتن واقف برا",
    pending: "الدفع معلّق · ما انخصم",
  },
};

function t() {
  return i18n[state.lang === "ar" ? "ar" : "en"];
}
function m() {
  return markets[state.market];
}

function device(inner, label, rtl) {
  return `<div class="device">
    <div class="device-label">${label}</div>
    <div class="notch"></div>
    <div class="screen ${rtl ? "rtl" : ""}" style="${state.large ? "font-size:17px" : ""}">${inner}</div>
    <div class="home-ind"></div>
  </div>`;
}

function mapBlock(fare) {
  return `<div class="map">
    <div class="road"></div><div class="road b"></div>
    <div class="pin a"></div><div class="pin b"></div>
    <div class="car-dot"></div>
    <div class="fare">${fare}</div>
  </div>`;
}

function tripScreen(lang) {
  const copy = i18n[lang];
  const mk = m();
  const name = mk.name[lang];
  const rtl = lang === "ar";
  const fare = `${mk.cur} ${mk.fare}`;
  const compactFee = state.learned
    ? `<div class="fee"><b>${copy.fee(mk.cur, mk.fee)}</b><span>${copy.why}</span></div>`
    : "";
  const extra =
    state.phone === "arrived"
      ? `<div class="fee"><b>${copy.arrived}</b><span>${copy.fee(mk.cur, mk.fee)}</span></div>`
      : state.phone === "pending"
        ? `<div class="fee"><b>${copy.pending}</b></div>`
        : compactFee;
  return device(
    `${mapBlock(fare)}
    <div class="sheet">
      <div class="handle"></div>
      <div class="captain">
        <div class="avatar">${name[0]}</div>
        <div class="who"><b>${name}</b><span>${copy.arriving} · ${copy.car}</span></div>
        <div class="plate">${mk.plate}</div>
      </div>
      ${extra}
      <div class="acts">
        <button type="button">${copy.call}</button>
        <button type="button">${copy.share}</button>
        <button class="danger" data-act="open-cancel" type="button">${copy.cancel}</button>
      </div>
    </div>`,
    lang === "ar" ? "مشوار" : "In trip",
    rtl
  );
}

function cancelScreen(lang) {
  const copy = i18n[lang];
  const mk = m();
  const rtl = lang === "ar";
  const speed = state.direction === "speed";
  const recovery = state.direction === "recovery";
  const feeBlock = speed
    ? ""
    : `<div class="fee"><b>${copy.fee(mk.cur, mk.fee)}</b><span>${copy.why}</span></div>`;
  const pay = recovery ? copy.cancel : copy.pay(mk.cur, mk.fee);
  return device(
    `${mapBlock(`${mk.cur} ${mk.fare}`)}
    <div class="sheet">
      <div class="handle"></div>
      <b>${copy.cancelQ}</b>
      <div class="who" style="margin:8px 0"><span>${mk.city} → ${mk.dest}</span></div>
      ${feeBlock}
      <button class="primary" data-act="keep" type="button">${copy.keep}</button>
      <button class="secondary" data-act="pay" type="button">${pay}</button>
    </div>`,
    lang === "ar" ? "إلغاء" : "Cancel",
    rtl
  );
}

function doneScreen(lang) {
  const copy = i18n[lang];
  const recovery = state.direction === "recovery";
  return device(
    `<div class="done">
      <div class="check">${recovery ? "↺" : "✓"}</div>
      <b>${recovery ? copy.undo : copy.gone}</b>
      <span>${recovery ? "8s" : copy.kept}</span>
      ${recovery ? `<button class="primary" data-act="keep" type="button">${copy.undo}</button>` : `<button class="ghost-btn" data-act="trip" type="button">${copy.keep}</button>`}
    </div>`,
    lang === "ar" ? "تم" : "Done",
    lang === "ar"
  );
}

function phonesFor(view) {
  const langs = state.lang === "both" ? ["en", "ar"] : [state.lang === "ar" ? "ar" : "en"];
  const render = view === "cancel" ? cancelScreen : view === "done" ? doneScreen : tripScreen;
  return langs.map(render).join("");
}

function renderChoose() {
  document.getElementById("stage").innerHTML = `
    <div class="dirs">
      <button class="dir-card ${state.direction === "transparency" ? "on" : ""}" data-dir="transparency" type="button">
        <div class="dir-preview"><i></i></div>
        <b>Transparency</b><span>Fee before the tap</span>
      </button>
      <button class="dir-card ${state.direction === "speed" ? "on" : ""}" data-dir="speed" type="button">
        <div class="dir-preview"><i style="background:#111"></i></div>
        <b>Speed</b><span>One tap, then confirm</span>
      </button>
      <button class="dir-card ${state.direction === "recovery" ? "on" : ""}" data-dir="recovery" type="button">
        <div class="dir-preview"><i style="width:60%;left:20%"></i></div>
        <b>Recovery</b><span>Undo after cancel</span>
      </button>
    </div>
    <div class="phones">${phonesFor("trip")}</div>`;
}

function renderFlow() {
  const view = ["cancel", "done"].includes(state.phone) ? state.phone : "trip";
  document.getElementById("stage").innerHTML = `<div class="phones">${phonesFor(view)}</div>`;
}

function paint() {
  if (state.view === "choose") renderChoose();
  else renderFlow();
}

function toast(html, ms = 4000) {
  const el = document.getElementById("toast");
  el.innerHTML = html;
  el.classList.add("show");
  clearTimeout(toast._t);
  toast._t = setTimeout(() => el.classList.remove("show"), ms);
}

document.addEventListener("click", (e) => {
  const lang = e.target.closest("[data-lang]");
  if (lang) {
    state.lang = lang.dataset.lang;
    document.querySelectorAll("[data-lang]").forEach((b) => b.classList.toggle("active", b === lang));
    paint();
    return;
  }
  const dir = e.target.closest("[data-dir]");
  if (dir) {
    state.direction = dir.dataset.dir;
    state.view = "flow";
    state.phone = "cancel";
    paint();
    return;
  }
  const act = e.target.closest("[data-act]");
  if (act) {
    const a = act.dataset.act;
    if (a === "open-cancel") state.phone = "cancel";
    if (a === "keep") {
      state.phone = "trip";
      toast(t().kept);
    }
    if (a === "pay") state.phone = "done";
    if (a === "trip") state.phone = "trip";
    state.view = "flow";
    paint();
    if (a === "open-cancel" && !state.learned) {
      toast(
        `Move the fee inline and cut extra copy?
        <div class="row">
          <button class="pill green" id="learnYes" type="button">Yes — learn this</button>
          <button class="pill" id="learnNo" type="button">Not now</button>
        </div>`,
        12000
      );
    }
    return;
  }
  if (e.target.id === "learnYes") {
    state.learned = true;
    document.getElementById("dnaChip").textContent = "DNA · inline fees";
    toast("Learned. Tooba favors compact, action-first layouts.");
    paint();
    return;
  }
  if (e.target.id === "learnNo") {
    document.getElementById("toast").classList.remove("show");
    return;
  }
  if (e.target.id === "stressBtn") {
    state.view = "flow";
    state.phone = "arrived";
    paint();
    toast("Missing state generated: Captain arrived + fee still visible.");
    return;
  }
  if (e.target.id === "handBtn") {
    toast("Handoff ready · screens, FareChip, Button/Primary, cancel_fee_shown, AR included.");
  }
});

document.getElementById("market").addEventListener("change", (e) => {
  state.market = e.target.value;
  state.large = e.target.value === "egy";
  paint();
});

function showAsk(data) {
  const box = document.getElementById("askReply");
  document.getElementById("askTopic").textContent = data.topic.replace("_", " ");
  document.getElementById("askMeta").textContent = `${Math.round((data.confidence || 0) * 100)}% · local model`;
  document.getElementById("askAnswer").textContent = data.answer;
  document.getElementById("askEvidence").innerHTML = (data.evidence || [])
    .map((row) => `<li><q>${row.text}</q><small>${row.source}</small></li>`)
    .join("");
  box.hidden = false;
}

document.getElementById("askClose").addEventListener("click", () => {
  document.getElementById("askReply").hidden = true;
});

document.getElementById("ask").addEventListener("submit", async (e) => {
  e.preventDefault();
  const q = document.getElementById("askInput").value.trim();
  if (!q) return;
  document.getElementById("askInput").value = "";
  document.getElementById("askAnswer").textContent = "Looking through the ride-review model…";
  document.getElementById("askEvidence").innerHTML = "";
  document.getElementById("askReply").hidden = false;
  try {
    const res = await fetch("/api/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question: q }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Ask failed");
    showAsk(data);
  } catch (err) {
    document.getElementById("askTopic").textContent = "error";
    document.getElementById("askAnswer").textContent = err.message || "Ask is offline. Restart studio_server.py.";
  }
});

paint();

const preset = new URLSearchParams(location.search).get("ask");
if (preset) {
  document.getElementById("askInput").value = preset;
  document.getElementById("ask").requestSubmit();
}
