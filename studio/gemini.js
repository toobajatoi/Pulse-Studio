async function generate(prompt, hint = "Return compact JSON only. No markdown.") {
  const response = await fetch("/api/generate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ prompt, hint }),
  });
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || "Gemini failed");
  return data.text;
}

function parseJson(text) {
  const match = String(text).match(/\{[\s\S]*\}/);
  return JSON.parse(match[0]);
}
