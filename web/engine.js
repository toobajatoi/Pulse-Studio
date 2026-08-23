(function (global) {
  const data = global.PULSE_DATA;

  function blob(row) {
    return `${row.quote || ""} ${row.screen || ""} ${row.task || ""}`.toLowerCase();
  }

  function hasKeyword(text, keyword) {
    const escaped = keyword.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    return new RegExp(`\\b${escaped}\\b`, "i").test(text);
  }

  function classifyRow(row) {
    const text = blob(row);
    const hits = Object.entries(data.themes)
      .filter(([, meta]) => meta.keywords.some((k) => hasKeyword(text, k)))
      .map(([key]) => key);
    return hits.length ? hits : ["home_ia"];
  }

  function mostCommon(values) {
    const counts = {};
    values.forEach((v) => {
      counts[v] = (counts[v] || 0) + 1;
    });
    return Object.entries(counts)
      .sort((a, b) => b[1] - a[1])
      .map(([k]) => k);
  }

  function analyze(rows) {
    const buckets = {};
    rows.forEach((row) => {
      classifyRow(row).forEach((key) => {
        buckets[key] = buckets[key] || [];
        buckets[key].push(row);
      });
    });

    return Object.entries(buckets)
      .map(([key, items]) => {
        const meta = data.themes[key];
        const score =
          items.reduce((sum, row) => sum + (data.severityWeight[String(row.severity).toLowerCase()] || 1), 0) /
          Math.max(items.length, 1);
        const top = items.slice().sort((a, b) => {
          return (data.severityWeight[String(b.severity).toLowerCase()] || 1) - (data.severityWeight[String(a.severity).toLowerCase()] || 1);
        });
        const cities = mostCommon(items.map((r) => r.city));
        const screens = mostCommon(items.map((r) => r.screen));
        const failN = items.filter((r) => String(r.success).toLowerCase() === "fail").length;
        return {
          key,
          label: meta.label,
          need: meta.need,
          count: items.length,
          severityScore: Math.round(score * 100) / 100,
          topSeverity: String(top[0].severity),
          cities,
          screens,
          quotes: top.slice(0, 4),
          opportunity: `If we fix ${meta.label.toLowerCase()} on ${screens[0]}, ${failN} of ${items.length} notes in this set should stop failing — starting in ${cities[0]}.`,
        };
      })
      .sort((a, b) => b.severityScore - a.severityScore || b.count - a.count);
  }

  function cityHook(cities) {
    if (cities.includes("Jeddah")) return "Jeddah";
    if (cities.includes("Karachi")) return "Karachi";
    if (cities.includes("Dubai")) return "Dubai";
    return cities[0] || "your city";
  }

  function generateCopy(insight, tone, language) {
    const toneKey = { "Careem default": "calm", "More punchy": "punchy", "More reassuring": "reassuring" }[tone] || "calm";
    const bank = data.copyBank[insight.key] || data.copyBank.home_ia;
    let variants = (bank[toneKey] || bank.calm || []).map((v) => ({ ...v }));
    const city = cityHook(insight.cities);
    variants.forEach((variant) => {
      if (city && variant.helper.toLowerCase().includes("heading home")) {
        variant.helper = `Heading home, ${city}? Your last trip is one tap.`;
      }
      if (variant.cta.includes("{price}")) {
        variant.cta = variant.cta.replace("{price}", city === "Dubai" ? "42 AED" : "28 SAR");
      }
    });
    if ((language === "Arabic" || language === "Both") && data.arOverlay[insight.key]) {
      const ar = { ...data.arOverlay[insight.key] };
      variants = language === "Arabic" ? [ar] : variants.concat([ar]);
    }
    const quotes = insight.quotes.slice(0, 2).map((q) => `“${q.quote}”`).join("; ");
    return {
      screen: insight.screens[0] || "Ride",
      tone,
      language,
      variants,
      rationale: `Grounded in ${insight.count} notes on ${insight.label.toLowerCase()} (${insight.cities.slice(0, 3).join(", ")}). ${insight.need}. Evidence: ${quotes} Tone follows Careem public TOV: short, certain, human — never a lecture.`,
      constraints: data.constraints,
    };
  }

  function generateLayouts(insight) {
    const layouts = data.layouts[insight.key] || data.defaultLayouts;
    const city = insight.cities.slice(0, 3).join(", ");
    return layouts.map((item) => ({
      ...item,
      grounding: `Based on ${insight.count} notes (${insight.topSeverity} peak) in ${city}. ${insight.opportunity}`,
    }));
  }

  function buildBrief(insight, tone) {
    const quotes = insight.quotes
      .map((q) => `- (${q.city}, ${q.screen}, ${q.severity}) ${q.quote}`)
      .join("\n");
    return `You are a product designer and UX writer embedded in Careem Ride.
Follow Careem's public tone of voice: less is more; upbeat and everyday; always dependable; driven but never cocky; no slang; no jargon (never say "user" or "purchase"); contractions are good; headlines under 10 words.

Job
Review the design notes below and return quick, usable improvements — not a critique essay.

Theme: ${insight.label}
Job-to-be-done: ${insight.need}
Tone slider: ${tone}
Markets in the notes: ${insight.cities.join(", ")}
Screens: ${insight.screens.join(", ")}

Evidence
${quotes}

Return exactly this structure:
1. Diagnosis (3 bullets, each citing a quote)
2. Usability fixes (5 bullets). Each bullet: problem → change → why it helps a first-time rider in one of the named cities
3. UI copy deck in English AND Arabic: headline, helper, CTA, empty, error
4. 3 layout directions: name, 4-part structure, what to test, one tradeoff
5. What not to do (2 bullets) — brand or trust risks

Constraints
- Do not invent metrics or research Careem did not provide
- Do not recommend dark patterns (hidden fees, fake nearby cars, forced wait)
- Prefer one primary action per screen
- Arabic must include RTL placement notes, not only translation
- Keep the whole answer under 350 words`;
  }

  global.PulseEngine = { analyze, generateCopy, generateLayouts, buildBrief };
})(window);
