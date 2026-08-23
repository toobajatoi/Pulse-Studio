const SUGGESTS = [
  "Make me a screen for Home dashboard for careem riders that should have analytics of their monthly earnings",
  "Ride cancellation with the fee visible before they tap",
  "Arabic rider home with August earnings",
];

const history = [];
let lastScreen = null;
let splitMode = null;
let thinking = false;
let lastModel = "";
let lastChoices = [];
let lastCritic = null;

const DNA_KEY = "careem-studio-dna";
const DEFAULT_DNA = {
  designer: "Tooba",
  density: "compact",
  copy: "short",
  numbers: "visible-first",
  accent: "careem-green",
  notes: ["action-first", "inline fees", "Ride stays one tap"],
};

function loadDna() {
  try {
    return { ...DEFAULT_DNA, ...JSON.parse(localStorage.getItem(DNA_KEY) || "{}") };
  } catch {
    return { ...DEFAULT_DNA };
  }
}

function saveDna(next) {
  localStorage.setItem(DNA_KEY, JSON.stringify(next));
  paintDna();
}

function dna() {
  return loadDna();
}

function paintDna() {
  const d = dna();
  const chip = document.getElementById("dnaChip");
  if (chip) chip.textContent = `DNA · ${d.density}`;
}

function applyChoiceToDna(id, label) {
  const d = dna();
  const note = label || id;
  if (!d.notes.includes(note)) d.notes = [...d.notes.slice(-6), note];
  if (id === "compact" || /compact|dense|tight/i.test(label)) d.density = "compact";
  if (id === "comfortable" || /spacious|air|comfortable/i.test(label)) d.density = "comfortable";
  if (id === "clear" || /number|fee|fare|visible/i.test(label)) d.numbers = "visible-first";
  if (id === "short" || /short|less copy/i.test(label)) d.copy = "short";
  if (id === "learn") d.notes = [...d.notes.slice(-6), "liked last screen"];
  saveDna(d);
  return d;
}

const DEFAULT_SCREEN = {
  kind: "dashboard",
  title: "Home",
  label: "Home · Dubai",
  rtl: false,
  hello: "Good evening, Tooba",
  where: "Where to?",
  month: "August earnings",
  earned: "AED 186.40",
  delta: "+12% vs July · Plus cashback",
  weeks: [42, 68, 51, 88],
  stats: [
    { n: "18", l: "Trips" },
    { n: "AED 1,248", l: "Spent" },
    { n: "AED 186", l: "Earned" },
  ],
  split: [["Rides", 72], ["Food", 19], ["Quik", 9]],
  recent_title: "Recent trips",
  trips: [
    ["Dubai Mall", "Today · 24.50"],
    ["Marina", "Yesterday · 18.00"],
    ["Airport T3", "22 Aug · 62.00"],
  ],
  tabs: ["Home", "Activity", "Pay", "You"],
};

function esc(text) {
  return String(text ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

function clone(obj) {
  return JSON.parse(JSON.stringify(obj));
}

function currentScreen() {
  return lastScreen || DEFAULT_SCREEN;
}

function device(inner, label, rtl) {
  const density = dna().density === "comfortable" ? "comfortable" : "compact";
  return `<div class="device">
    <div class="device-label">${label || ""}</div>
    <div class="notch"></div>
    <div class="screen ${rtl ? "rtl" : ""} ${density}">${inner}</div>
    <div class="home-ind"></div>
  </div>`;
}

function renderDashboard(s) {
  const weeks = s.weeks || [40, 60, 50, 80];
  const max = Math.max(...weeks, 1);
  const bars = weeks.map((n) => `<i style="height:${Math.round((n / max) * 100)}%"></i>`).join("");
  const stats = (s.stats || []).map((x) => `<div class="stat"><b>${esc(x.n)}</b><span>${esc(x.l)}</span></div>`).join("");
  const split = (s.split || [])
    .map((row) => {
      const name = Array.isArray(row) ? row[0] : row.n || row.name;
      const pct = Array.isArray(row) ? row[1] : row.p || row.pct;
      return `<div class="split-row"><b>${esc(name)}</b><div class="track"><i style="width:${pct}%"></i></div><span>${pct}%</span></div>`;
    })
    .join("");
  const trips = (s.trips || [])
    .map((row) => {
      const name = Array.isArray(row) ? row[0] : row.t || row.name;
      const meta = Array.isArray(row) ? row[1] : row.s || row.meta;
      return `<div class="trip"><b>${esc(name)}</b><span>${esc(meta)}</span></div>`;
    })
    .join("");
  const tabs = (s.tabs || ["Home", "You"]).map((t, i) => `<span class="${i === 0 ? "on" : ""}">${esc(t)}</span>`).join("");
  const search = s.where ? `<div class="where">${esc(s.where)}</div>` : "";
  return device(
    `<div class="dash">
      <span class="dash-hello">${esc(s.hello || "")}</span>
      <div class="dash-name">${esc(s.title || "Home")}</div>
      ${search}
      <section class="earn">
        <small>${esc(s.month || "")}</small>
        <h2>${esc(s.earned || "")}</h2>
        <p>${esc(s.delta || "")}</p>
        <div class="bars">${bars}</div>
      </section>
      <div class="stats">${stats}</div>
      <div class="split">${split}</div>
      <div class="recent"><b>${esc(s.recent_title || "")}</b>${trips}</div>
      <nav class="tabbar">${tabs}</nav>
    </div>`,
    s.label,
    s.rtl
  );
}

function renderBlock(b) {
  const type = b.type;
  if (type === "hello") {
    return `<span class="dash-hello">${esc(b.kicker || "")}</span><div class="dash-name">${esc(b.title || "")}</div>`;
  }
  if (type === "search") return `<div class="where">${esc(b.text || "Search")}</div>`;
  if (type === "pills") {
    return `<div class="svc">${(b.items || []).map((x) => `<span>${esc(x)}</span>`).join("")}</div>`;
  }
  if (type === "hero") {
    const bars = b.bars || [];
    const max = Math.max(...bars, 1);
    const chart = bars.length
      ? `<div class="bars">${bars.map((n) => `<i style="height:${Math.round((n / max) * 100)}%"></i>`).join("")}</div>`
      : "";
    return `<section class="earn"><small>${esc(b.label || "")}</small><h2>${esc(b.value || "")}</h2><p>${esc(b.meta || "")}</p>${chart}</section>`;
  }
  if (type === "stats") {
    return `<div class="stats">${(b.items || []).map((x) => `<div class="stat"><b>${esc(x.n)}</b><span>${esc(x.l)}</span></div>`).join("")}</div>`;
  }
  if (type === "split") {
    return `<div class="split">${(b.items || [])
      .map((x) => `<div class="split-row"><b>${esc(x.n)}</b><div class="track"><i style="width:${x.p || 0}%"></i></div><span>${x.p || 0}%</span></div>`)
      .join("")}</div>`;
  }
  if (type === "list") {
    return `<div class="recent"><b>${esc(b.title || "")}</b>${(b.items || [])
      .map((x) => `<div class="trip"><b>${esc(x.t)}</b><span>${esc(x.s)}</span></div>`)
      .join("")}</div>`;
  }
  if (type === "note") return `<div class="note-card">${esc(b.text || "")}</div>`;
  if (type === "map") {
    return `<div class="map"><div class="road"></div><div class="road b"></div><div class="pin a"></div><div class="pin b"></div></div>`;
  }
  if (type === "sheet") {
    return `<div class="sheet"><div class="handle"></div><b>${esc(b.title || "")}</b><div style="margin:8px 0;color:#5f6368;font-size:12px">${esc(b.sub || "")}</div>${
      b.fee ? `<div class="fee"><b>${esc(b.fee)}</b><span>${esc(b.feeNote || "")}</span></div>` : ""
    }${b.primary ? `<button class="primary" type="button">${esc(b.primary)}</button>` : ""}${
      b.secondary ? `<button class="secondary" type="button">${esc(b.secondary)}</button>` : ""
    }</div>`;
  }
  if (type === "cta") {
    return `<button class="${b.style === "secondary" ? "secondary" : "primary"}" type="button">${esc(b.text || "Continue")}</button>`;
  }
  if (type === "tabs") {
    return `<nav class="tabbar">${(b.items || []).map((t, i) => `<span class="${i === 0 ? "on" : ""}">${esc(t)}</span>`).join("")}</nav>`;
  }
  return "";
}

function renderGeneric(s) {
  const body = (s.blocks || []).map(renderBlock).join("");
  return device(`<div class="dash">${body}</div>`, s.label, s.rtl);
}

function renderOne(s) {
  if (!s) return "";
  if (s.blocks && s.blocks.length) return renderGeneric(s);
  if (s.kind === "cancel" || s.kind === "arrived") return renderCancel(s);
  return renderDashboard(s);
}

function renderCancel(s) {
  return device(
    `<div class="map">
      <div class="road"></div><div class="road b"></div>
      <div class="pin a"></div><div class="pin b"></div>
      <div class="fare">${s.fare}</div>
    </div>
    <div class="sheet">
      <div class="handle"></div>
      <b>${s.rtl ? "تلغي المشوار؟" : "Cancel this ride?"}</b>
      <div style="margin:8px 0;color:#5f6368;font-size:12px">${s.city} → ${s.dest}</div>
      <div class="fee"><b>${s.fee} ${s.rtl ? "إذا ألغيت الآن" : "if you cancel now"}</b><span>${s.rtl ? "الكابتن قبل الطلب." : "Captain already accepted."}</span></div>
      <button class="primary" type="button">${s.rtl ? "خلّ المشوار" : "Keep this trip"}</button>
      <button class="secondary" type="button">${s.rtl ? "ألغِ وادفع" : "Cancel and pay"} ${s.fee}</button>
    </div>`,
    s.label,
    s.rtl
  );
}

function paintPhones(screens, head) {
  const preview = document.getElementById("preview");
  const stage = document.getElementById("stage");
  const pane = document.querySelector(".pane");
  const previewHead = document.getElementById("previewHead");
  if (!screens.length) {
    preview.hidden = true;
    pane.classList.remove("has-preview");
    return;
  }
  stage.innerHTML = screens.map(renderOne).join("");
  previewHead.textContent = head || "Live screen";
  preview.hidden = false;
  pane.classList.add("has-preview");
}

function paintScreen(screen) {
  if (!screen) {
    paintPhones([], "");
    return;
  }
  lastScreen = screen;
  if (splitMode) {
    openSplit(splitMode);
    return;
  }
  paintPhones([screen], screen.label || "Live screen");
}

function emptyMonth(screen) {
  const s = clone(screen);
  s.label = "Empty state";
  if (s.blocks) {
    s.blocks = s.blocks.map((b) => {
      if (b.type === "hero") return { ...b, value: "0", meta: "Nothing here yet", bars: [4, 4, 4, 4] };
      if (b.type === "stats") return { ...b, items: (b.items || []).map((x) => ({ ...x, n: "0" })) };
      if (b.type === "list") return { ...b, items: [] };
      return b;
    });
    return s;
  }
  s.earned = String(s.earned || "0").replace(/[\d,.]+/, "0.00");
  s.delta = "No trips yet this month";
  s.weeks = [4, 4, 4, 4];
  s.stats = (s.stats || []).map((row, i) => ({ n: i === 0 ? "0" : String(row.n).replace(/[\d,.]+/, "0"), l: row.l }));
  s.trips = [];
  return s;
}

function arabicVariant(screen) {
  const s = clone(screen);
  s.rtl = true;
  s.label = `${s.label || "Screen"} · AR`;
  if (s.kind === "cancel" && !s.blocks) return s;
  if (!s.blocks) {
    s.hello = "مساء الخير، Tooba";
    s.title = s.title || "الرئيسية";
    s.where = s.where ? "وين نروح؟" : "";
    s.tabs = ["الرئيسية", "نشاط", "دفع", "حسابك"];
  }
  return s;
}

function arrivedCancel(screen) {
  const base = screen && screen.kind === "cancel" ? clone(screen) : {
    kind: "cancel",
    label: "Arrived · fee on",
    rtl: false,
    city: "Dubai",
    dest: "Marina",
    fare: "AED 27.50",
    fee: "AED 8",
  };
  base.kind = "cancel";
  base.label = "Arrived · fee on";
  return base;
}

function splitCards(mode, screen) {
  if (mode === "stress") {
    if (screen.kind === "cancel" && !screen.blocks) {
      return {
        title: "Stress test",
        head: "Screens",
        screens: [arrivedCancel(screen), arabicVariant(arrivedCancel(screen))],
        cards: [
          { h: "Captain arrived", p: "Fee stays visible after arrival. Hiding it here is how surprise-charge tickets start." },
          { h: "Arabic expansion", p: "Primary and pay labels grow. Keep them one line, or the sheet covers the fare chip." },
          { h: "Missing state", p: "Payment pending + not charged must still show the same fee rule." },
        ],
        pills: ["cancel_fee_shown", "arrived", "AR", "Careem DNA"],
      };
    }
    return {
      title: "Stress test",
      head: "Screens",
      screens: [screen, emptyMonth(screen), arabicVariant(screen)],
      cards: [
        { h: "Happy path", p: "The main number and primary action stay on the first screen." },
        { h: "Empty state", p: "Zero data must not break the layout. Flat bars beat a blank card." },
        { h: "Arabic", p: "RTL and longer labels cannot clip the primary action." },
      ],
      pills: ["happy_path", "empty_state", "AR"],
    };
  }
  const components = screen.kind === "cancel"
    ? ["FareChip", "Button / Primary", "FeeBanner", "Map"]
    : ["WhereTo", "EarningsCard", "StatRow", "SplitBar", "TabBar"];
  return {
    title: "Handoff",
    head: "Screens to ship",
    screens: screen.kind === "cancel" ? [screen, arabicVariant(screen)] : [screen, arabicVariant(screen)],
    cards: [
      { h: "What ships", p: screen.kind === "cancel" ? "Cancel sheet with fee before the tap, EN + AR, UAE numbers." : "The live screen plus its Arabic twin." },
      { h: "Design DNA", p: `Tooba · ${dna().density} · ${dna().copy} copy · ${dna().numbers}. ${dna().notes.slice(-3).join(" · ")}` },
      { h: "Acceptance", p: "Primary number stays visible. Style matches the learned DNA. Arabic does not clip the CTA." },
    ],
    pills: components.concat(["EN", "AR", "UAE", `DNA:${dna().density}`]),
  };
}

function openSplit(mode) {
  const screen = currentScreen();
  lastScreen = screen;
  splitMode = mode;
  const spec = splitCards(mode, screen);
  const details = document.getElementById("details");
  const pane = document.querySelector(".pane");
  details.hidden = false;
  details.innerHTML = `
    <div class="details-top">
      <h2>${spec.title}</h2>
      <button type="button" id="closeSplit">Back to chat</button>
    </div>
    ${spec.cards.map((c) => `<article class="detail-card"><h3>${c.h}</h3><p>${c.p}</p></article>`).join("")}
    <article class="detail-card">
      <h3>Included</h3>
      <div class="detail-pills">${spec.pills.map((p) => `<span>${p}</span>`).join("")}</div>
    </article>`;
  pane.classList.add("split-mode", "has-preview");
  document.getElementById("stressBtn").classList.toggle("on", mode === "stress");
  document.getElementById("handBtn").classList.toggle("on", mode === "handoff");
  paintPhones(spec.screens, spec.head);
}

function closeSplit() {
  splitMode = null;
  document.getElementById("details").hidden = true;
  document.querySelector(".pane").classList.remove("split-mode");
  document.getElementById("stressBtn").classList.remove("on");
  document.getElementById("handBtn").classList.remove("on");
  if (lastScreen) paintPhones([lastScreen], lastScreen.label || "Live screen");
  else {
    document.getElementById("preview").hidden = true;
    document.querySelector(".pane").classList.remove("has-preview");
  }
}

function emptyState() {
  return `<div class="hero">
    <h1 class="hello">Hello, Tooba</h1>
    <p class="sub">I co-design with you and learn your style.</p>
    <div class="ideas">${SUGGESTS.map((s) => `<button class="idea" type="button">${s}</button>`).join("")}</div>
  </div>`;
}

function renderThread() {
  const el = document.getElementById("thread");
  if (!history.length) {
    el.innerHTML = emptyState();
    return;
  }
  el.innerHTML = history
    .map((m, i) => {
      if (m.role === "user") return `<article class="msg user"><div class="bubble">${esc(m.content)}</div></article>`;
      const who = m.model ? `Studio · ${m.model}` : "Studio";
      const last = i === history.length - 1 && !thinking;
      const choices = last && lastChoices.length
        ? `<div class="choices">${lastChoices.map((c) => `<button class="choice ${c.id === "learn" ? "learn" : ""}" data-choice="${esc(c.id)}" type="button">${esc(c.label)}</button>`).join("")}</div>`
        : "";
      return `<article class="msg assistant"><div class="bubble"><div class="who"><svg viewBox="0 0 24 24" width="16" height="16"><path fill="url(#g)" d="M12 2l1.6 6.4L20 10l-6.4 1.6L12 18l-1.6-6.4L4 10l6.4-1.6L12 2z"/></svg> ${esc(who)}</div>${esc(m.content)}${choices}</div></article>`;
    })
    .join("");
  if (thinking) {
    el.innerHTML += `<article class="msg assistant"><div class="bubble"><div class="who">Studio</div>Designing your screen…</div></article>`;
  }
  el.scrollTop = el.scrollHeight;
}

async function send(text) {
  const q = (text || "").trim();
  if (!q || thinking) return;
  history.push({ role: "user", content: q });
  thinking = true;
  renderThread();
  document.getElementById("askInput").value = "";
  try {
    const res = await fetch("/api/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        question: q,
        history: history.map((m) => ({ role: m.role, content: m.content, intent: m.intent })),
        dna: dna(),
      }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Ask failed");
    lastModel = data.model || "";
    lastChoices = data.choices || [];
    lastCritic = data.critic || null;
    history.push({ role: "assistant", content: data.reply, intent: data.intent, screen: data.screen, model: lastModel });
    thinking = false;
    renderThread();
    paintScreen(data.screen || lastScreen);
    showCritic(lastCritic);
  } catch (err) {
    thinking = false;
    history.push({ role: "assistant", content: err.message || "Studio is offline. Start studio_server.py." });
    renderThread();
  }
}

document.getElementById("ask").addEventListener("submit", (e) => {
  e.preventDefault();
  send(document.getElementById("askInput").value);
});

function showCritic(c) {
  const card = document.getElementById("criticCard");
  if (!card) return;
  if (!c) {
    card.hidden = true;
    return;
  }
  card.hidden = false;
  document.getElementById("criticRing").style.setProperty("--p", String(c.score || 90));
  document.getElementById("criticScore").textContent = c.score || 90;
  document.getElementById("criticNote").textContent = c.note || "Careem + your DNA";
}

function openDnaPanel() {
  const d = dna();
  const details = document.getElementById("details");
  const pane = document.querySelector(".pane");
  splitMode = "dna";
  details.hidden = false;
  details.innerHTML = `
    <div class="details-top">
      <h2>Design DNA</h2>
      <button type="button" id="closeSplit">Back to chat</button>
    </div>
    <article class="detail-card"><h3>Designer</h3><p>${esc(d.designer)} — Studio adapts to this style on every prompt.</p></article>
    <article class="detail-card"><h3>Density</h3><p>${esc(d.density)}</p></article>
    <article class="detail-card"><h3>Copy</h3><p>${esc(d.copy)} · numbers ${esc(d.numbers)}</p></article>
    <article class="detail-card"><h3>Learned</h3><div class="detail-pills">${d.notes.map((n) => `<span>${esc(n)}</span>`).join("")}</div></article>`;
  pane.classList.add("split-mode", "has-preview");
  if (lastScreen) paintPhones([lastScreen], "Adapted to your DNA");
  else paintPhones([DEFAULT_SCREEN], "Adapted to your DNA");
}

document.getElementById("thread").addEventListener("click", (e) => {
  const idea = e.target.closest(".idea");
  if (idea) send(idea.textContent);
  const choice = e.target.closest("[data-choice]");
  if (choice) {
    const id = choice.dataset.choice;
    const label = choice.textContent;
    applyChoiceToDna(id, label);
    if (id === "learn") {
      lastChoices = [];
      renderThread();
      return;
    }
    send(`Adapt the current screen: ${label}. Stay on the same product problem.`);
  }
});

document.getElementById("stressBtn").addEventListener("click", () => openSplit("stress"));
document.getElementById("handBtn").addEventListener("click", () => openSplit("handoff"));
document.getElementById("dnaChip").addEventListener("click", openDnaPanel);
document.getElementById("details").addEventListener("click", (e) => {
  if (e.target.id === "closeSplit") closeSplit();
});

paintDna();
renderThread();

const params = new URLSearchParams(location.search);
const preset = params.get("ask");
if (preset) {
  send(preset).then(() => {
    if (params.get("mode") === "stress") openSplit("stress");
    if (params.get("mode") === "handoff") openSplit("handoff");
  });
} else if (params.get("mode") === "stress") openSplit("stress");
else if (params.get("mode") === "handoff") openSplit("handoff");
