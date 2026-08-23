(function () {
  const pages = [
    { id: "feedback", label: "Feedback Pulse", title: "What are riders actually stuck on?", lede: "Paste-level research, clustered into themes. Pick a theme and Pulse writes copy or layouts against the evidence — not a generic prompt." },
    { id: "copy", label: "Copy Studio", title: "Write it like Careem.", lede: "Short. Certain. Human. Headline, helper, CTA, empty and error — in English, Arabic, or both." },
    { id: "layouts", label: "Layout Lab", title: "Three directions, not one mock.", lede: "Each layout is a hypothesis you can test. No fake nearby cars. No hidden fees." },
    { id: "prompt", label: "Design prompt", title: "The brief you can paste into any LLM.", lede: "Forces citation, bilingual copy, and testable layouts — so the model behaves like a designer." },
  ];

  const state = {
    page: "feedback",
    city: "All cities",
    source: "All sources",
    theme: null,
    tone: "Careem default",
    language: "English",
  };

  const notes = window.PULSE_DATA.notes;
  const nav = document.getElementById("nav");
  const citySel = document.getElementById("city");
  const sourceSel = document.getElementById("source");
  const view = document.getElementById("view");

  function unique(key) {
    return [...new Set(notes.map((n) => n[key]))].sort();
  }

  function fillSelect(el, items) {
    el.innerHTML = items.map((v) => `<option>${v}</option>`).join("");
  }

  fillSelect(citySel, ["All cities", ...unique("city")]);
  fillSelect(sourceSel, ["All sources", ...unique("source")]);

  nav.innerHTML = pages
    .map((p) => `<button class="nav-btn" data-page="${p.id}" type="button">${p.label}</button>`)
    .join("");

  function filteredNotes() {
    return notes.filter((n) => {
      const cityOk = state.city === "All cities" || n.city === state.city;
      const sourceOk = state.source === "All sources" || n.source === state.source;
      return cityOk && sourceOk;
    });
  }

  function insights() {
    const list = window.PulseEngine.analyze(filteredNotes());
    if (!state.theme || !list.some((i) => i.key === state.theme)) {
      state.theme = list[0] ? list[0].key : null;
    }
    return list;
  }

  function selected(list) {
    return list.find((i) => i.key === state.theme) || list[0];
  }

  function escapeHtml(value) {
    return String(value)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;");
  }

  function renderNav() {
    nav.querySelectorAll(".nav-btn").forEach((btn) => {
      btn.classList.toggle("active", btn.dataset.page === state.page);
    });
  }

  function renderHead() {
    const page = pages.find((p) => p.id === state.page);
    document.getElementById("title").textContent = page.title;
    document.getElementById("lede").textContent = page.lede;
  }

  function themeOptions(list) {
    return list
      .map((i) => `<option value="${i.key}" ${i.key === state.theme ? "selected" : ""}>${escapeHtml(i.label)} · ${i.count} notes</option>`)
      .join("");
  }

  function renderFeedback(list) {
    const rows = filteredNotes();
    const failed = rows.filter((r) => r.success === "fail").length;
    const cities = new Set(rows.map((r) => r.city)).size;
    const cards = list
      .slice(0, 6)
      .map((insight) => {
        const quotes = insight.quotes
          .slice(0, 2)
          .map((q) => `<div class="quote">“${escapeHtml(q.quote)}”<br><span class="tag">${escapeHtml(q.city)} · ${escapeHtml(q.screen)}</span></div>`)
          .join("");
        return `<article class="card">
          <div><span class="tag ${insight.topSeverity}">${insight.topSeverity.toUpperCase()}</span><span class="tag">${insight.count} notes</span></div>
          <h3>${escapeHtml(insight.label)}</h3>
          <p>${escapeHtml(insight.need)}</p>
          ${quotes}
          <p>${escapeHtml(insight.opportunity)}</p>
          <button class="use-btn" data-use="${insight.key}" type="button">Use this theme →</button>
        </article>`;
      })
      .join("");
    view.innerHTML = `
      <div class="metrics">
        <div class="metric"><b>${rows.length}</b><span>Notes in view</span></div>
        <div class="metric"><b>${list.length}</b><span>Themes</span></div>
        <div class="metric"><b>${failed}</b><span>Failed tasks</span></div>
        <div class="metric"><b>${cities}</b><span>Markets</span></div>
      </div>
      <div class="grid">${cards}</div>`;
  }

  function renderCopy(list) {
    const insight = selected(list);
    const deck = window.PulseEngine.generateCopy(insight, state.tone, state.language);
    const evidence = insight.quotes
      .slice(0, 3)
      .map((q) => `<li><em>${escapeHtml(q.city)}</em> · ${escapeHtml(q.screen)} — “${escapeHtml(q.quote)}”</li>`)
      .join("");
    const variants = deck.variants
      .map((v, i) => {
        const rtl = /[^\u0000-\u00ff]/.test(v.headline) ? "ar" : "";
        return `<div class="copybox ${rtl}">
          <h4>Variant ${i + 1} · ${escapeHtml(v.headline)}</h4>
          <p><b>Helper.</b> ${escapeHtml(v.helper)}</p>
          <p><b>CTA.</b> ${escapeHtml(v.cta)}</p>
          <p><b>Empty.</b> ${escapeHtml(v.empty)}</p>
          <p><b>Error.</b> ${escapeHtml(v.error)}</p>
          <p><b>Chip.</b> ${escapeHtml(v.chip)}</p>
        </div>`;
      })
      .join("");
    view.innerHTML = `
      <div class="split">
        <div>
          <label>Theme to write for<br>
            <select id="themeSelect">${themeOptions(list)}</select>
          </label>
          <p style="margin:16px 0 8px;font-size:13px;color:#6b6b6b">Tone slider</p>
          <div id="tone">${["Careem default", "More punchy", "More reassuring"].map((t) => `<button class="ghost ${t === state.tone ? "solid" : ""}" data-tone="${t}" type="button">${t}</button>`).join(" ")}</div>
          <p style="margin:16px 0 8px;font-size:13px;color:#6b6b6b">Language</p>
          <div id="lang">${["English", "Arabic", "Both"].map((t) => `<button class="ghost ${t === state.language ? "solid" : ""}" data-lang="${t}" type="button">${t}</button>`).join(" ")}</div>
          <p style="margin:20px 0 8px;font-weight:600">Evidence this copy has to answer</p>
          <ul class="evidence">${evidence}</ul>
        </div>
        <div>
          <p style="color:#6b6b6b;font-size:13px;margin-top:0">Screen · ${escapeHtml(deck.screen)}</p>
          ${variants}
          <p>${escapeHtml(deck.rationale)}</p>
        </div>
      </div>`;
  }

  function renderLayouts(list) {
    const insight = selected(list);
    const layouts = window.PulseEngine.generateLayouts(insight);
    const cards = layouts
      .map((layout) => {
        const rows = layout.structure
          .map((step, i) => `<div class="row ${i === layout.structure.length - 1 ? "primary" : ""}">${escapeHtml(step)}</div>`)
          .join("");
        return `<article class="card">
          <span class="tag">HYPOTHESIS</span>
          <h3>${escapeHtml(layout.name)}</h3>
          <p>${escapeHtml(layout.hypothesis)}</p>
          <div class="wire">${rows}</div>
          <p><b>Test.</b> ${escapeHtml(layout.test)}</p>
          <p><b>Tradeoff.</b> ${escapeHtml(layout.tradeoff)}</p>
          <p>${escapeHtml(layout.grounding)}</p>
        </article>`;
      })
      .join("");
    view.innerHTML = `
      <div style="padding:8px 32px 0">
        <label>Theme to layout<br>
          <select id="themeSelect">${themeOptions(list)}</select>
        </label>
      </div>
      <div class="grid">${cards}</div>`;
  }

  function renderPrompt(list) {
    const insight = selected(list);
    const brief = window.PulseEngine.buildBrief(insight, state.tone);
    view.innerHTML = `
      <div style="padding:8px 32px 28px">
        <label>Tone to lock in the prompt<br>
          <select id="toneSelect">
            ${["Careem default", "More punchy", "More reassuring"].map((t) => `<option ${t === state.tone ? "selected" : ""}>${t}</option>`).join("")}
          </select>
        </label>
        <p style="margin:16px 0 8px;font-weight:600">Ready-to-paste prompt</p>
        <textarea class="prompt" id="brief">${escapeHtml(brief)}</textarea>
        <p style="margin-top:18px;font-weight:600">Why this prompt is strict</p>
        <ul>
          <li><b>Grounding.</b> Every diagnosis line must cite a quote.</li>
          <li><b>Brand.</b> Careem’s public TOV is a constraint, not a vibe.</li>
          <li><b>Markets.</b> Dubai is not Cairo.</li>
          <li><b>Safety.</b> Hidden fees and fake cars are banned.</li>
          <li><b>Arabic.</b> RTL placement is required, not only translation.</li>
        </ul>
      </div>`;
  }

  function render() {
    const list = insights();
    renderNav();
    renderHead();
    if (state.page === "feedback") renderFeedback(list);
    if (state.page === "copy") renderCopy(list);
    if (state.page === "layouts") renderLayouts(list);
    if (state.page === "prompt") renderPrompt(list);
  }

  nav.addEventListener("click", (e) => {
    const btn = e.target.closest("[data-page]");
    if (!btn) return;
    state.page = btn.dataset.page;
    render();
  });

  citySel.addEventListener("change", () => {
    state.city = citySel.value;
    render();
  });
  sourceSel.addEventListener("change", () => {
    state.source = sourceSel.value;
    render();
  });

  view.addEventListener("click", (e) => {
    const use = e.target.closest("[data-use]");
    if (use) {
      state.theme = use.dataset.use;
      state.page = "copy";
      render();
      return;
    }
    const tone = e.target.closest("[data-tone]");
    if (tone) {
      state.tone = tone.dataset.tone;
      render();
      return;
    }
    const lang = e.target.closest("[data-lang]");
    if (lang) {
      state.language = lang.dataset.lang;
      render();
    }
  });

  view.addEventListener("change", (e) => {
    if (e.target.id === "themeSelect") {
      state.theme = e.target.value;
      render();
    }
    if (e.target.id === "toneSelect") {
      state.tone = e.target.value;
      render();
    }
  });

  document.getElementById("studioBtn").addEventListener("click", () => {
    document.getElementById("studio").scrollIntoView({ behavior: "smooth" });
  });
  document.getElementById("notesBtn").addEventListener("click", () => {
    state.page = "feedback";
    render();
    document.getElementById("studio").scrollIntoView({ behavior: "smooth" });
  });

  document.getElementById("askForm").addEventListener("submit", (e) => {
    e.preventDefault();
    const q = document.getElementById("ask").value.toLowerCase();
    const list = insights();
    const hit = list.find((i) => i.label.toLowerCase().includes(q) || i.need.toLowerCase().includes(q));
    if (hit) state.theme = hit.key;
    state.page = q.includes("layout") ? "layouts" : q.includes("prompt") ? "prompt" : "copy";
    document.getElementById("ask").value = "";
    render();
  });

  render();
})();
