const KEY = "careem-studio-v2";
const COMPONENTS = {
  hello: "Text/Title",
  search: "WhereTo",
  pills: "ChipRow",
  hero: "EarningsCard",
  stats: "StatRow",
  split: "SplitBar",
  list: "ListRow",
  note: "HelperText",
  map: "Map",
  sheet: "Sheet",
  cta: "Button/Primary",
  tabs: "TabBar",
};

const state = {
  view: "brief",
  mode: "prompt",
  brief: {
    goal: "Design the checkout flow for scheduled grocery delivery.",
    product: "Quik",
    platform: "iOS",
    user: "First-time rider",
    market: "UAE",
    language: "EN",
    constraint: "Max 2 CTAs · fee visible before pay",
    flow: "Home → Search → Slot → Checkout → Payment",
  },
  dna: {
    density: 28,
    corners: 62,
    hierarchy: 35,
    copy: 22,
    interaction: 30,
    observed: ["Sticky primary actions", "Bottom sheets over dialogs", "Maximum 2 actions per screen", "Prefer concise microcopy"],
    projectOnly: [],
  },
  directions: [],
  previews: {},
  picked: null,
  screen: null,
  tree: [],
  issues: [],
  flow: { steps: [], problems: [] },
  reply: "",
  thinking: false,
  pendingLearn: null,
  selectedLayer: -1,
  sketch: ["header", "search"],
  chats: [],
  chatId: null,
  messages: [],
  os: "ios",
  lang: "en",
};

function load() {
  try {
    const saved = JSON.parse(localStorage.getItem(KEY) || "{}");
    if (saved.dna) state.dna = { ...state.dna, ...saved.dna };
    if (saved.brief) state.brief = { ...state.brief, ...saved.brief };
    if (saved.chats) state.chats = saved.chats;
    if (saved.chatId) state.chatId = saved.chatId;
  } catch {}
}
function persist() {
  localStorage.setItem(KEY, JSON.stringify({ dna: state.dna, brief: state.brief, chats: state.chats, chatId: state.chatId }));
}
function chatTitle() {
  return (state.brief.goal || "New chat").replace(/\s+/g, " ").slice(0, 46);
}
function saveChat() {
  const id = state.chatId || String(Date.now());
  state.chatId = id;
  const item = {
    id,
    title: chatTitle(),
    preview: (state.reply || state.messages.slice(-1)[0]?.text || "Brief").slice(0, 72),
    snap: {
      view: state.view,
      mode: state.mode,
      brief: JSON.parse(JSON.stringify(state.brief)),
      directions: state.directions,
      previews: state.previews,
      picked: state.picked,
      screen: state.screen,
      tree: state.tree,
      issues: state.issues,
      flow: state.flow,
      reply: state.reply,
      messages: state.messages,
      os: state.os,
      lang: state.lang,
    },
  };
  const i = state.chats.findIndex((c) => c.id === id);
  if (i >= 0) state.chats[i] = item;
  else state.chats.unshift(item);
  persist();
  paintHistory();
}
function newChat() {
  state.chatId = String(Date.now());
  state.messages = [];
  state.directions = [];
  state.previews = {};
  state.picked = null;
  state.screen = null;
  state.tree = [];
  state.issues = [];
  state.reply = "";
  state.pendingLearn = null;
  state.selectedLayer = -1;
  state.view = "brief";
  const input = document.getElementById("askInput");
  if (input) input.value = "";
  render();
}
function openChat(id) {
  const item = state.chats.find((c) => c.id === id);
  if (!item || !item.snap) return;
  Object.assign(state, item.snap);
  state.chatId = id;
  render();
}
function deleteChat(id) {
  const wasOpen = state.chatId === id;
  state.chats = state.chats.filter((c) => c.id !== id);
  persist();
  if (wasOpen) newChat();
  else paintHistory();
}
function paintHistory() {
  const el = document.getElementById("histList");
  if (!el) return;
  if (!state.chats.length) {
    el.innerHTML = `<p class="hist-empty">Chats you start will show up here</p>`;
    return;
  }
  el.innerHTML = state.chats
    .map(
      (c) => `<div class="hist-row ${c.id === state.chatId ? "on" : ""}">
        <button class="hist-item" data-chat="${c.id}" type="button"><b>${esc(c.title)}</b><span>${esc(c.preview || "")}</span></button>
        <button class="hist-del" data-del="${c.id}" type="button" aria-label="Delete chat">×</button>
      </div>`
    )
    .join("");
}
function esc(t) {
  return String(t ?? "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}
function labelOf(v, a, b) {
  if (v < 35) return a;
  if (v > 65) return b;
  return `${a} / ${b}`;
}

function asPairs(list, a, b) {
  return (list || []).map((x) => (Array.isArray(x) ? { [a]: x[0], [b]: x[1] } : x));
}
function device(inner, label, rtl) {
  const dense = state.dna.density < 40 ? "compact" : "comfortable";
  const os = state.os === "android" ? "android" : "ios";
  return `<div class="device ${os}"><div class="device-label">${esc(label || "")} · ${os === "android" ? "Android" : "iOS"} · ${rtl ? "AR" : "EN"}</div><div class="screen ${rtl ? "rtl" : ""} ${dense}"><div class="status"><span>9:41</span><span class="notch"></span><span>${os === "android" ? "LTE" : "5G"} ●●●</span></div>${inner}</div></div>`;
}
const I18N = {
  en: {
    online: "Online",
    hey: (n) => `Hey! ${n} wants to ride with you`,
    pickupPoint: "Pickup point",
    dropPoint: "Drop-off point",
    accept: "Accept",
    decline: "Decline",
    keep: "Keep this trip",
    cancelQ: "Cancel this ride?",
    payCancel: (fee) => `Cancel and pay ${fee}`,
    feeNow: (fee) => `${fee} if you cancel now`,
    feeWhy: "Captain already accepted.",
    home: "Home",
    wallet: "Wallet",
    history: "History",
    more: "More",
    rider: { Ahmed: "Ahmed", Mohammed: "Mohammed", Omar: "Omar", Tooba: "Tooba" },
    place: {
      "Dubai Mall, Financial Centre Rd": "Dubai Mall, Financial Centre Rd",
      "Downtown Dubai": "Downtown Dubai",
      "Marina Walk, JBR": "Marina Walk, JBR",
      "Dubai Marina": "Dubai Marina",
      "Kingdom Centre, Olaya St": "Kingdom Centre, Olaya St",
      Olaya: "Olaya",
      "King Abdullah Park": "King Abdullah Park",
      "City Stars, Nasr City": "City Stars, Nasr City",
      "Zamalek Bridge Rd": "Zamalek Bridge Rd",
    },
  },
  ar: {
    online: "متصل",
    hey: (n) => `هلا! ${n} يبي مشوار معك`,
    pickupPoint: "نقطة الانطلاق",
    dropPoint: "نقطة الوصول",
    accept: "قبول",
    decline: "رفض",
    keep: "خلّ المشوار",
    cancelQ: "تلغي المشوار؟",
    payCancel: (fee) => `ألغِ وادفع ${fee}`,
    feeNow: (fee) => `${fee} إذا ألغيت الآن`,
    feeWhy: "الكابتن قبل الطلب.",
    home: "الرئيسية",
    wallet: "المحفظة",
    history: "سجل",
    more: "المزيد",
    rider: { Ahmed: "أحمد", Mohammed: "محمد", Omar: "عمر", Tooba: "طوبى" },
    place: {
      "Dubai Mall, Financial Centre Rd": "دبي مول، شارع المركز المالي",
      "Downtown Dubai": "وسط دبي",
      "Marina Walk, JBR": "مارينا ووك، جي بي آر",
      "Dubai Marina": "دبي مارينا",
      "Kingdom Centre, Olaya St": "مركز المملكة، شارع العليا",
      Olaya: "العليا",
      "King Abdullah Park": "حديقة الملك عبدالله",
      "City Stars, Nasr City": "سيتي ستارز، مدينة نصر",
      "Zamalek Bridge Rd": "الزمالك",
    },
  },
};

function loc() {
  return I18N[state.lang === "ar" ? "ar" : "en"];
}

const AR_MAP = {
  "Payment failed": "فشل الدفع",
  "Payment Failed": "فشل الدفع",
  "Payment details": "تفاصيل الدفع",
  "Trip amount": "قيمة المشوار",
  "Try Again": "حاول مرة ثانية",
  "Try again": "حاول مرة ثانية",
  "Change Payment": "غيّر طريقة الدفع",
  "Change payment": "غيّر طريقة الدفع",
  "Could not be processed": "ما قدرنا نعالج الدفع",
  "Payment could not be processed": "ما قدرنا نعالج الدفع",
  Checkout: "الدفع",
  Subtotal: "المجموع",
  Delivery: "التوصيل",
  Total: "الإجمالي",
  "Pay now": "ادفع الآن",
  "Change slot": "غيّر الوقت",
  "Choose a slot": "اختَر وقت التوصيل",
  Home: "الرئيسية",
  Activity: "نشاط",
  Pay: "ادفع",
  You: "حسابك",
  Search: "بحث",
  "Where to?": "وين نروح؟",
  Recent: "الأخير",
  Trips: "مشاوير",
  Spent: "مصروف",
  Earned: "أرباح",
  Orders: "طلبات",
  Saved: "وفّرت",
  Continue: "كمّل",
  "Book a ride": "احجز مشوار",
  "Book Ride": "احجز مشوار",
  Accept: "قبول",
  Decline: "رفض",
  "Accept Ride": "قبول المشوار",
  "Keep this trip": "خلّ المشوار",
  "Cancel this ride?": "تلغي المشوار؟",
  Pickup: "الانطلاق",
  "Pickup point": "نقطة الانطلاق",
  "Drop-off": "الوصول",
  "Drop-off point": "نقطة الوصول",
  Fare: "الأجرة",
  Distance: "المسافة",
  Time: "الوقت",
  Online: "متصل",
  Wallet: "المحفظة",
  History: "سجل",
  More: "المزيد",
  Food: "طعام",
  Rides: "مشاوير",
  Quik: "كويك",
  "Careem Pay": "كريم باي",
  Visa: "فيزا",
  Apps: "تطبيقات",
  Hello: "مرحباً",
  "Good evening": "مساء الخير",
  "Good afternoon": "مساء الخير",
  "August earnings": "أرباح أغسطس",
};

function tx(text) {
  if (text == null) return "";
  const raw = String(text);
  if (state.lang !== "ar") return raw;
  if (AR_MAP[raw]) return AR_MAP[raw];
  const exact = Object.keys(AR_MAP).find((k) => k.toLowerCase() === raw.toLowerCase());
  if (exact) return AR_MAP[exact];
  let out = raw;
  Object.keys(AR_MAP)
    .sort((a, b) => b.length - a.length)
    .forEach((k) => {
      out = out.replace(new RegExp(k.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"), "ig"), AR_MAP[k]);
    });
  return out;
}
function placeName(text) {
  if (!text) return "";
  return loc().place[text] || text;
}
function looksLikeAddress(text) {
  if (!text) return false;
  const t = String(text).trim();
  if (/^(pickup|drop-?off|drop|location|pin|dot)$/i.test(t)) return false;
  return t.length > 4;
}
function screenKind(s) {
  const blob = `${state.brief.goal || ""} ${s.kind || ""} ${s.label || ""}`.toLowerCase();
  if (/accept|incoming|offer/.test(blob)) return "accept";
  if (/cancel/.test(blob)) return "cancel";
  if (/fail|try again/.test(blob)) return "failed";
  if (/checkout|grocery|quik/.test(blob)) return "checkout";
  if (s.kind === "accept" || s.kind === "cancel" || s.kind === "checkout" || s.kind === "failed") return s.kind;
  return s.kind || "home";
}
function mergeAccept(s) {
  const blocks = s.blocks || [];
  const list = (blocks.find((b) => b.type === "list") || {}).items || [];
  const hero = blocks.find((b) => b.type === "hero") || {};
  const pickup = looksLikeAddress(s.pickup) ? s.pickup : looksLikeAddress(list[0]?.t) ? list[0].t : "Dubai Mall, Financial Centre Rd";
  const dest = looksLikeAddress(s.dest) ? s.dest : looksLikeAddress(s.drop) ? s.drop : looksLikeAddress(list[1]?.t) ? list[1].t : "Marina Walk, JBR";
  return {
    kind: "accept",
    label: s.label || "Accept · Dubai",
    rider: s.rider || "Ahmed",
    pay: s.pay || "Careem Pay",
    pickup,
    pickupArea: s.pickupArea || "Downtown Dubai",
    dest,
    dropArea: s.dropArea || "Dubai Marina",
    fare: s.fare || hero.value || "AED 45.00",
    distance: s.distance || "2.3 km",
    eta: s.eta || "8 min",
    rating: s.rating || "4.8",
  };
}
function renderAccept(raw) {
  const s = mergeAccept(raw);
  const t = loc();
  const rider = t.rider[s.rider] || s.rider;
  const initial = rider[0];
  return device(
    `<div class="accept">
      <div class="online-bar"><b>${t.online}</b><span class="switch"></span></div>
      <div class="radar">
        <i class="ring"></i><i class="ring"></i>
        <span class="car"></span>
        <button class="gear" type="button">⚙</button>
      </div>
      <div class="offer">
        <p class="offer-hey">${esc(t.hey(rider))}</p>
        <div class="offer-top">
          <div class="who-row">
            <span class="avatar">${esc(initial)}</span>
            <div><b>${esc(rider)}</b><small>${esc(tx(s.pay))}</small></div>
          </div>
          <div class="price"><b>${esc(s.fare)}</b><span>${esc(s.distance)}</span></div>
        </div>
        <div class="stops">
          <div>
            <i class="stop-dot"></i>
            <div><small>${t.pickupPoint}</small><b>${esc(placeName(s.pickup))}</b><span>${esc(placeName(s.pickupArea))}</span></div>
          </div>
          <div>
            <i class="stop-pin"></i>
            <div><small>${t.dropPoint}</small><b>${esc(placeName(s.dest))}</b><span>${esc(placeName(s.dropArea))}</span></div>
          </div>
        </div>
        <div class="offer-acts">
          <button class="ghost" type="button">${t.decline}</button>
          <button class="primary" type="button">${t.accept}</button>
        </div>
      </div>
      <nav class="tabbar slim">
        <span class="on">${t.home}</span><span>${t.wallet}</span><span>${t.history}</span><span>${t.more}</span>
      </nav>
    </div>`,
    s.label,
    state.lang === "ar"
  );
}
function renderTrip(s) {
  const t = loc();
  const pickup = placeName(looksLikeAddress(s.pickup) ? s.pickup : s.city ? `${s.city} Mall, Downtown` : "Dubai Mall, Financial Centre Rd");
  const drop = placeName(looksLikeAddress(s.dest) ? s.dest : "Marina Walk, JBR");
  const fare = s.fare || s.fee || "";
  return device(
    `<div class="map"><div class="road"></div><div class="road b"></div><div class="pin a"></div><div class="pin b"></div>${fare ? `<div class="fare">${esc(fare)}</div>` : ""}</div>
    <div class="sheet trip-sheet">
      <div class="handle"></div>
      <b>${s.kind === "cancel" ? t.cancelQ : t.hey(s.rider || t.rider.Ahmed)}</b>
      <div class="stops">
        <div><i class="stop-dot"></i><div><small>${t.pickupPoint}</small><b>${esc(pickup)}</b></div></div>
        <div><i class="stop-pin"></i><div><small>${t.dropPoint}</small><b>${esc(drop)}</b></div></div>
      </div>
      ${s.fee ? `<div class="fee"><b>${esc(t.feeNow(s.fee))}</b><span>${t.feeWhy}</span></div>` : ""}
      <div class="offer-acts">
        <button class="ghost" type="button">${s.kind === "cancel" ? t.keep : t.decline}</button>
        <button class="primary" type="button">${s.kind === "cancel" ? t.payCancel(s.fee || fare) : t.accept}</button>
      </div>
    </div>`,
    s.label,
    state.lang === "ar"
  );
}
function renderCancel(s) {
  return renderTrip({ ...s, kind: "cancel" });
}
function renderFailed(s) {
  const amount = s.fare || s.earned || s.amount || "AED 25.00";
  const method = s.method || s.card || "Visa **** 1234";
  return device(
    `<div class="dash failed">
      <div class="fail-mark">!</div>
      <div class="dash-name">${tx("Payment failed")}</div>
      <p class="sheet-sub">${tx("Payment could not be processed")}</p>
      <div class="totals">
        <div class="grand"><span>${tx("Payment details")}</span></div>
        <div><span>${tx("Trip amount")}</span><b>${esc(amount)}</b></div>
        <div><span>${tx("Pay")}</span><b>${esc(tx(method))}</b></div>
      </div>
      <button class="primary" type="button">${tx("Try Again")}</button>
      <button class="secondary" type="button">${tx("Change Payment")}</button>
    </div>`,
    s.label || "Payment failed",
    state.lang === "ar"
  );
}
function renderCheckout(s) {
  const items = asPairs(s.items, "t", "s");
  return device(
    `<div class="dash checkout">
      <span class="dash-hello">${esc(tx(s.store || "Quik"))}</span>
      <div class="dash-name">${esc(tx(s.title || "Checkout"))}</div>
      <div class="slot">${esc(tx(s.slot || "Choose a slot"))}</div>
      <div class="recent">${items.map((x) => `<div class="trip"><b>${esc(tx(x.t))}</b><span>${esc(x.s)}</span></div>`).join("")}</div>
      <div class="totals">
        <div><span>${tx("Subtotal")}</span><b>${esc(s.sub || "")}</b></div>
        <div class="fee-line"><span>${tx("Delivery")}</span><b>${esc(s.fee || "")}</b></div>
        <p class="fee-note">${esc(tx(s.feeNote || ""))}</p>
        <div class="grand"><span>${tx("Total")}</span><b>${esc(s.total || "")}</b></div>
      </div>
      ${s.primary ? `<button class="primary" type="button">${esc(tx(s.primary))}</button>` : ""}
      ${s.secondary ? `<button class="secondary" type="button">${esc(tx(s.secondary))}</button>` : ""}
    </div>`,
    s.label,
    state.lang === "ar"
  );
}
function renderBlock(b) {
  const t = b.type;
  if (t === "hello") return `<span class="dash-hello">${esc(tx(b.kicker || ""))}</span><div class="dash-name">${esc(tx(b.title || ""))}</div>`;
  if (t === "search") return `<div class="where">${esc(tx(b.text || "Search"))}</div>`;
  if (t === "pills") return `<div class="svc">${(b.items || []).map((x) => `<span>${esc(tx(x))}</span>`).join("")}</div>`;
  if (t === "hero") {
    const bars = b.bars || [];
    const max = Math.max(...bars, 1);
    const chart = bars.length ? `<div class="bars">${bars.map((n) => `<i style="height:${Math.round((n / max) * 100)}%"></i>`).join("")}</div>` : "";
    return `<section class="earn"><small>${esc(tx(b.label || ""))}</small><h2>${esc(b.value || "")}</h2><p>${esc(tx(b.meta || ""))}</p>${chart}</section>`;
  }
  if (t === "stats") return `<div class="stats">${(b.items || []).map((x) => `<div class="stat"><b>${esc(x.n)}</b><span>${esc(tx(x.l))}</span></div>`).join("")}</div>`;
  if (t === "split") return `<div class="split">${(b.items || []).map((x) => `<div class="split-row"><b>${esc(tx(x.n))}</b><div class="track"><i style="width:${x.p || 0}%"></i></div></div>`).join("")}</div>`;
  if (t === "list") return `<div class="recent"><b>${esc(tx(b.title || ""))}</b>${(b.items || []).map((x) => `<div class="trip"><b>${esc(tx(x.t))}</b><span>${esc(tx(x.s))}</span></div>`).join("")}</div>`;
  if (t === "note") return `<div class="note-card">${esc(tx(b.text || ""))}</div>`;
  if (t === "map") return `<div class="map"><div class="road"></div><div class="road b"></div><div class="pin a"></div><div class="pin b"></div></div>`;
  if (t === "sheet") {
    return `<div class="sheet"><div class="handle"></div><b>${esc(tx(b.title || ""))}</b><div style="margin:8px 0;color:#5f6368;font-size:12px">${esc(tx(b.sub || ""))}</div>${
      b.fee ? `<div class="fee"><b>${esc(tx(b.fee))}</b><span>${esc(tx(b.feeNote || ""))}</span></div>` : ""
    }${b.primary ? `<button class="primary" type="button">${esc(tx(b.primary))}</button>` : ""}${b.secondary ? `<button class="secondary" type="button">${esc(tx(b.secondary))}</button>` : ""}</div>`;
  }
  if (t === "cta") return `<button class="${b.style === "secondary" ? "secondary" : "primary"}" type="button">${esc(tx(b.text || "Continue"))}</button>`;
  if (t === "tabs") return `<nav class="tabbar">${(b.items || []).map((x, i) => `<span class="${i === 0 ? "on" : ""}">${esc(tx(x))}</span>`).join("")}</nav>`;
  return "";
}
function renderDashboard(s) {
  const weeks = Array.isArray(s.weeks) ? s.weeks : [40, 60, 50, 80];
  const max = Math.max(...weeks, 1);
  const split = asPairs(s.split, "n", "p");
  const trips = asPairs(s.trips, "t", "s");
  return device(
    `<div class="dash"><span class="dash-hello">${esc(tx(s.hello || ""))}</span><div class="dash-name">${esc(tx(s.title || "Home"))}</div>
    ${s.where ? `<div class="where">${esc(tx(s.where))}</div>` : ""}
    ${s.helper ? `<div class="note-card">${esc(tx(s.helper))}</div>` : ""}
    ${s.earned ? `<section class="earn"><small>${esc(tx(s.month || ""))}</small><h2>${esc(s.earned)}</h2><p>${esc(tx(s.delta || ""))}</p>
    ${weeks.length ? `<div class="bars">${weeks.map((n) => `<i style="height:${Math.round((n / max) * 100)}%"></i>`).join("")}</div>` : ""}</section>` : ""}
    ${s.cta ? `<button class="primary" type="button">${esc(tx(s.cta))}</button>` : ""}
    <div class="stats">${(s.stats || []).map((x) => `<div class="stat"><b>${esc(x.n)}</b><span>${esc(tx(x.l))}</span></div>`).join("")}</div>
    ${split.length ? `<div class="split">${split.map((x) => `<div class="split-row"><b>${esc(tx(x.n))}</b><div class="track"><i style="width:${x.p || 0}%"></i></div></div>`).join("")}</div>` : ""}
    ${trips.length ? `<div class="recent"><b>${esc(tx(s.recent_title || "Recent"))}</b>${trips.map((x) => `<div class="trip"><b>${esc(tx(x.t))}</b><span>${esc(tx(x.s))}</span></div>`).join("")}</div>` : ""}
    <nav class="tabbar">${(s.tabs || ["Home", "You"]).map((tab, i) => `<span class="${i === 0 ? "on" : ""}">${esc(tx(tab))}</span>`).join("")}</nav></div>`,
    s.label,
    state.lang === "ar"
  );
}
function renderOne(s) {
  if (!s) return "";
  const kind = screenKind(s);
  if (kind === "accept") return renderAccept(s);
  if (kind === "cancel") return renderCancel(s);
  if (kind === "failed") return renderFailed(s);
  if (kind === "checkout") return renderCheckout(s);
  if (s.blocks && s.blocks.length) {
    const keep = s.blocks.filter((b) => !["split", "note"].includes(b.type)).slice(0, 6);
    return device(`<div class="dash tight">${keep.map(renderBlock).join("")}</div>`, s.label, state.lang === "ar");
  }
  return renderDashboard({ ...s, rtl: state.lang === "ar" });
}

function previewTools() {
  return `<div class="preview-tools">
    <div class="seg">
      <button type="button" data-os="ios" class="${state.os === "ios" ? "on" : ""}">iOS</button>
      <button type="button" data-os="android" class="${state.os === "android" ? "on" : ""}">Android</button>
    </div>
    <div class="seg">
      <button type="button" data-lang="en" class="${state.lang === "en" ? "on" : ""}">EN</button>
      <button type="button" data-lang="ar" class="${state.lang === "ar" ? "on" : ""}">AR</button>
    </div>
  </div>`;
}

function fitPhone() {
  const stage = document.querySelector(".phone-fit");
  const phone = stage && stage.querySelector(".device");
  if (!stage || !phone) return;
  phone.style.transform = "none";
  const scale = Math.min(1, (stage.clientHeight - 4) / phone.offsetHeight, (stage.clientWidth - 8) / phone.offsetWidth);
  phone.style.transform = `scale(${Math.max(0.62, scale)})`;
}

function slider(id, left, right, value) {
  return `<label class="slide"><span>${left}</span><input type="range" min="0" max="100" value="${value}" data-slide="${id}" /><span>${right}</span></label>`;
}

const CHIPS = [
  { label: "Cancel a ride", prompt: "Ride cancellation with the fee visible before they tap" },
  { label: "Rider earnings", prompt: "Rider home with monthly earnings" },
  { label: "Grocery checkout", prompt: "Grocery checkout that shows delivery fee early" },
];

function inferBrief(goal) {
  const q = goal.toLowerCase();
  if (/grocery|food|quik|checkout/.test(q)) state.brief.product = "Quik";
  else if (/pay|wallet|card/.test(q)) state.brief.product = "Pay";
  else state.brief.product = "Rides";
  state.brief.goal = goal;
}

function threadHtml() {
  const rows = state.messages
    .map((m) =>
      m.role === "user"
        ? `<div class="msg user"><div class="bubble">${esc(m.text)}</div></div>`
        : `<div class="msg assistant"><div class="bubble"><div class="who"><span class="mark"></span>Pulse</div><p>${esc(m.text)}</p></div></div>`
    )
    .join("");
  const typing = state.thinking
    ? `<div class="msg assistant"><div class="bubble"><div class="who"><span class="mark"></span>Pulse</div><div class="typing"><i></i><i></i><i></i></div></div></div>`
    : "";
  return rows + typing;
}

function viewBrief() {
  return `<div class="gem-home">
    <h1 class="hello">Hello, Tooba</h1>
    <p class="sub">What should we design for Careem?</p>
    <div class="ideas">${CHIPS.map((s) => `<button class="idea" type="button" data-chip="${esc(s.prompt)}">${esc(s.label)}</button>`).join("")}</div>
  </div>`;
}

function viewChat() {
  return `<div class="gem-thread">${threadHtml()}</div>`;
}

function viewDirections() {
  return `<div class="gem-thread">
    ${threadHtml()}
    <div class="dir-grid">
      ${state.directions
        .map((d) => {
          const preview = state.previews[d.id];
          return `<article class="dir">
        <div class="mini-wrap">${preview ? renderOne(preview) : `<div class="dir-art ${d.id}"></div>`}</div>
        <b>${esc(d.name)}</b>
        <p>${esc(d.promise)}</p>
        <button class="go slim" data-pick="${d.id}" type="button">Use ${esc(d.name)}</button>
      </article>`;
        })
        .join("")}
    </div>
    <button class="idea combine" data-combine="A+C" type="button">Combine Fastest + Guided</button>
  </div>`;
}

function viewWork() {
  const s = state.screen;
  return `<div class="gem-work">
    <div class="gem-thread">
      ${threadHtml()}
      <div class="issues">${state.issues
        .slice(0, 2)
        .map((iss) => `<article><b>${esc(iss.title)}</b><p>${esc(iss.why)}</p></article>`)
        .join("")}</div>
    </div>
    <section class="preview-col">
      ${previewTools()}
      <div class="phone-fit" id="phone">${s ? renderOne(s) : ""}</div>
    </section>
  </div>`;
}

function layerEditor(block, i) {
  const text = block.text || block.title || block.value || block.primary || block.kicker || "";
  return `<div class="inspector">
    <p>Component <code>${esc(COMPONENTS[block.type] || block.type)}</code></p>
    <label>Copy<input data-edit="copy" data-i="${i}" value="${esc(text)}" /></label>
    <div class="row">
      <button type="button" data-space="16" data-i="${i}">Spacing 16</button>
      <button type="button" data-space="24" data-i="${i}">Spacing 24</button>
      <button type="button" data-swap="sheet" data-i="${i}">Use bottom sheet</button>
    </div>
  </div>`;
}

function viewFlow() {
  const f = state.flow;
  return `<div class="flow-page">
    <h1 class="hello">Flows, not just screens.</h1>
    <div class="flow-line">${(f.steps || []).map((s) => `<span>${esc(s)}</span><i></i>`).join("")}</div>
    <h3>UX problems</h3>
    ${(f.problems || []).map((p) => `<article class="detail-card"><h3>⚠ ${esc(p.flag)}</h3><p>${esc(p.fix)}</p></article>`).join("")}
    <button class="go" id="missingBtn" type="button">Generate missing failure states</button>
  </div>`;
}

function viewDna() {
  return `<div class="brief">
    <h1 class="hello">Style Memory</h1>
    <p class="sub">You control what I learn. Sliders are yours. Observed items only stay if you kept them.</p>
    ${slider("density", "Dense", "Spacious", state.dna.density)}
    ${slider("corners", "Sharp", "Rounded", state.dna.corners)}
    ${slider("hierarchy", "Minimal", "Expressive", state.dna.hierarchy)}
    ${slider("copy", "Concise", "Conversational", state.dna.copy)}
    ${slider("interaction", "Direct", "Guided", state.dna.interaction)}
    <h3>Observed preferences</h3>
    <ul class="obs">${state.dna.observed.map((n) => `<li>✓ ${esc(n)}</li>`).join("")}</ul>
    <p class="sub">Careem DNA stays on: 8px grid, sheets, max 2 CTAs, fee before the tap.</p>
  </div>`;
}

function setBusy(on, msg) {
  state.thinking = on;
  document.body.classList.toggle("thinking", on);
  const el = document.getElementById("busy");
  if (el) {
    el.hidden = true;
    const text = document.getElementById("busyText");
    if (text) text.textContent = msg || "Designing…";
  }
  const send = document.getElementById("sendBtn");
  if (send) send.disabled = on;
  const input = document.getElementById("askInput");
  if (input) {
    input.disabled = on;
    if (msg) input.placeholder = msg;
    if (!on) input.placeholder = state.screen ? "Change the copy, spacing, or layout…" : "Ask Pulse to design a Careem screen";
  }
}

function paintDna() {
  const box = document.getElementById("dnaBody");
  if (!box) return;
  box.innerHTML = `
    ${slider("density", "Dense", "Spacious", state.dna.density)}
    ${slider("corners", "Sharp", "Rounded", state.dna.corners)}
    ${slider("hierarchy", "Minimal", "Expressive", state.dna.hierarchy)}
    ${slider("copy", "Concise", "Conversational", state.dna.copy)}
    ${slider("interaction", "Direct", "Guided", state.dna.interaction)}
    <h4>Observed</h4>
    <ul class="obs">${state.dna.observed.map((n) => `<li>✓ ${esc(n)}</li>`).join("")}</ul>
    <p class="sub">Careem stays on: 8px grid, sheets, max 2 CTAs, fee before the tap.</p>`;
}

function applyDna() {
  const r = 10 + Math.round(state.dna.corners / 10);
  document.documentElement.style.setProperty("--card-r", `${r}px`);
}

function render() {
  const app = document.getElementById("app");
  const views = { brief: viewBrief, chat: viewChat, directions: viewDirections, work: viewWork, flow: viewFlow, dna: viewDna };
  app.innerHTML = (views[state.view] || viewBrief)();
  applyDna();
  paintDna();
  const chip = document.getElementById("dnaChip");
  if (chip) chip.textContent = `DNA · ${labelOf(state.dna.density, "dense", "spacious")}`;
  const tabs = document.getElementById("projTabs");
  if (tabs) tabs.hidden = !(state.directions.length || state.screen);
  const bar = document.getElementById("learnBar");
  if (state.pendingLearn) {
    bar.hidden = false;
    document.getElementById("learnText").textContent = state.pendingLearn.text;
  } else if (bar) bar.hidden = true;
  const input = document.getElementById("askInput");
  if (input && !state.thinking) {
    input.placeholder = state.screen ? "Change the copy, spacing, or layout…" : "Ask Pulse to design a Careem screen";
  }
  paintHistory();
  const thread = app.querySelector(".gem-thread");
  if (thread) thread.scrollTop = thread.scrollHeight;
  requestAnimationFrame(fitPhone);
}

async function start(goal) {
  const text = (goal || document.getElementById("askInput").value || "").trim();
  if (!text || state.thinking) return;
  inferBrief(text);
  document.getElementById("askInput").value = "";
  state.messages = [{ role: "user", text }];
  state.view = "chat";
  setBusy(true, "Reading the brief…");
  render();
  try {
    const res = await fetch("/api/studio", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ action: "start", brief: state.brief, dna: state.dna }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Start failed");
    state.directions = data.directions || [];
    state.previews = data.previews || {};
    state.reply = data.reply;
    state.issues = data.issues || [];
    state.flow = data.flow || state.flow;
    state.view = "directions";
    state.messages = [{ role: "user", text: text }, { role: "studio", text: state.reply }];
    saveChat();
  } catch (err) {
    state.view = "brief";
    state.reply = err.message;
    alert(err.message);
  }
  setBusy(false);
  render();
}

async function pick(id, combine) {
  if (state.thinking) return;
  state.messages.push({ role: "user", text: `Use ${combine || id}` });
  state.view = "chat";
  setBusy(true, "Building that direction…");
  render();
  try {
    const res = await fetch("/api/studio", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ action: "pick", brief: state.brief, direction: id, combine, dna: state.dna }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Pick failed");
    state.picked = combine || id;
    state.screen = data.screen;
    state.tree = data.tree || [];
    state.issues = data.issues || [];
    state.flow = data.flow || state.flow;
    state.reply = data.reply;
    state.view = "work";
    state.messages.push({ role: "studio", text: state.reply });
    saveChat();
  } catch (err) {
    state.view = state.screen ? "work" : "directions";
    alert(err.message);
  }
  setBusy(false);
  render();
}

function proposeLearn(text) {
  state.pendingLearn = { text };
  render();
}

document.body.addEventListener("click", (e) => {
  if (e.target.id === "newChat" || e.target.closest("#newChat")) {
    newChat();
    return;
  }
  const del = e.target.closest("[data-del]");
  if (del) {
    deleteChat(del.dataset.del);
    return;
  }
  const chat = e.target.closest("[data-chat]");
  if (chat) {
    openChat(chat.dataset.chat);
    return;
  }
  if (e.target.id === "dnaChip" || e.target.closest("#dnaChip") || e.target.id === "dnaClose") {
    const drawer = document.getElementById("dnaDrawer");
    if (drawer) drawer.hidden = !drawer.hidden;
    return;
  }
  const nav = { navBrief: "brief", navDirs: "directions", navWork: "work", navFlow: "flow", navDna: "dna" };
  if (e.target.id && nav[e.target.id]) {
    if (e.target.id === "navDirs" && !state.directions.length) return;
    if (e.target.id === "navWork" && !state.screen) return;
    if (e.target.id === "navDna") {
      const drawer = document.getElementById("dnaDrawer");
      if (drawer) drawer.hidden = false;
      return;
    }
    state.view = nav[e.target.id];
    render();
    return;
  }
  const mode = e.target.closest("[data-mode]");
  if (mode) {
    state.mode = mode.dataset.mode;
    render();
    return;
  }
  const sk = e.target.closest("[data-sk]");
  if (sk) {
    const name = sk.dataset.sk;
    if (state.sketch.includes(name)) state.sketch = state.sketch.filter((x) => x !== name);
    else state.sketch.push(name);
    render();
    return;
  }
  const chip = e.target.closest("[data-chip]");
  if (chip) {
    start(chip.dataset.chip);
    return;
  }
  const pickBtn = e.target.closest("[data-pick]");
  if (pickBtn) {
    pick(pickBtn.dataset.pick);
    return;
  }
  if (e.target.closest("[data-combine]")) {
    pick("A", "A+C");
    return;
  }
  const os = e.target.closest("[data-os]");
  if (os) {
    state.os = os.dataset.os;
    state.brief.platform = state.os === "android" ? "Android" : "iOS";
    render();
    return;
  }
  const lang = e.target.closest("[data-lang]");
  if (lang) {
    state.lang = lang.dataset.lang;
    state.brief.language = state.lang === "ar" ? "AR" : "EN";
    render();
    return;
  }
  const layer = e.target.closest("[data-layer]");
  if (layer) {
    state.selectedLayer = Number(layer.dataset.layer);
    render();
    return;
  }
  if (e.target.dataset.space) {
    proposeLearn(`You changed spacing to ${e.target.dataset.space}px in transactional UI.`);
    if (e.target.dataset.space === "16") state.dna.density = Math.max(10, state.dna.density - 15);
    render();
    return;
  }
  if (e.target.dataset.swap === "sheet") {
    const i = Number(e.target.dataset.i);
    if (state.screen && state.screen.blocks && state.screen.blocks[i]) {
      const prev = state.screen.blocks[i];
      state.screen.blocks[i] = { type: "sheet", title: prev.title || prev.text || "Confirm?", primary: "Keep", secondary: "Cancel" };
      proposeLearn("You prefer bottom sheets over cards for decisions.");
      render();
    }
    return;
  }
  if (e.target.id === "missingBtn") {
    const steps = state.flow.steps || [];
    if (!steps.includes("Failed")) state.flow.steps = [...steps, "Failed", "Retry"];
    state.flow.problems = state.flow.problems.filter((p) => !/fail/i.test(p.flag));
    proposeLearn("You asked for missing failure states before happy-path polish.");
    render();
    return;
  }
  if (e.target.id === "stressBtn") {
    state.view = "work";
    if (state.issues.length) state.reply = "Stress: empty, Arabic, and fee-visible states. " + (state.issues[0] || {}).title;
    render();
    return;
  }
  if (e.target.id === "handBtn") {
    state.view = "work";
    state.reply = `Handoff ready · ${state.picked || "unpicked"} · Careem components only · DNA ${labelOf(state.dna.copy, "concise", "conversational")} copy · ${state.dna.observed.slice(0, 3).join(" · ")}`;
    render();
  }
});

document.body.addEventListener("input", (e) => {
  if (e.target.dataset.slide) {
    state.dna[e.target.dataset.slide] = Number(e.target.value);
    persist();
    return;
  }
  if (e.target.dataset.edit === "copy") {
    const i = Number(e.target.dataset.i);
    const next = e.target.value;
    const block = state.screen && state.screen.blocks && state.screen.blocks[i];
    if (!block) return;
    const prev = block.text || block.title || block.primary || "";
    if (block.primary) block.primary = next;
    else if (block.title) block.title = next;
    else if (block.value) block.value = next;
    else block.text = next;
    if (next.length + 4 < prev.length) proposeLearn("You consistently shorten microcopy. Prefer concise CTAs.");
  }
});

document.body.addEventListener("change", (e) => {
  if (e.target.dataset.slide) {
    persist();
    render();
  }
});

function isLocaleOnly(q) {
  return /^(please )?(give me |show (me )?)?(the )?(arabic|english|ar|en|rtl)( version)?[.!]?$/i.test(q.trim());
}

async function refine(q) {
  if (!q || state.thinking) return;
  if (isLocaleOnly(q)) {
    state.lang = /arabic|rtl|\bar\b/i.test(q) ? "ar" : "en";
    state.brief.language = state.lang === "ar" ? "AR" : "EN";
    state.messages.push(
      { role: "user", text: q },
      { role: "studio", text: state.lang === "ar" ? "Arabic, right-to-left. Same screen — use the AR toggle anytime." : "English. Same screen — use the EN toggle anytime." }
    );
    state.reply = state.messages.slice(-1)[0].text;
    saveChat();
    render();
    return;
  }
  state.messages.push({ role: "user", text: q });
  const input = document.getElementById("askInput");
  if (input) input.value = "";
  setBusy(true, "Adapting the screen…");
  render();
  try {
    const res = await fetch("/api/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question: `${state.brief.goal}. ${q}`, dna: state.dna, history: state.messages.slice(-6) }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Ask failed");
    state.screen = data.screen || state.screen;
    if (screenKind(state.screen) === "accept") state.screen = { ...mergeAccept(state.screen), kind: "accept" };
    state.reply = data.reply;
    state.view = "work";
    if (data.critic) state.issues = [{ title: data.critic.note, why: "Critic vs Careem + your style.", layer: "Consistency" }];
    state.messages.push({ role: "studio", text: state.reply });
    saveChat();
  } catch (err) {
    alert(err.message);
  }
  setBusy(false);
  render();
}

document.getElementById("ask").addEventListener("submit", (e) => {
  e.preventDefault();
  const q = document.getElementById("askInput").value.trim();
  if (!q) return;
  if (state.view === "work" && state.screen) refine(q);
  else start(q);
});

document.body.addEventListener("submit", (e) => {
  if (e.target.id !== "refine") return;
  e.preventDefault();
  refine(e.target.q.value.trim());
  e.target.q.value = "";
});

document.getElementById("learnBar").addEventListener("click", (e) => {
  const act = e.target.dataset.learn;
  if (!act || !state.pendingLearn) return;
  if (act === "keep") {
    if (!state.dna.observed.includes(state.pendingLearn.text)) state.dna.observed.push(state.pendingLearn.text);
    persist();
  }
  if (act === "project") state.dna.projectOnly.push(state.pendingLearn.text);
  state.pendingLearn = null;
  render();
});

window.addEventListener("resize", fitPhone);
load();
render();
{
  const params = new URLSearchParams(location.search);
  const go = params.get("go");
  if (go) start(go).then(() => { if (params.get("pick")) pick(params.get("pick")); });
  if (params.get("demo") === "accept") {
    state.view = "work";
    state.brief.goal = "Design an accept ride screen";
    state.screen = {
      kind: "accept",
      label: "Accept · Dubai",
      rider: "Ahmed",
      pay: "Careem Pay",
      pickup: "Dubai Mall, Financial Centre Rd",
      pickupArea: "Downtown Dubai",
      dest: "Marina Walk, JBR",
      dropArea: "Dubai Marina",
      fare: "AED 45.00",
      distance: "2.3 km",
    };
    state.messages = [
      { role: "user", text: "Design an accept ride screen" },
      { role: "studio", text: "Map plus a sheet. Fare stays visible. Two actions only." },
    ];
    render();
  }
}
