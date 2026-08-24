const KEY = "careem-studio-v2";
const COMPONENTS = {
  hello: "Text/Title",
  search: "WhereTo",
  location: "LocationChip",
  pills: "ChipRow",
  categories: "CategoryChipRow",
  offer: "OfferBanner",
  section: "SectionHeader",
  restaurants: "RestaurantCard",
  hero: "EarningsCard",
  stats: "StatRow",
  split: "SplitBar",
  list: "ListRow",
  note: "HelperText",
  map: "Map",
  sheet: "Sheet",
  captain: "CaptainRow",
  trip: "TripSummary",
  rating: "StarRating",
  tips: "TipChips",
  totals: "TotalsBlock",
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
    flow: "",
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
  designSystem: null,
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
  showMorePrompts: false,
  flowScreens: {},
};

function load() {
  try {
    const saved = JSON.parse(localStorage.getItem(KEY) || "{}");
    if (saved.dna) state.dna = { ...state.dna, ...saved.dna };
    if (saved.brief) state.brief = { ...state.brief, ...saved.brief };
    if (saved.chats) state.chats = saved.chats;
    if (saved.chatId) state.chatId = saved.chatId;
    if (saved.lang) state.lang = saved.lang;
    else if (state.brief.language) state.lang = state.brief.language === "AR" ? "ar" : "en";
  } catch {}
}
function persist() {
  localStorage.setItem(
    KEY,
    JSON.stringify({ dna: state.dna, brief: state.brief, chats: state.chats, chatId: state.chatId, lang: state.lang })
  );
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
      designSystem: state.designSystem,
      reply: state.reply,
      messages: state.messages,
      os: state.os,
      lang: state.lang,
      flowScreens: state.flowScreens,
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
  state.flow = { steps: [], problems: [] };
  state.flowScreens = {};
  state.designSystem = null;
  state.reply = "";
  state.pendingLearn = null;
  state.selectedLayer = -1;
  state.os = "ios";
  state.lang = "en";
  state.brief.language = "EN";
  state.view = "brief";
  const input = document.getElementById("askInput");
  if (input) input.value = "";
  setDnaOpen(false);
  setHistOpen(false);
  render();
}
function openChat(id) {
  const item = state.chats.find((c) => c.id === id);
  if (!item || !item.snap) return;
  Object.assign(state, item.snap);
  state.chatId = id;
  setHistOpen(false);
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
    arriving: (n, eta) => `${n} is ${eta} away`,
    pickupPoint: "Pickup point",
    dropPoint: "Drop-off point",
    accept: "Accept",
    decline: "Decline",
    call: "Call",
    message: "Message",
    cancelRide: "Cancel ride",
    plate: "Plate",
    rating: "Rating",
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
    arriving: (n, eta) => `${n} يبعد ${eta}`,
    pickupPoint: "نقطة الانطلاق",
    dropPoint: "نقطة الوصول",
    accept: "قبول",
    decline: "رفض",
    call: "اتصال",
    message: "رسالة",
    cancelRide: "إلغاء المشوار",
    plate: "اللوحة",
    rating: "التقييم",
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
  "Trip complete": "المشوار خلص",
  Payment: "الدفع",
  Done: "تم",
  "View receipt": "عرض الإيصال",
  "Any feedback? (optional)": "ملاحظات؟ (اختياري)",
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
  "Cancel ride": "إلغاء المشوار",
  Call: "اتصال",
  Message: "رسالة",
  Plate: "اللوحة",
  "Captain is arriving": "الكابتن في الطريق",
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
  "We couldn't process your payment": "ما قدرنا نعالج الدفع",
  "We couldn’t process your payment": "ما قدرنا نعالج الدفع",
  "Your card was declined. Please try again or use a different payment method.": "البطاقة انرفضت. جرّب مرة ثانية أو غيّر طريقة الدفع.",
  "Trip Details": "تفاصيل المشوار",
  "Payment Method": "طريقة الدفع",
  "Change Payment Method": "غيّر طريقة الدفع",
  "Need help? Contact Support": "تحتاج مساعدة؟ تواصل مع الدعم",
  "Try again": "حاول مرة ثانية",
};

const AR_RE = /[\u0600-\u06FF]/;
const EN_FROM_AR = Object.fromEntries(Object.entries(AR_MAP).map(([en, ar]) => [ar, en]));

function asLabel(value) {
  if (value == null) return "";
  if (typeof value === "string" || typeof value === "number") return String(value);
  if (typeof value === "object") return value.label || value.name || value.text || value.title || value.t || value.value || "";
  return "";
}
function tx(text) {
  if (text == null) return "";
  let raw = asLabel(text).replace(/\s+/g, " ").trim();
  if (!raw) return "";
  const arabic = AR_RE.test(raw);
  const latin = /[A-Za-z]/.test(raw);
  if (state.lang !== "ar") {
    if (!arabic) return raw;
    if (EN_FROM_AR[raw]) return EN_FROM_AR[raw];
    const onlyAr = raw.replace(/[^\u0600-\u06FF\s]/g, "").trim();
    if (EN_FROM_AR[onlyAr]) return EN_FROM_AR[onlyAr];
    return raw.replace(/[\u0600-\u06FF]+/g, "").replace(/\s{2,}/g, " ").trim();
  }
  if (AR_MAP[raw]) return AR_MAP[raw];
  const exact = Object.keys(AR_MAP).find((k) => k.toLowerCase() === raw.toLowerCase());
  if (exact) return AR_MAP[exact];
  if (arabic && latin) {
    const onlyAr = raw.replace(/[^\u0600-\u06FF\s]/g, "").trim();
    return onlyAr || raw;
  }
  return raw;
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
function inferKindFromText(q) {
  const t = `${q || ""}`.toLowerCase();
  if (/super app|service grid|services hub|home hub/.test(t)) return "superapp";
  if (/driver arriving|captain arriving|arriving screen|on the way|pickup progress|license plate|estimated arrival|vehicle details/.test(t)) return "arriving";
  if (/accept ride|accept this ride|incoming ride|ride request/.test(t)) return "accept";
  if (/payment failed|try again|could not be processed/.test(t)) return "failed";
  if (/ride completed|ride complete|trip completed|trip complete|trip summary|final fare|rate your|rate the driver|leave a tip|optional tip|trip receipt|receipt screen|rating experience|how was your trip|ride finished/.test(t)) return "completed";
  if (/food cart|food checkout|restaurant cart|careem food cart/.test(t) || (/cart/.test(t) && /food|restaurant|burger|dish/.test(t))) return "food";
  if (/food home|careem food home|discover what to eat|restaurant recommendation|food categor|popular dishes|restaurant cards|promo banner|what to eat|search restaurants|delivery location/.test(t)) return "food";
  if (/grocery|quik cart|quik checkout/.test(t) || (/checkout/.test(t) && /grocery|quik|slot/.test(t))) return "checkout";
  if (/monthly earnings|rider home|home dashboard/.test(t)) return "home";
  if (/cancel this ride|cancel ride screen|cancellation/.test(t) && !/arriv|accept ride|payment failed/.test(t)) return "cancel";
  return "";
}
function screenKind(s) {
  const inferred = inferKindFromText(state.brief.goal);
  const locked = s && s.kind;
  if (locked === "dashboard") return inferred === "home" ? "home" : inferred || "generic";
  if (locked && ["arriving", "accept", "cancel", "failed", "checkout", "completed", "food", "home", "superapp"].includes(locked)) return locked;
  return inferred || (s && s.blocks && s.blocks.length ? "generic" : inferred || "generic");
}
function projectKind() {
  const product = (state.brief.product || "").toLowerCase();
  const inferred = inferKindFromText(state.brief.goal);
  if (product === "super app" && (!inferred || inferred === "food" || inferred === "home")) return "superapp";
  if (product === "food" && (!inferred || inferred === "home" || inferred === "generic" || inferred === "checkout")) return "food";
  return inferred || (state.screen && screenKind(state.screen)) || "generic";
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
    screenRtl()
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
    screenRtl()
  );
}
function renderCancel(s) {
  return renderTrip({ ...s, kind: "cancel" });
}
function renderArriving(raw) {
  const t = loc();
  const name = raw.captain || "Yousef";
  const eta = raw.eta || "3 min";
  const progress = Math.max(8, Math.min(100, Number(raw.progress) || 68));
  return device(
    `<div class="map"><div class="road"></div><div class="road b"></div><div class="pin a"></div><div class="pin b"></div><div class="fare">${esc(raw.fare || "")}</div><div class="eta-chip">${esc(eta)}</div></div>
    <div class="sheet trip-sheet">
      <div class="handle"></div>
      <div class="offer-top">
        <div class="who-row">
          <span class="avatar">${esc(name[0])}</span>
          <div><b>${esc(name)}</b><small>★ ${esc(raw.rating || "4.9")} · ${esc(tx(raw.car || "White Toyota Camry"))}</small></div>
        </div>
        <div class="price"><b>${esc(raw.plate || "")}</b><span>${t.plate}</span></div>
      </div>
      <p class="offer-hey">${esc(t.arriving(name, eta))}</p>
      ${raw.helper ? `<p class="sheet-note">${esc(tx(raw.helper))}</p>` : ""}
      <div class="arrive-track"><i style="width:${progress}%"></i></div>
      <div class="stops">
        <div><i class="stop-dot"></i><div><small>${t.pickupPoint}</small><b>${esc(placeName(raw.pickup || "Dubai Mall, Financial Centre Rd"))}</b></div></div>
      </div>
      <div class="offer-acts">
        <button class="primary" type="button">${t.call}</button>
        <button class="ghost" type="button">${t.message}</button>
      </div>
      <button class="linkish" type="button">${t.cancelRide}</button>
    </div>`,
    raw.label || "Arriving",
    screenRtl()
  );
}
function renderFailed(s) {
  const amount = s.fare || s.earned || s.amount || "AED 25.00";
  const method = s.method || s.card || "Visa **** 1234";
  const rows = s.rows && s.rows.length ? s.rows : [
    { label: "Trip amount", value: amount },
    { label: "Pay", value: method },
  ];
  const helper = s.helper || s.note || "";
  const sub = s.sub || "Payment could not be processed";
  return device(
    `<div class="dash failed">
      <div class="fail-mark">!</div>
      <div class="dash-name">${tx("Payment failed")}</div>
      <p class="sheet-sub">${tx(sub)}</p>
      ${helper ? `<div class="note-card">${esc(tx(helper))}</div>` : ""}
      <div class="totals">
        <div class="grand"><span>${tx("Payment details")}</span></div>
        ${rows.map((r) => `<div><span>${esc(tx(r.label || r.t || ""))}</span><b>${esc(tx(r.value || r.s || ""))}</b></div>`).join("")}
      </div>
      <button class="primary" type="button">${tx("Try Again")}</button>
      <button class="secondary" type="button">${tx("Change Payment")}</button>
    </div>`,
    s.label || "Payment failed",
    screenRtl()
  );
}
function renderCompleted(raw) {
  const s = raw || {};
  const tips = (s.tips || ["AED 5", "AED 10", "AED 15"]).slice(0, 3);
  const name = s.captain || "Yousef";
  return device(
    `<div class="dash completed">
      <span class="dash-hello">${tx("Trip complete")}</span>
      <div class="dash-name">${esc(s.fare || "AED 32.50")}</div>
      <p class="sheet-sub">${esc(s.duration || "24 min")} · ${esc(s.distance || "12.4 km")}</p>
      <div class="totals compact">
        <div><span>${loc().pickupPoint}</span><b>${esc(placeName(s.pickup || "Dubai Mall, Financial Centre Rd"))}</b></div>
        <div><span>${loc().dropPoint}</span><b>${esc(placeName(s.dest || "Marina Walk, JBR"))}</b></div>
        <div><span>${tx("Payment")}</span><b>${esc(tx(s.method || "Careem Pay"))}</b></div>
      </div>
      <div class="captain-row">
        <span class="avatar">${esc(name[0])}</span>
        <div><b>${esc(name)}</b><small>★ ${esc(s.rating || "4.9")} · ${esc(tx(s.car || "White Toyota Camry"))}</small></div>
      </div>
      <div class="stars" aria-label="Rating"><span class="on">★</span><span class="on">★</span><span class="on">★</span><span class="on">★</span><span>★</span></div>
      <div class="tip-row">${tips.map((tip, i) => `<button type="button" class="tip-chip${i === 1 ? " on" : ""}">${esc(tip)}</button>`).join("")}</div>
      <input class="feedback" type="text" placeholder="${tx("Any feedback? (optional)")}" readonly />
      <button class="primary" type="button">${tx(s.primary || "Done")}</button>
      ${s.secondary ? `<button class="ghost full" type="button">${tx(s.secondary)}</button>` : ""}
    </div>`,
    s.label || "Trip complete",
    screenRtl()
  );
}
function renderFoodCard(r) {
  const card = typeof r === "object" && r ? r : { name: asLabel(r) };
  const name = asLabel(card.name || card.title || card.t);
  if (!name) return "";
  return `<article class="food-card">
    <div class="food-img">${card.tag ? `<span class="food-tag">${esc(asLabel(card.tag))}</span>` : ""}</div>
    <b>${esc(name)}</b>
    <small>★ ${esc(asLabel(card.rating) || "4.8")} · ${esc(asLabel(card.eta) || "25 min")}${card.from ? ` · ${esc(asLabel(card.from))}` : ""}</small>
    ${card.dish ? `<span class="food-dish">${esc(asLabel(card.dish))}</span>` : ""}
  </article>`;
}
function renderFoodHome(raw) {
  const s = raw || {};
  const sections = s.sections || [{ title: "For you", items: s.restaurants || [] }];
  const cats = (s.categories || ["Burgers", "Healthy", "Arabic"]).slice(0, 6);
  return device(
    `<div class="dash food-home">
      <div class="food-loc"><span class="pin"></span>${esc(placeName(s.location || "Marina Walk, JBR"))}</div>
      <div class="where">${esc(tx(s.search || "Search restaurants or dishes"))}</div>
      <div class="food-cats">${cats.map((c, i) => `<span class="${i === 0 ? "on" : ""}">${esc(tx(c))}</span>`).join("")}</div>
      ${s.offer ? `<div class="food-offer">${esc(tx(s.offer))}</div>` : ""}
      ${s.helper ? `<div class="note-card">${esc(tx(s.helper))}</div>` : ""}
      ${sections
        .map(
          (sec) => `<h3 class="food-section">${esc(tx(sec.title))}</h3>
        <div class="food-cards">${(sec.items || []).map(renderFoodCard).join("")}</div>`
        )
        .join("")}
      <nav class="tabbar slim">${(s.tabs || ["Food", "Search", "Orders", "You"]).map((tab, i) => `<span class="${i === 0 ? "on" : ""}">${esc(tx(tab))}</span>`).join("")}</nav>
    </div>`,
    s.label || "Food",
    screenRtl()
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
    screenRtl()
  );
}
function screenRtl() {
  return state.lang === "ar";
}
function renderBlock(b) {
  const t = b.type;
  if (t === "hello") return `<span class="dash-hello">${esc(tx(b.kicker || ""))}</span><div class="dash-name">${esc(tx(b.title || ""))}</div>`;
  if (t === "location") return `<div class="food-loc"><span class="pin"></span>${esc(tx(b.text || ""))}</div>`;
  if (t === "search") return `<div class="where">${esc(tx(b.text || "Search"))}</div>`;
  if (t === "pills") {
    const items = (b.items || []).map(asLabel).filter(Boolean);
    const serviceHits = items.filter((x) => /^(rides|food|quik|pay|shops|plus|bike|box|rent|dineout)$/i.test(x)).length;
    const grid = serviceHits >= 3 || /super app|service grid/i.test(state.brief.goal || "");
    if (grid) {
      return `<div class="service-grid">${items
        .map((x, i) => `<button type="button" class="svc-tile${i === 0 ? " on" : ""}"><i>${esc(x[0] || "")}</i><span>${esc(tx(x))}</span></button>`)
        .join("")}</div>`;
    }
    return `<div class="svc">${items.map((x) => `<span>${esc(tx(x))}</span>`).join("")}</div>`;
  }
  if (t === "categories") return `<div class="food-cats">${(b.items || []).map(asLabel).filter(Boolean).map((x, i) => `<span class="${i === 0 ? "on" : ""}">${esc(tx(x))}</span>`).join("")}</div>`;
  if (t === "offer") return `<div class="food-offer">${esc(tx(b.text || ""))}</div>`;
  if (t === "section") return `<h3 class="food-section">${esc(tx(b.title || ""))}</h3>`;
  if (t === "restaurants") {
    const items = b.items || [];
    return `${b.title ? `<h3 class="food-section">${esc(tx(b.title))}</h3>` : ""}<div class="food-cards">${items.map((r) => renderFoodCard(r)).join("")}</div>`;
  }
  if (t === "captain") {
    const name = b.name || "Captain";
    return `<div class="captain-row"><span class="avatar">${esc(name[0])}</span><div><b>${esc(name)}</b><small>★ ${esc(b.rating || "4.9")}${b.car ? ` · ${esc(tx(b.car))}` : ""}${b.plate ? ` · ${esc(b.plate)}` : ""}</small></div></div>`;
  }
  if (t === "trip") {
    const duration = asLabel(b.duration).replace(/trip/gi, "").trim();
    const distance = asLabel(b.distance).replace(/trip/gi, "").trim();
    const meta = [duration, distance].filter(Boolean).join(" · ");
    return `<div class="totals compact">
      ${b.pickup ? `<div><span>${loc().pickupPoint}</span><b>${esc(placeName(asLabel(b.pickup)))}</b></div>` : ""}
      ${b.dest ? `<div><span>${loc().dropPoint}</span><b>${esc(placeName(asLabel(b.dest)))}</b></div>` : ""}
      ${b.fare ? `<div><span>${tx("Trip amount")}</span><b>${esc(asLabel(b.fare))}</b></div>` : ""}
      ${b.method ? `<div><span>${tx("Payment")}</span><b>${esc(tx(asLabel(b.method)))}</b></div>` : ""}
      ${meta ? `<div><span>Trip</span><b>${esc(meta)}</b></div>` : ""}
    </div>`;
  }
  if (t === "rating") {
    const n = Math.max(0, Math.min(5, Number(b.value) || 4));
    return `<div class="stars">${[1, 2, 3, 4, 5].map((i) => `<span class="${i <= n ? "on" : ""}">★</span>`).join("")}</div>`;
  }
  if (t === "tips") {
    return `<div class="tip-row">${(b.items || []).map(asLabel).filter(Boolean).map((tip, i) => `<button type="button" class="tip-chip${i === 1 ? " on" : ""}">${esc(tip)}</button>`).join("")}</div>`;
  }
  if (t === "totals") {
    const rows = b.rows || b.items || [];
    return `<div class="totals">${rows.map((r) => `<div><span>${esc(tx(r.label || r.t || ""))}</span><b>${esc(tx(r.value || r.s || ""))}</b></div>`).join("")}</div>`;
  }
  if (t === "hero") {
    const wantsEarnings = /earnings|monthly|dashboard|cashback|spent|analytics/.test((state.brief.goal || "").toLowerCase());
    const bars = wantsEarnings ? b.bars || [] : [];
    const max = Math.max(...bars, 1);
    const chart = bars.length ? `<div class="bars">${bars.map((n) => `<i style="height:${Math.round((n / max) * 100)}%"></i>`).join("")}</div>` : "";
    if (!wantsEarnings && !chart) {
      return `<div class="food-offer">${esc(tx(b.meta || b.value || b.label || "Offer"))}</div>`;
    }
    return `<section class="earn"><small>${esc(tx(b.label || ""))}</small><h2>${esc(b.value || "")}</h2><p>${esc(tx(b.meta || ""))}</p>${chart}</section>`;
  }
  if (t === "stats") return `<div class="stats">${(b.items || []).map((x) => `<div class="stat"><b>${esc(x.n)}</b><span>${esc(tx(x.l))}</span></div>`).join("")}</div>`;
  if (t === "split") return `<div class="split">${(b.items || []).map((x) => `<div class="split-row"><b>${esc(tx(x.n))}</b><div class="track"><i style="width:${x.p || 0}%"></i></div></div>`).join("")}</div>`;
  if (t === "list") {
    const items = b.items || [];
    if (items.some((x) => x && typeof x === "object" && (x.rating || x.eta || x.from || x.dish))) {
      return `${b.title ? `<h3 class="food-section">${esc(tx(b.title))}</h3>` : ""}<div class="food-cards">${items.map(renderFoodCard).join("")}</div>`;
    }
    return `<div class="recent"><b>${esc(tx(b.title || ""))}</b>${items
      .map((x) => {
        const row = typeof x === "object" && x ? x : { t: asLabel(x), s: "" };
        return `<div class="trip"><b>${esc(tx(asLabel(row.t || row.name || row.title)))}</b><span>${esc(tx(asLabel(row.s || row.meta)))}</span></div>`;
      })
      .join("")}</div>`;
  }
  if (t === "note") return `<div class="note-card">${esc(tx(b.text || ""))}</div>`;
  if (t === "map") return `<div class="map"><div class="road"></div><div class="road b"></div><div class="pin a"></div><div class="pin b"></div></div>`;
  if (t === "sheet") {
    return `<div class="sheet"><div class="handle"></div><b>${esc(tx(b.title || ""))}</b><div style="margin:8px 0;color:#5f6368;font-size:12px">${esc(tx(b.sub || ""))}</div>${
      b.fee ? `<div class="fee"><b>${esc(tx(b.fee))}</b><span>${esc(tx(b.feeNote || ""))}</span></div>` : ""
    }${b.primary ? `<button class="primary" type="button">${esc(tx(b.primary))}</button>` : ""}${b.secondary ? `<button class="secondary" type="button">${esc(tx(b.secondary))}</button>` : ""}</div>`;
  }
  if (t === "cta") return `<button class="${b.style === "secondary" ? "secondary" : "primary"}" type="button">${esc(tx(asLabel(b.text) || "Continue"))}</button>`;
  if (t === "tabs") return `<nav class="tabbar">${(b.items || []).map(asLabel).filter(Boolean).map((x, i) => `<span class="${i === 0 ? "on" : ""}">${esc(tx(x))}</span>`).join("")}</nav>`;
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
    screenRtl()
  );
}
function renderFromBlocks(s) {
  const blocks = Array.isArray(s.blocks) ? s.blocks : [];
  const scroll = blocks.length > 6 || blocks.some((b) => ["restaurants", "list", "map"].includes(b.type));
  return device(
    `<div class="dash ${scroll ? "scrollish" : "tight"}">${blocks.map(renderBlock).join("")}</div>`,
    s.label || "Careem",
    screenRtl()
  );
}
const KNOWN_BLOCKS = new Set([
  "hello",
  "location",
  "search",
  "pills",
  "categories",
  "offer",
  "section",
  "restaurants",
  "hero",
  "stats",
  "split",
  "list",
  "note",
  "map",
  "sheet",
  "captain",
  "trip",
  "rating",
  "tips",
  "totals",
  "cta",
  "tabs",
]);

const BLOCK_ALIASES = {
  captaincard: "captain",
  captainrow: "captain",
  drivercard: "captain",
  driver: "captain",
  progresslist: "list",
  progress: "list",
  timeline: "list",
  steps: "list",
  listrow: "list",
  livemap: "map",
  drivermap: "map",
  bottomsheet: "sheet",
  actionsheet: "sheet",
  button: "cta",
  primarybutton: "cta",
  secondarybutton: "cta",
  searchfield: "search",
  whereto: "search",
  offerbanner: "offer",
  promo: "offer",
  promobanner: "offer",
  banner: "offer",
  chiprow: "pills",
  locationbar: "location",
  locationchip: "location",
  deliverylocation: "location",
  categorychips: "categories",
  categorychiprow: "categories",
  filters: "categories",
  restaurantcard: "restaurants",
  restaurantlist: "restaurants",
  restaurant: "restaurants",
  restaurantsrow: "restaurants",
  bottomstickycta: "cta",
  stickycta: "cta",
  stickybutton: "cta",
};

function canonicalBlockType(value) {
  const raw = String(value || "note");
  const key = raw.toLowerCase().replace(/[^a-z]/g, "");
  if (BLOCK_ALIASES[key]) return BLOCK_ALIASES[key];
  if (KNOWN_BLOCKS.has(raw.toLowerCase())) return raw.toLowerCase();
  return raw;
}

function knownBlocks(list) {
  return (list || [])
    .filter((b) => b && typeof b === "object")
    .map((b) => ({ ...b, type: canonicalBlockType(b.type || b.name || b.component) }))
    .filter((b) => KNOWN_BLOCKS.has(b.type));
}

function fieldsFromBlocks(screen) {
  const blocks = knownBlocks(screen.blocks);
  const cap = blocks.find((b) => b.type === "captain") || {};
  const trip = blocks.find((b) => b.type === "trip") || {};
  const sheet = blocks.find((b) => b.type === "sheet") || {};
  const hello = blocks.find((b) => b.type === "hello") || {};
  const note = blocks.find((b) => b.type === "note") || {};
  const totals = blocks.find((b) => b.type === "totals") || {};
  return {
    ...screen,
    captain: screen.captain || cap.name || "Yousef",
    rating: screen.rating || cap.rating || "4.9",
    car: screen.car || cap.car || "White Toyota Camry",
    plate: screen.plate || cap.plate || "D-17234",
    pickup: screen.pickup || trip.pickup,
    dest: screen.dest || trip.dest,
    fare: screen.fare || trip.fare || screen.amount,
    method: screen.method || trip.method,
    eta: screen.eta || sheet.sub || "3 min",
    title: screen.title || hello.title || sheet.title,
    primary: screen.primary || sheet.primary,
    secondary: screen.secondary || sheet.secondary,
    helper: screen.helper || note.text || "",
    rows: screen.rows || totals.rows || totals.items,
    blocks,
  };
}

function foodFromScreen(s) {
  const blocks = knownBlocks(s.blocks);
  const loc = blocks.find((b) => b.type === "location") || {};
  const search = blocks.find((b) => b.type === "search") || {};
  const cats = blocks.find((b) => b.type === "categories" || b.type === "pills") || {};
  const offer = blocks.find((b) => b.type === "offer") || {};
  const note = blocks.find((b) => b.type === "note") || {};
  const restBlocks = blocks.filter((b) => b.type === "restaurants");
  const tabs = blocks.find((b) => b.type === "tabs") || {};
  let items = restBlocks.flatMap((b) => b.items || []);
  if (items.length < 2) items = s.restaurants || [];
  if (items.length < 2) {
    const fb = fallbackBlocks("Food home").find((b) => b.type === "restaurants");
    items = (fb && fb.items) || [];
  }
  const sections = restBlocks.length
    ? restBlocks.map((b, i) => ({ title: b.title || (i ? "Popular near you" : "For you"), items: b.items || items }))
    : [{ title: "For you", items }];
  return {
    ...s,
    location: s.location || loc.text || "Marina Walk, JBR",
    search: s.search || search.text || "Search restaurants or dishes",
    categories: s.categories || cats.items || ["Burgers", "Healthy", "Arabic"],
    offer: s.offer || offer.text || "30% off · First Food order",
    helper: s.helper || note.text || "",
    restaurants: items,
    sections,
    tabs: s.tabs || tabs.items || ["Food", "Search", "Orders", "You"],
  };
}

function hydrateScreen(raw) {
  if (!raw || typeof raw !== "object") return { kind: "generic", label: "Careem", blocks: fallbackBlocks("Home") };
  const kind = raw.kind || inferKindFromText(`${raw.label || ""} ${state.brief.goal || ""}`) || "generic";
  let blocks = knownBlocks(raw.blocks);
  const types = new Set(blocks.map((b) => b.type));
  const foodOk = kind === "food" && (types.has("restaurants") || (raw.restaurants && raw.restaurants.length));
  const thin = blocks.length < 3 || (kind === "food" && !foodOk);
  if (thin) {
    const converted = knownBlocks(blocksFromFields(raw));
    const fallback = fallbackBlocks(raw.label || (kind === "food" ? "Food home" : kind) || "Home");
    blocks = converted.length >= 3 && !(kind === "food" && !converted.some((b) => b.type === "restaurants")) ? converted : fallback;
  }
  return { ...raw, kind, blocks };
}

function renderOne(s) {
  if (!s) return "";
  const screen = hydrateScreen(s);
  const kind = screenKind(screen);
  const merged = fieldsFromBlocks(screen);
  if (kind === "food") return renderFoodHome(foodFromScreen(merged));
  if (kind === "arriving") return renderArriving(merged);
  if (kind === "accept") return renderAccept(merged);
  if (kind === "cancel") return renderCancel(merged);
  if (kind === "failed") return renderFailed(merged);
  if (kind === "completed") return renderCompleted(merged);
  if (kind === "checkout") return renderCheckout(merged);
  if (merged.blocks && merged.blocks.length) return renderFromBlocks(merged);
  return renderFromBlocks({ ...merged, blocks: fallbackBlocks(merged.label || "Home") });
}
function blocksFromFields(s) {
  const out = [];
  if (s.hello || s.title) out.push({ type: "hello", kicker: s.hello || "Careem", title: s.title || "Careem" });
  if (s.location) out.push({ type: "location", text: s.location });
  if (s.where || s.search) out.push({ type: "search", text: s.search || s.where });
  if (Array.isArray(s.categories) && s.categories.length) out.push({ type: "categories", items: s.categories });
  if (typeof s.offer === "string" && s.offer) out.push({ type: "offer", text: s.offer });
  if (Array.isArray(s.sections)) {
    s.sections.forEach((sec) => {
      if (sec && sec.items) out.push({ type: "restaurants", title: sec.title || "For you", items: sec.items });
    });
  } else if (Array.isArray(s.restaurants) && s.restaurants.length) {
    out.push({ type: "restaurants", title: "Recommended", items: s.restaurants });
  }
  if (s.earned) out.push({ type: "hero", label: s.month || "This month", value: s.earned, meta: s.delta || "", bars: s.weeks || [] });
  if (s.stats) out.push({ type: "stats", items: s.stats });
  if (s.captain) out.push({ type: "map" }, { type: "captain", name: s.captain, rating: s.rating || "4.9", car: s.car || "", plate: s.plate || "" });
  if (s.pickup || s.dest || s.fare) out.push({ type: "trip", pickup: s.pickup, dest: s.dest, fare: s.fare || s.amount, method: s.method });
  if (s.primary) out.push({ type: "sheet", title: s.title || "Confirm", sub: s.eta || "", fee: s.fee, primary: s.primary, secondary: s.secondary || "" });
  if (s.amount && s.method && !s.primary) {
    out.push({ type: "hello", kicker: "Payment", title: s.title || "Payment failed" });
    out.push({ type: "totals", rows: [{ label: "Trip amount", value: s.amount }, { label: "Card", value: s.method }] });
  }
  if (Array.isArray(s.tips) && s.tips.length) out.push({ type: "tips", items: s.tips });
  if (Array.isArray(s.tabs) && s.tabs.length) out.push({ type: "tabs", items: s.tabs });
  return out;
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

const DNA_TRAITS = [
  { id: "density", name: "Spacing", left: "Dense", right: "Spacious" },
  { id: "corners", name: "Corners", left: "Sharp", right: "Rounded" },
  { id: "hierarchy", name: "Hierarchy", left: "Minimal", right: "Expressive" },
  { id: "copy", name: "Copy", left: "Concise", right: "Conversational" },
  { id: "interaction", name: "Guidance", left: "Direct", right: "Guided" },
];

function slider(id, left, right, value) {
  return `<label class="slide"><span>${left}</span><input type="range" min="0" max="100" value="${value}" data-slide="${id}" style="--pct:${value}%" /><span>${right}</span></label>`;
}

const dnaAcc = { lean: true, traits: true, kept: false, locks: false };

function accItem(id, title, value, body) {
  const open = !!dnaAcc[id];
  return `<section class="dna-acc-item${open ? " open" : ""}" data-acc="${id}">
    <button type="button" class="dna-acc-btn" data-acc-toggle="${id}" aria-expanded="${open}">
      <span>${title}</span>
      ${value ? `<em>${esc(value)}</em>` : ""}
      <i class="dna-chev" aria-hidden="true"></i>
    </button>
    <div class="dna-acc-body">${body}</div>
  </section>`;
}

function dnaPanelHtml() {
  const pad = 10 + Math.round(state.dna.density / 8);
  const r = 8 + Math.round(state.dna.corners / 8);
  const lean = `${labelOf(state.dna.density, "Tight", "Open")} · ${labelOf(state.dna.corners, "sharp", "soft")}`;
  const traits = DNA_TRAITS.map((t) => {
    const v = Number(state.dna[t.id] || 0);
    return `<div class="dna-trait">
      <div class="dna-trait-top"><span>${t.name}</span><em>${esc(labelOf(v, t.left, t.right))}</em></div>
      ${slider(t.id, t.left, t.right, v)}
    </div>`;
  }).join("");
  const kept = `<p class="dna-hint">Drop a rule if Pulse learned the wrong thing.</p>
    <div class="dna-chips">${
      state.dna.observed.length
        ? state.dna.observed.map((n, i) => `<button type="button" class="dna-chip" data-obs-del="${i}">${esc(n)} <span aria-hidden="true">×</span></button>`).join("")
        : `<span class="dna-hint">Nothing extra yet.</span>`
    }</div>`;
  return `<div class="dna-acc">
    ${accItem(
      "lean",
      "Pulse will lean",
      lean,
      `<div class="dna-swatch"><div class="dna-card" style="border-radius:${r}px;padding:${pad}px 16px">
        <small>Pulse will lean</small>
        <b>${esc(lean)}</b>
        <span>${esc(labelOf(state.dna.copy, "Short copy", "Talky copy"))} · ${esc(labelOf(state.dna.interaction, "direct", "guided"))}</span>
      </div></div>`
    )}
    ${accItem("traits", "Traits", `${DNA_TRAITS.length} sliders`, traits)}
    ${accItem("kept", "You kept", state.dna.observed.length ? String(state.dna.observed.length) : "None", kept)}
    ${accItem(
      "locks",
      "Locked Careem DNA",
      "4 rules",
      `<div class="dna-locks"><span>8px grid</span><span>Bottom sheets</span><span>Max 2 CTAs</span><span>Fee before the tap</span></div>`
    )}
  </div>`;
}

function isNarrow() {
  return window.matchMedia("(max-width: 640px)").matches;
}

function isTabletNav() {
  return window.matchMedia("(max-width: 1100px)").matches;
}

function askPlaceholder() {
  if (state.screen) return isNarrow() ? "Change copy or layout…" : "Change the copy, spacing, or layout…";
  return isNarrow() ? "Design a Careem screen" : "Ask Pulse to design a Careem screen";
}

function isDnaOpen() {
  const drawer = document.getElementById("dnaDrawer");
  return !!(drawer && drawer.classList.contains("open"));
}

function isHistOpen() {
  return document.body.classList.contains("hist-open");
}

function setHistOpen(open) {
  document.body.classList.toggle("hist-open", open);
  const scrim = document.getElementById("histScrim");
  const btn = document.getElementById("navToggle");
  if (scrim) scrim.classList.toggle("open", open);
  if (btn) btn.setAttribute("aria-expanded", open ? "true" : "false");
}

function setDnaOpen(open) {
  if (open) setHistOpen(false);
  const drawer = document.getElementById("dnaDrawer");
  const scrim = document.getElementById("dnaScrim");
  const chip = document.getElementById("dnaChip");
  if (drawer) {
    drawer.classList.toggle("open", open);
    drawer.setAttribute("aria-hidden", open ? "false" : "true");
  }
  if (scrim) scrim.classList.toggle("open", open);
  document.body.classList.toggle("dna-open", open);
  if (chip) {
    chip.classList.toggle("on", open);
    chip.setAttribute("aria-expanded", open ? "true" : "false");
  }
}

const FLOW_MAP = {
  arriving: {
    steps: ["Accepted", "Arriving", "Pickup", "On trip"],
    here: "Arriving",
    problems: [
      { flag: "Rider cannot find the car.", fix: "Keep plate, color, and Call on this screen." },
      { flag: "Cancel is too easy to hit.", fix: "Cancel stays a text action, not a second primary." },
    ],
  },
  accept: {
    steps: ["Offer", "Accept", "Arriving"],
    here: "Accept",
    problems: [
      { flag: "Fare hidden until after Accept.", fix: "Show fare before the tap." },
      { flag: "Addresses look like pins only.", fix: "Use street names, not the word Pickup." },
    ],
  },
  cancel: {
    steps: ["On trip", "Cancel", "Fee confirm", "Done"],
    here: "Cancel",
    problems: [
      { flag: "Fee appears after they tap.", fix: "Fee stays on the sheet before Cancel and pay." },
      { flag: "No keep-ride path.", fix: "Keep this trip is the primary." },
    ],
  },
  failed: {
    steps: ["Pay", "Failed", "Retry"],
    here: "Failed",
    problems: [
      { flag: "Amount disappears on failure.", fix: "Trip amount and card stay visible." },
    ],
  },
  completed: {
    steps: ["On trip", "Complete", "Rate", "Receipt"],
    here: "Complete",
    problems: [
      { flag: "Fare hidden until after rating.", fix: "Show the final fare before stars." },
      { flag: "Too many actions after the trip.", fix: "Done plus receipt or home — not both as primaries." },
    ],
  },
  food: {
    steps: ["Food home", "Restaurant", "Cart", "Checkout", "Track"],
    here: "Food home",
    problems: [
      { flag: "Restaurant cards missing ETA or rating.", fix: "Every card shows ★ and delivery time." },
      { flag: "Delivery location buried.", fix: "Pin + address stays at the top." },
    ],
  },
  superapp: {
    steps: ["Home", "Service", "Search", "Book", "Track"],
    here: "Home",
    problems: [
      { flag: "Services look like leftover chips.", fix: "Use a 4-column service grid with Careem tiles." },
      { flag: "Where to is buried under promos.", fix: "Search stays at the top." },
    ],
  },
  checkout: {
    steps: ["Home", "Slot", "Checkout", "Pay", "Success"],
    here: "Checkout",
    problems: [
      { flag: "Delivery fee only at the last tap.", fix: "Lock the fee next to Pay." },
    ],
  },
  home: {
    steps: ["Home", "Search", "Match", "On trip", "Receipt"],
    here: "Home",
    problems: [
      { flag: "Where to is buried.", fix: "Search stays one tap from open." },
    ],
  },
  generic: {
    steps: ["This screen", "Next", "Done"],
    here: "This screen",
    problems: [
      { flag: "No failure path yet.", fix: "Generate missing failure states." },
    ],
  },
};

function currentKind() {
  return projectKind();
}

function isGroceryFlow(steps) {
  const line = (steps || []).join("→");
  return line.includes("Slot") && (line.includes("Checkout") || line.includes("Payment"));
}

function ensureFlow() {
  const kind = currentKind();
  const def = FLOW_MAP[kind] || FLOW_MAP.generic;
  const steps = state.flow.steps || [];
  const extras = ["Failed", "Retry", "No-show", "Cancel"].filter((x) => steps.includes(x) && !def.steps.includes(x));
  const stale = !steps.length || (isGroceryFlow(steps) && kind !== "checkout");
  const mismatch = def.here && !steps.includes(def.here) && kind !== "generic";
  if (stale || mismatch) {
    let keepHere = state.flow.here && [...def.steps, ...extras].includes(state.flow.here) ? state.flow.here : def.here;
    if (kind === "food" && /cart|basket|checkout/.test((state.brief.goal || "").toLowerCase())) keepHere = "Cart";
    state.flow = { steps: [...def.steps, ...extras], problems: def.problems.map((p) => ({ ...p })), here: keepHere };
  }
  if (!state.flow.here) state.flow.here = def.here;
}

const STEP_KIND = {
  Offer: "accept",
  Accept: "accept",
  Accepted: "accept",
  Arriving: "arriving",
  Pickup: "arriving",
  "On trip": "arriving",
  Trip: "arriving",
  Track: "arriving",
  Book: "accept",
  Service: "superapp",
  Cancel: "cancel",
  "No-show": "cancel",
  "Fee confirm": "cancel",
  Failed: "failed",
  Retry: "failed",
  Pay: "failed",
  Checkout: "checkout",
  Cart: "food",
  Slot: "checkout",
  Results: "food",
  Payment: "checkout",
  Success: "completed",
  Home: "home",
  Search: "home",
  Match: "home",
  Complete: "completed",
  Rate: "completed",
  Receipt: "completed",
  "Food home": "food",
  Restaurant: "food",
};

function fallbackBlocks(step) {
  const product = state.brief.product || "";
  const kind = STEP_KIND[step] || currentKind();
  if (step === "Food home" || (step === "Home" && product === "Food") || kind === "food" && step !== "Restaurant" && step !== "Cart") {
    return [
      { type: "location", text: "Marina Walk, JBR" },
      { type: "search", text: "Search restaurants or dishes" },
      { type: "categories", items: ["Pizza", "Burgers", "Sushi", "Desserts"] },
      { type: "offer", text: "30% off · First Food order · FOOD20" },
      {
        type: "restaurants",
        title: "Recommended",
        items: [
          { name: "Salt", rating: "4.8", eta: "25 min", from: "From AED 35", dish: "Truffle fries" },
          { name: "Al Mallah", rating: "4.7", eta: "30 min", from: "From AED 18", dish: "Falafel wrap" },
        ],
      },
      { type: "tabs", items: ["Food", "Search", "Orders", "You"] },
    ];
  }
  if (step === "Restaurant") {
    return [
      { type: "hello", kicker: "Salt · 4.8", title: "Menu" },
      { type: "categories", items: ["Popular", "Burgers", "Sides"] },
      { type: "list", title: "Popular", items: [{ t: "Smash burger", s: "AED 42" }, { t: "Truffle fries", s: "AED 18" }] },
      { type: "cta", text: "Add to cart" },
    ];
  }
  if (step === "Cart" || (step === "Checkout" && (product === "Food" || currentKind() === "food"))) {
    return [
      { type: "hello", kicker: "Burger & Beyond", title: "Cart" },
      { type: "list", title: "Items", items: [{ t: "Double Cheese Burger", s: "AED 32" }, { t: "Truffle fries", s: "AED 18" }] },
      { type: "note", text: "Tap to add allergy notes or preferences" },
      { type: "totals", rows: [{ label: "Delivery fee", value: "AED 9.00" }, { label: "Total", value: "AED 59.00" }] },
      { type: "cta", text: "Go to checkout" },
    ];
  }
  if (kind === "checkout") {
    return [
      { type: "hello", kicker: product || "Quik", title: "Checkout" },
      { type: "list", title: "Items", items: [{ t: "Milk 1L", s: "AED 8" }, { t: "Eggs 12", s: "AED 14" }] },
      { type: "totals", rows: [{ label: "Delivery fee", value: "AED 9.00" }, { label: "Total", value: "AED 64.50" }] },
      { type: "cta", text: "Pay now" },
    ];
  }
  if (kind === "arriving") {
    return [
      { type: "map" },
      { type: "captain", name: "Yousef", rating: "4.9", car: "White Toyota Camry", plate: "D-17234" },
      { type: "trip", pickup: "Dubai Mall, Financial Centre Rd", dest: "Marina Walk, JBR", fare: "AED 45.00" },
      { type: "sheet", title: step === "Track" ? "Order on the way" : "Captain is arriving", sub: "3 min", primary: "Call", secondary: "Message" },
    ];
  }
  if (kind === "accept" || step === "Book") {
    return [
      { type: "map" },
      { type: "trip", pickup: "Dubai Mall, Financial Centre Rd", dest: "Marina Walk, JBR", fare: "AED 45.00" },
      { type: "sheet", title: "Book this ride?", sub: "Economy · 8 min", fee: "AED 45.00", feeNote: "Fare before you accept", primary: "Accept", secondary: "Decline" },
    ];
  }
  if (kind === "cancel") {
    return [
      { type: "map" },
      { type: "sheet", title: step === "No-show" ? "Captain didn’t arrive" : "Cancel this ride?", sub: "Fee applies if you cancel now", fee: "AED 8.00", feeNote: "Shown before you tap", primary: "Keep this trip", secondary: "Cancel and pay" },
    ];
  }
  if (kind === "failed") {
    return [
      { type: "hello", kicker: "Payment", title: "Payment failed" },
      { type: "totals", rows: [{ label: "Trip amount", value: "AED 25.00" }, { label: "Card", value: "Visa **** 1234" }] },
      { type: "cta", text: "Try Again" },
      { type: "cta", text: "Change Payment", style: "secondary" },
    ];
  }
  if (kind === "completed") {
    return [
      { type: "hello", kicker: "Trip complete", title: "AED 32.50" },
      { type: "trip", pickup: "Dubai Mall, Financial Centre Rd", dest: "Marina Walk, JBR", fare: "AED 32.50", method: "Careem Pay" },
      { type: "captain", name: "Yousef", rating: "4.9", car: "White Toyota Camry" },
      { type: "rating", value: 5 },
      { type: "tips", items: ["AED 5", "AED 10", "AED 15"] },
      { type: "cta", text: "Done" },
    ];
  }
  if (step === "Service") {
    return [
      { type: "hello", kicker: "Careem", title: "Choose a service" },
      { type: "pills", items: ["Rides", "Food", "Quik", "Pay", "Shops", "Plus", "Bike", "Box"] },
      { type: "list", title: "Recent destinations", items: [{ t: "Dubai Mall", s: "Downtown" }, { t: "Marina Walk", s: "JBR" }] },
      { type: "cta", text: "Continue" },
    ];
  }
  if (step === "Search") {
    return [
      { type: "search", text: "Where to?" },
      { type: "list", title: "Suggestions", items: [{ t: "Home", s: "Saved" }, { t: "Work", s: "Saved" }, { t: "Dubai Mall", s: "Downtown" }] },
      { type: "cta", text: "See results" },
    ];
  }
  return [
    { type: "hello", kicker: "Good evening", title: product || "Careem" },
    { type: "search", text: "Where to?" },
    { type: "pills", items: ["Rides", "Food", "Quik", "Pay", "Shops", "Plus", "Bike", "Box"] },
    { type: "offer", text: "Plus · 10% back on your next ride" },
    { type: "list", title: "Recent", items: [{ t: "Dubai Mall", s: "Downtown" }, { t: "Marina Walk", s: "JBR" }] },
    { type: "tabs", items: ["Home", "Activity", "Pay", "You"] },
  ];
}

function screenForStep(step) {
  const cached = state.flowScreens && state.flowScreens[step];
  if (cached && cached._for === step && Array.isArray(cached.blocks) && cached.blocks.length) {
    return { ...cached, label: step };
  }
  if (state.screen && state.screen._for === step && Array.isArray(state.screen.blocks) && state.screen.blocks.length) {
    return { ...state.screen, label: step };
  }
  return { kind: STEP_KIND[step] || currentKind(), label: step, blocks: fallbackBlocks(step) };
}

function openFlowStep(step) {
  ensureFlow();
  state.flow.here = step;
  state.screen = hydrateScreen(screenForStep(step));
  if (state.screen) state.screen._for = step;
  state.flowScreens = state.flowScreens || {};
  state.flowScreens[step] = state.screen;
  state.view = "flow";
  saveChat();
  render();
}

async function generateStepScreen(step) {
  if (state.thinking) return;
  const cached = state.flowScreens && state.flowScreens[step];
  if (cached && cached._gen && Array.isArray(cached.blocks) && cached.blocks.length >= 4) return;
  setBusy(true, `Designing ${step}…`);
  render();
  try {
    const res = await fetch("/api/studio", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ action: "step", brief: state.brief, step, dna: state.dna, history: state.messages.slice(-4) }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Step failed");
    const screen = hydrateScreen(data.screen);
    screen._gen = true;
    state.screen = screen;
    state.flowScreens[step] = screen;
    if (data.design_system) state.designSystem = data.design_system;
    if (data.reply) {
      state.reply = data.reply;
      state.messages.push({ role: "studio", text: data.reply });
    }
    saveChat();
  } catch {
    /* keep the fallback screen on canvas */
  }
  setBusy(false);
  render();
}

function generateMissingStates() {
  ensureFlow();
  const kind = currentKind();
  const extras = kind === "checkout" || kind === "failed" ? ["Failed", "Retry"] : ["Cancel", "No-show"];
  extras.forEach((step) => {
    if (!state.flow.steps.includes(step)) state.flow.steps.push(step);
    state.flowScreens[step] = screenForStep(step);
  });
  if (!state.flow.here) state.flow.here = extras[0];
  state.screen = hydrateScreen(screenForStep(state.flow.here));
  state.flow.problems = (state.flow.problems || []).filter((p) => !/fail|empty|arabic|missing|no-show/i.test(p.flag));
  state.messages.push({
    role: "studio",
    text: `Added ${extras.join(" → ")} to the journey. Tap a step to preview it.`,
  });
  state.reply = state.messages.slice(-1)[0].text;
  saveChat();
  proposeLearn("You asked for missing failure states before happy-path polish.");
}

const HOME_CHIPS = [
  { label: "Payment failed", product: "Pay", prompt: "Payment failed screen with trip amount, card visible, Try Again and Change Payment" },
  { label: "Driver arriving", product: "Rides", prompt: "Driver arriving screen with captain name, car, plate, ETA, Call and Message" },
  { label: "Food home", product: "Food", prompt: "Careem Food home with delivery location, search, categories, promo banner, restaurant cards with ratings ETA and pricing" },
  { label: "Accept ride", product: "Rides", prompt: "Accept ride sheet with map, fare, pickup and drop-off addresses, Decline and Accept" },
  { label: "Cancel ride", product: "Rides", prompt: "Ride cancellation with the fee visible on the sheet before they tap Cancel" },
  { label: "Ride completed", product: "Rides", prompt: "Ride completed screen with final fare, trip summary, payment, captain rating, optional tip" },
  { label: "Grocery checkout", product: "Quik", prompt: "Grocery checkout with cart items, delivery fee visible before Pay, and slot picker" },
  { label: "Super app home", product: "Super App", prompt: "Careem super app home with service grid for Rides Food Quik Pay Shops, promos, and Where to search" },
];

const CAREEM_PRODUCTS = [
  { label: "Super App", product: "Super App" },
  { label: "Rides", product: "Rides" },
  { label: "Food", product: "Food" },
  { label: "Quik", product: "Quik" },
  { label: "Shops", product: "Shops" },
  { label: "Pay", product: "Pay" },
  { label: "Plus", product: "Plus" },
  { label: "Bike", product: "Bike" },
  { label: "Rent", product: "Rent" },
  { label: "DineOut", product: "DineOut" },
  { label: "Box", product: "Box" },
  { label: "Captain", product: "Captain" },
];

const PROMPT_GROUPS = [
  {
    title: "Super App",
    product: "Super App",
    chips: [
      { label: "Home hub", prompt: "Careem super app home with service grid for Rides Food Quik Pay Shops, promos, and Where to search" },
      { label: "Service picker", prompt: "Choose a service bottom sheet with Rides Food Quik Shops Pay and recent destinations" },
      { label: "Activity feed", prompt: "Recent activity feed mixing rides food orders and pay transactions with status chips" },
    ],
  },
  {
    title: "Rides",
    product: "Rides",
    chips: [
      { label: "Book ride", prompt: "Book a ride home with Where to search, saved places, and ride type pills Economy Comfort Premium" },
      { label: "Accept ride", prompt: "Accept ride sheet with map, fare, pickup and drop-off addresses, Decline and Accept" },
      { label: "Driver arriving", prompt: "Driver arriving screen with captain name, car, plate, ETA, Call and Message" },
      { label: "On trip", prompt: "Ride in progress with map route, ETA, share trip, and emergency help" },
      { label: "Cancel ride", prompt: "Ride cancellation with the fee visible on the sheet before they tap Cancel" },
      { label: "Ride completed", prompt: "Ride completed screen with final fare, trip summary, payment, captain rating, optional tip, receipt or home" },
      { label: "Rider home", prompt: "Rider home with Where to search and monthly earnings dashboard with bar chart" },
    ],
  },
  {
    title: "Food",
    product: "Food",
    chips: [
      { label: "Food home", prompt: "Careem Food home with delivery location, search, categories, promo banner not charts, restaurant cards with ratings ETA and pricing" },
      { label: "Restaurant page", prompt: "Restaurant menu screen with hero dish, categories, popular items, and add-to-cart" },
      { label: "Cart & checkout", prompt: "Food cart checkout with items, delivery fee visible before Pay, promo code, and place order CTA" },
      { label: "Order tracking", prompt: "Food order tracking with map, ETA, captain, and order status steps" },
    ],
  },
  {
    title: "Quik",
    product: "Quik",
    chips: [
      { label: "Grocery home", prompt: "Quik grocery home with search, categories, reorder, and delivery slot hint" },
      { label: "Product detail", prompt: "Grocery product detail with image placeholder, price, quantity stepper, and add to cart" },
      { label: "Grocery checkout", prompt: "Grocery checkout with cart items, delivery fee visible before Pay, and slot picker" },
    ],
  },
  {
    title: "Shops",
    product: "Shops",
    chips: [
      { label: "Shops home", prompt: "Careem Shops home with store categories, featured brands, and delivery ETA badges" },
      { label: "Store page", prompt: "Shop store page with aisles, search, product grid, and cart FAB" },
      { label: "Order confirmed", prompt: "Shops order confirmed with order ID, ETA, and track order CTA" },
    ],
  },
  {
    title: "Pay",
    product: "Pay",
    chips: [
      { label: "Wallet home", prompt: "Careem Pay wallet home with balance, recent transactions, and send money CTA" },
      { label: "Payment failed", prompt: "Payment failed screen with trip amount, card visible, Try Again and Change Payment" },
      { label: "Send money", prompt: "Send money screen with recipient, amount, and fee before confirm" },
      { label: "Bill split", prompt: "Split bill screen with participants, amounts, and request payment actions" },
    ],
  },
  {
    title: "Plus & Captain",
    product: "Plus",
    chips: [
      { label: "Plus benefits", prompt: "Careem Plus subscription benefits screen with savings summary and manage plan" },
      { label: "Plus checkout", prompt: "Subscribe to Careem Plus with plan options, price breakdown, and confirm CTA" },
      { label: "Captain earnings", prompt: "Captain earnings home with weekly trips, net pay bar chart, and payout history" },
      { label: "Captain trip", prompt: "Captain active trip screen with navigation, rider info, and complete trip action" },
      { label: "Captain offline", prompt: "Captain go online sheet with earnings preview and start accepting rides CTA" },
    ],
  },
  {
    title: "Bike · Rent · DineOut · Box",
    product: "Bike",
    chips: [
      { label: "Bike unlock", prompt: "Careem Bike unlock screen with QR scan, nearby bikes map, and unlock CTA" },
      { label: "Car rental", prompt: "Car rental browse with vehicle cards, daily price, pickup location, and book CTA" },
      { label: "DineOut booking", prompt: "DineOut restaurant booking with date time party size and confirm reservation" },
      { label: "Box delivery", prompt: "Careem Box send parcel screen with pickup dropoff addresses, package size, and price estimate" },
    ],
  },
  {
    title: "UI patterns",
    product: "Careem",
    chips: [
      { label: "Empty state", prompt: "Empty state screen with illustration placeholder, headline, helper text, and one primary action" },
      { label: "Error state", prompt: "Error state with clear message, retry action, and support link" },
      { label: "Loading skeleton", prompt: "Loading skeleton screen with shimmer placeholders for list cards and hero" },
      { label: "Onboarding", prompt: "First-time onboarding with 3 value props and Get started CTA" },
      { label: "Search results", prompt: "Search results list with filters, sort, and result cards" },
      { label: "Filters sheet", prompt: "Filter bottom sheet with chips, price range, and apply reset actions" },
      { label: "Notifications", prompt: "Notifications inbox with grouped items and read/unread states" },
      { label: "Settings", prompt: "Account settings list with profile, language, payments, and support rows" },
      { label: "Profile", prompt: "User profile screen with avatar, name, saved places, payment methods, and logout" },
      { label: "Help & support", prompt: "Help center with FAQ categories, chat support CTA, and report issue" },
    ],
  },
];

const CHIPS = PROMPT_GROUPS.flatMap((g) => g.chips);

function deriveDesignSystem() {
  const blocks = (state.screen && state.screen.blocks) || [];
  const blockComponents = blocks.map((b) => ({
    name: COMPONENTS[b.type] || b.type,
    spec: `Generated \`${b.type}\` block`,
  }));
  const kind = inferKindFromText(state.brief.goal) || "screen";
  const defaults = {
    name: `${(state.brief.product || "Careem")} · ${kind || "screen"}`,
    product: state.brief.product || "Careem",
    layout: blocks.length ? `${blocks.length} blocks from your brief` : "Generate a screen to see components",
    tokens: {
      primary: "#00E784",
      forest: "#06281F",
      text: "#1F1F1F",
      muted: "#5F6368",
      radius: `${10 + Math.round(state.dna.corners / 10)}px`,
      grid: "8px",
    },
    typography: {
      title: "Google Sans 22/28 Medium",
      body: "Google Sans Text 14/20 Regular",
      meta: "Google Sans Text 12/16 Regular",
    },
    components: blockComponents,
    rules: [
      "8px grid",
      "Max 2 CTAs on action screens",
      "Fee / fare before the tap",
      "Bottom sheets over modals",
      "No bar charts on Food promos — use offer banners",
      ...(state.dna.observed || []).slice(0, 2),
    ],
  };
  const api = state.designSystem || {};
  return {
    ...defaults,
    ...api,
    tokens: { ...defaults.tokens, ...(api.tokens || {}) },
    typography: { ...defaults.typography, ...(api.typography || {}) },
    components: (api.components || []).length ? api.components : blockComponents,
    rules: (api.rules || []).length ? api.rules : defaults.rules,
  };
}

function designSystemPanel(full) {
  const ds = deriveDesignSystem();
  const globalRules = ["Google Sans", "Careem green #00E784", "Light surfaces", "44px touch targets"];
  const tokenRows = Object.entries(ds.tokens || {}).map(([k, v]) => {
    const color = /^#/.test(String(v)) ? v : null;
    return `<div class="ds-token${color ? " swatch" : ""}">${color ? `<i style="background:${color}"></i>` : ""}<div><b>${esc(k)}</b><span>${esc(v)}</span></div></div>`;
  });
  const typeRows = ds.typography
    ? Object.entries(ds.typography)
        .map(([k, v]) => `<div class="ds-type-row"><span>${esc(k)}</span><b>${esc(v)}</b></div>`)
        .join("")
    : "";
  const comps = (ds.components || []).length
    ? ds.components
        .map((c) => `<li class="ds-comp"><code>${esc(c.name)}</code><span>${esc(c.spec)}</span></li>`)
        .join("")
    : `<li class="ds-comp empty"><span>Generate a screen to populate components.</span></li>`;
  return `<section class="design-system ${full ? "full" : ""}">
    <div class="ds-card">
      <div class="ds-head"><div><p class="dna-kicker">Design system</p><b>${esc(ds.product)}</b></div><span class="ds-badge">Live</span></div>
      <p class="ds-layout">${esc(ds.layout || "")}</p>
    </div>
    <div class="ds-card">
      <p class="dna-kicker">Tokens</p>
      <div class="ds-token-grid">${tokenRows.join("")}</div>
      ${typeRows ? `<p class="dna-kicker">Type</p><div class="ds-type-grid">${typeRows}</div>` : ""}
    </div>
    <div class="ds-card">
      <p class="dna-kicker">Components on canvas</p>
      <ul class="ds-components">${comps}</ul>
    </div>
    <div class="ds-card">
      <p class="dna-kicker">Screen rules</p>
      <ul class="ds-rules">${(ds.rules || []).map((r) => `<li>${esc(r)}</li>`).join("")}</ul>
      <p class="dna-kicker">Careem global</p>
      <div class="dna-locks">${globalRules.map((r) => `<span>${esc(r)}</span>`).join("")}</div>
    </div>
  </section>`;
}

function inferBrief(goal) {
  const q = goal.toLowerCase();
  const explicit = state.brief.product;
  const fromText = (() => {
    if (/super app|service grid|services hub|home hub/.test(q)) return "Super App";
    if (/captain earnings|captain app|driver app|go online/.test(q)) return "Captain";
    if (/plus|subscription|cashback/.test(q) && !/food|ride/.test(q)) return "Plus";
    if (/food cart|food checkout|food search|careem food|food home/.test(q)) return "Food";
    if (/shop|mall|store page/.test(q) && !/food home|restaurant/.test(q)) return "Shops";
    if (/grocery|quik/.test(q) && !/food home|restaurant|what to eat|food cart/.test(q)) return "Quik";
    if (/\b(food home|restaurant menu|order tracking|what to eat|restaurant cards)\b/.test(q) || (/restaurant/.test(q) && !/booking|dineout/.test(q)))
      return "Food";
    if (/bike|scooter unlock/.test(q)) return "Bike";
    if (/rent|rental|lease a car/.test(q)) return "Rent";
    if (/dineout|dine out|table booking/.test(q)) return "DineOut";
    if (/box|parcel|courier|send package/.test(q)) return "Box";
    if (/pay|wallet|send money|payment failed|bill split/.test(q)) return "Pay";
    if (/ride|driver arriving|cancel ride|where to/.test(q)) return "Rides";
    return null;
  })();
  if (fromText) state.brief.product = fromText;
  else if (!explicit) state.brief.product = "Rides";
  state.brief.goal = goal;
  state.brief.flow = "";
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
  const starters = HOME_CHIPS.map(
    (s) =>
      `<button class="idea" type="button" data-chip="${esc(s.prompt)}" data-product="${esc(s.product)}">${esc(s.label)}</button>`
  ).join("");
  const more = state.showMorePrompts
    ? PROMPT_GROUPS.map(
        (g) => `<div class="prompt-group">
      <p class="hist-label">${esc(g.title)}</p>
      <div class="ideas">${g.chips.map((s) => `<button class="idea" type="button" data-chip="${esc(s.prompt)}" data-product="${esc(g.product)}">${esc(s.label)}</button>`).join("")}</div>
    </div>`
      ).join("")
    : "";
  return `<div class="gem-home">
    <h1 class="hello">Hello, Tooba</h1>
    <p class="sub">Describe a Careem screen — or pick a starter.</p>
    <div class="ideas home-chips">${starters}</div>
    <button class="idea subtle" type="button" data-toggle-more>${state.showMorePrompts ? "Fewer options" : "More Careem screens"}</button>
    ${more}
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
    <aside class="ds-col">${designSystemPanel(true)}</aside>
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
  ensureFlow();
  const f = state.flow;
  const steps = f.steps || [];
  const kind = currentKind();
  const title = {
    arriving: "This trip, beat by beat.",
    accept: "Offer to on the way.",
    cancel: "Cancel without a surprise.",
    failed: "Pay, fail, recover.",
    checkout: "Slot to paid.",
    completed: "Rate, tip, and receipt.",
    food: "Discover → order → track.",
    home: "Home to receipt.",
    superapp: "Open Careem. Pick a service.",
  }[kind] || "Flows, not just screens.";
  const preview = hydrateScreen(screenForStep(f.here || steps[0] || "Home"));
  return `<div class="gem-work flow-work">
    <div class="flow-page">
      <p class="dna-kicker">Journey · ${esc(state.brief.product || "Careem")}</p>
      <h1 class="flow-title">${esc(title)}</h1>
      <p class="sub">You are on <b>${esc(f.here || "this screen")}</b>. Tap a step to preview it.</p>
      <div class="flow-line">${steps
        .map(
          (s, i) =>
            `<button type="button" class="flow-step${s === f.here ? " on" : ""}" data-step="${esc(s)}">${esc(s)}</button>${
              i < steps.length - 1 ? "<i></i>" : ""
            }`
        )
        .join("")}</div>
      <h3>UX problems on this path</h3>
      ${(f.problems || [])
        .map((p) => `<article class="detail-card"><h3>${esc(p.flag)}</h3><p>${esc(p.fix)}</p></article>`)
        .join("")}
      <button class="go" id="missingBtn" type="button">Generate missing failure states</button>
    </div>
    <section class="preview-col">
      ${previewTools()}
      <div class="phone-fit" id="phone">${renderOne(preview)}</div>
    </section>
  </div>`;
}

function viewDna() {
  return `<div class="dna-page wide">
    <p class="dna-kicker">Style Memory</p>
    <h1 class="hello">Your DNA.</h1>
    <p class="sub">Sliders are yours. Careem rules stay locked. The next screen follows this mix.</p>
    ${dnaPanelHtml()}
    ${state.screen ? `<div class="ds-page-block">${designSystemPanel(true)}</div>` : ""}
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
    if (!on) input.placeholder = askPlaceholder();
  }
}

function paintDna() {
  const box = document.getElementById("dnaBody");
  if (!box) return;
  box.innerHTML = dnaPanelHtml();
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
  if (chip) {
    chip.textContent = isNarrow() ? "DNA" : `DNA · ${labelOf(state.dna.density, "dense", "spacious")}`;
    chip.classList.toggle("on", isDnaOpen());
    chip.setAttribute("aria-expanded", isDnaOpen() ? "true" : "false");
  }
  const tabFor = { directions: "navDirs", work: "navWork", flow: "navFlow", dna: "navDna" };
  document.querySelectorAll(".proj-tabs button").forEach((btn) => {
    btn.classList.toggle("on", btn.id === tabFor[state.view]);
  });
  const tabs = document.getElementById("projTabs");
  if (tabs) tabs.hidden = !(state.directions.length || state.screen);
  const bar = document.getElementById("learnBar");
  if (state.pendingLearn) {
    bar.hidden = false;
    document.getElementById("learnText").textContent = state.pendingLearn.text;
  } else if (bar) bar.hidden = true;
  const input = document.getElementById("askInput");
  if (input && !state.thinking) {
    input.placeholder = askPlaceholder();
  }
  paintHistory();
  const thread = app.querySelector(".gem-thread");
  if (thread) thread.scrollTop = thread.scrollHeight;
  requestAnimationFrame(fitPhone);
}

async function start(goal) {
  const text = (goal || document.getElementById("askInput").value || "").trim();
  if (!text || state.thinking) return;
  setHistOpen(false);
  state.brief.language = state.lang === "ar" ? "AR" : "EN";
  inferBrief(text);
  state.lang = "en";
  state.brief.language = "EN";
  document.getElementById("askInput").value = "";
  state.messages = [{ role: "user", text }];
  state.view = "chat";
  setBusy(true, "Pulse is generating from your brief…");
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
    state.designSystem = data.design_system || state.designSystem;
    const preview = data.previews && (data.previews.B || data.previews.C || data.previews.A);
    state.screen = hydrateScreen(preview || state.screen);
    if (state.screen && state.flow.here) {
      state.screen._for = state.flow.here;
      state.flowScreens = { ...(state.flowScreens || {}), [state.flow.here]: state.screen };
    }
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
  setBusy(true, "Pulse is generating that direction…");
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
    state.flow = data.flow || state.flow;
    state.screen = hydrateScreen(data.screen);
    if (state.screen) {
      state.screen.rtl = state.lang === "ar";
      state.screen._for = state.flow.here;
      state.flowScreens = { ...(state.flowScreens || {}), [state.flow.here]: state.screen };
    }
    state.tree = data.tree || [];
    state.issues = data.issues || [];
    state.designSystem = data.design_system || state.designSystem;
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
  if (e.target.id === "navToggle" || e.target.closest("#navToggle")) {
    const next = !isHistOpen();
    if (next) setDnaOpen(false);
    setHistOpen(next);
    return;
  }
  if (e.target.id === "histScrim") {
    setHistOpen(false);
    return;
  }
  if (e.target.id === "dnaChip" || e.target.closest("#dnaChip")) {
    setDnaOpen(!isDnaOpen());
    return;
  }
  if (e.target.id === "dnaClose" || e.target.id === "dnaScrim") {
    setDnaOpen(false);
    return;
  }
  const acc = e.target.closest("[data-acc-toggle]");
  if (acc) {
    const id = acc.dataset.accToggle;
    dnaAcc[id] = !dnaAcc[id];
    const item = acc.closest(".dna-acc-item");
    if (item) item.classList.toggle("open", dnaAcc[id]);
    acc.setAttribute("aria-expanded", dnaAcc[id] ? "true" : "false");
    return;
  }
  const dropObs = e.target.closest("[data-obs-del]");
  if (dropObs) {
    state.dna.observed = state.dna.observed.filter((_, i) => i !== Number(dropObs.dataset.obsDel));
    persist();
    render();
    return;
  }
  const nav = { navBrief: "brief", navDirs: "directions", navWork: "work", navFlow: "flow", navDna: "dna" };
  if (e.target.id && nav[e.target.id]) {
    if (e.target.id === "navDirs" && !state.directions.length) return;
    if (e.target.id === "navWork") {
      if (!state.screen || !state.screen.blocks || !state.screen.blocks.length) {
        ensureFlow();
        state.screen = hydrateScreen(screenForStep(state.flow.here || (state.flow.steps || [])[0] || "Home"));
      }
    }
    setDnaOpen(false);
    setHistOpen(false);
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
    if (chip.dataset.product) state.brief.product = chip.dataset.product;
    start(chip.dataset.chip);
    return;
  }
  const prodOnly = e.target.closest("button[data-product]:not([data-chip])");
  if (prodOnly) {
    state.brief.product = prodOnly.dataset.product;
    persist();
    const input = document.getElementById("askInput");
    if (input) {
      input.placeholder = `Describe a ${prodOnly.dataset.product} screen…`;
      input.focus();
    }
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
    if (state.screen) state.screen.rtl = state.lang === "ar";
    persist();
    render();
    return;
  }
  const toggleMore = e.target.closest("[data-toggle-more]");
  if (toggleMore) {
    state.showMorePrompts = !state.showMorePrompts;
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
  const stepBtn = e.target.closest("[data-step]");
  if (stepBtn) {
    openFlowStep(stepBtn.dataset.step);
    return;
  }
  if (e.target.id === "missingBtn") {
    generateMissingStates();
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
    const value = Number(e.target.value);
    state.dna[e.target.dataset.slide] = value;
    e.target.style.setProperty("--pct", `${value}%`);
    const card = e.target.closest(".dna-trait");
    const trait = DNA_TRAITS.find((t) => t.id === e.target.dataset.slide);
    if (card && trait) {
      const label = card.querySelector("em");
      if (label) label.textContent = labelOf(value, trait.left, trait.right);
    }
    applyDna();
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
    state.screen = hydrateScreen(data.screen || state.screen);
    if (state.screen) state.screen.rtl = state.lang === "ar";
    if (data.design_system) state.designSystem = data.design_system;
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

document.addEventListener("keydown", (e) => {
  if (e.key !== "Escape") return;
  if (isDnaOpen()) setDnaOpen(false);
  else if (isHistOpen()) setHistOpen(false);
});
function onViewport() {
  if (!isTabletNav()) setHistOpen(false);
  const chip = document.getElementById("dnaChip");
  if (chip && !state.thinking) {
    chip.textContent = isNarrow() ? "DNA" : `DNA · ${labelOf(state.dna.density, "dense", "spacious")}`;
  }
  const input = document.getElementById("askInput");
  if (input && !state.thinking) input.placeholder = askPlaceholder();
  fitPhone();
}
window.addEventListener("resize", onViewport);
if (window.visualViewport) window.visualViewport.addEventListener("resize", fitPhone);
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
