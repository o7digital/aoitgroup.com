(() => {
  "use strict";

  const API = "https://olivia-ai.o7digital.com";
  const CLIENT = "aoitgroup";
  const supported = ["en", "fr", "es", "de", "it"];
  const routeLanguage = location.pathname.split("/").filter(Boolean)[0];
  const language = supported.includes(routeLanguage)
    ? routeLanguage
    : supported.includes(document.documentElement.lang?.slice(0, 2))
      ? document.documentElement.lang.slice(0, 2)
      : "en";
  const copy = {
    en: { title: "Olivia AI", subtitle: "A&O IT Group assistant", welcome: "Hello. How can I help with your IT or cyber security requirements?", placeholder: "Write your message…", send: "Send", open: "Chat with Olivia AI", privacy: "By sending a message, you agree that A&O IT Group may process the information provided to answer your request.", accept: "Accept and continue", close: "Close", error: "The service is temporarily unavailable. Please try again." },
    fr: { title: "Olivia AI", subtitle: "Assistante A&O IT Group", welcome: "Bonjour. Comment puis-je vous aider avec vos besoins informatiques ou de cybersécurité ?", placeholder: "Écrivez votre message…", send: "Envoyer", open: "Parler avec Olivia AI", privacy: "En envoyant un message, vous acceptez qu’A&O IT Group traite les informations fournies afin de répondre à votre demande.", accept: "Accepter et continuer", close: "Fermer", error: "Le service est temporairement indisponible. Veuillez réessayer." },
    es: { title: "Olivia AI", subtitle: "Asistente de A&O IT Group", welcome: "Hola. ¿Cómo puedo ayudarle con sus necesidades de TI o ciberseguridad?", placeholder: "Escriba su mensaje…", send: "Enviar", open: "Hablar con Olivia AI", privacy: "Al enviar un mensaje, acepta que A&O IT Group procese la información proporcionada para responder a su solicitud.", accept: "Aceptar y continuar", close: "Cerrar", error: "El servicio no está disponible temporalmente. Inténtelo de nuevo." },
    de: { title: "Olivia AI", subtitle: "A&O IT Group Assistentin", welcome: "Hallo. Wie kann ich Ihnen bei Ihren IT- oder Cybersicherheitsanforderungen helfen?", placeholder: "Nachricht schreiben…", send: "Senden", open: "Mit Olivia AI chatten", privacy: "Mit dem Senden einer Nachricht stimmen Sie zu, dass A&O IT Group Ihre Angaben zur Beantwortung Ihrer Anfrage verarbeitet.", accept: "Akzeptieren und fortfahren", close: "Schließen", error: "Der Dienst ist vorübergehend nicht verfügbar. Bitte versuchen Sie es erneut." },
    it: { title: "Olivia AI", subtitle: "Assistente A&O IT Group", welcome: "Buongiorno. Come posso aiutarla con le sue esigenze IT o di sicurezza informatica?", placeholder: "Scrivi il tuo messaggio…", send: "Invia", open: "Chatta con Olivia AI", privacy: "Inviando un messaggio, accetta che A&O IT Group tratti le informazioni fornite per rispondere alla richiesta.", accept: "Accetta e continua", close: "Chiudi", error: "Il servizio è temporaneamente non disponibile. Riprovi." },
  }[language];

  const storageKey = `olivia:${CLIENT}`;
  const visitorId = localStorage.getItem(`${storageKey}:visitor`) || crypto.randomUUID();
  localStorage.setItem(`${storageKey}:visitor`, visitorId);
  let accepted = localStorage.getItem(`${storageKey}:privacy`) === "accepted";
  let busy = false;

  const style = document.createElement("style");
  style.textContent = `
    #olivia-launcher{position:fixed;right:22px;bottom:22px;z-index:2147483000;width:62px;height:62px;border:0;border-radius:50%;background:#00a4ed;color:#fff;box-shadow:0 10px 30px #0004;cursor:pointer;font:700 24px Arial}#olivia-launcher:hover{transform:translateY(-2px)}
    #olivia-panel{position:fixed;right:22px;bottom:98px;z-index:2147483000;width:min(390px,calc(100vw - 24px));height:min(590px,calc(100vh - 125px));display:none;flex-direction:column;overflow:hidden;border-radius:14px;background:#fff;box-shadow:0 20px 55px #0005;font:14px/1.45 Arial,sans-serif;color:#171d30}#olivia-panel[data-open=true]{display:flex}
    .olivia-head{display:flex;align-items:center;gap:12px;padding:16px 18px;background:#171d30;color:#fff}.olivia-avatar{display:grid;place-items:center;width:40px;height:40px;border-radius:50%;background:#00a4ed;font-weight:700}.olivia-head strong,.olivia-head small{display:block}.olivia-head small{color:#c9cede}.olivia-close{margin-left:auto;border:0;background:transparent;color:#fff;font-size:25px;cursor:pointer}
    .olivia-messages{flex:1;overflow:auto;padding:16px;background:#f5f7fa}.olivia-message{max-width:82%;margin:0 0 12px;padding:10px 13px;border-radius:12px;background:#fff;box-shadow:0 1px 3px #0001;white-space:pre-wrap}.olivia-message.user{margin-left:auto;background:#00a4ed;color:#fff}.olivia-message.error{color:#a52a2a}
    .olivia-consent{padding:13px 16px;border-top:1px solid #e4e8ee;background:#fff;font-size:12px;color:#566074}.olivia-consent button{display:block;margin-top:9px;padding:9px 12px;border:0;border-radius:6px;background:#171d30;color:#fff;cursor:pointer}
    .olivia-form{display:flex;gap:8px;padding:12px;border-top:1px solid #e4e8ee;background:#fff}.olivia-form textarea{flex:1;resize:none;min-height:42px;max-height:100px;padding:10px;border:1px solid #ccd3dc;border-radius:8px;font:inherit}.olivia-form button{border:0;border-radius:8px;padding:0 15px;background:#00a4ed;color:#fff;font-weight:700;cursor:pointer}.olivia-form button:disabled{opacity:.55;cursor:wait}
    @media(max-width:520px){#olivia-launcher{right:12px;bottom:12px}#olivia-panel{right:12px;bottom:84px;height:calc(100vh - 100px)}}`;
  document.head.appendChild(style);

  document.body.insertAdjacentHTML("beforeend", `<button id="olivia-launcher" type="button" aria-label="${copy.open}" title="${copy.open}">O</button><section id="olivia-panel" role="dialog" aria-label="${copy.open}"><header class="olivia-head"><span class="olivia-avatar">O</span><span><strong>${copy.title}</strong><small>${copy.subtitle}</small></span><button class="olivia-close" type="button" aria-label="${copy.close}">×</button></header><div class="olivia-messages" aria-live="polite"><div class="olivia-message">${copy.welcome}</div></div><div class="olivia-consent" ${accepted ? "hidden" : ""}>${copy.privacy}<button type="button">${copy.accept}</button></div><form class="olivia-form"><textarea rows="1" required maxlength="2000" placeholder="${copy.placeholder}" ${accepted ? "" : "disabled"}></textarea><button type="submit" ${accepted ? "" : "disabled"}>${copy.send}</button></form></section>`);

  const panel = document.querySelector("#olivia-panel");
  const messages = panel.querySelector(".olivia-messages");
  const form = panel.querySelector("form");
  const input = form.querySelector("textarea");
  const submit = form.querySelector("button");
  const add = (text, role = "ai") => { const node = document.createElement("div"); node.className = `olivia-message ${role}`; node.textContent = text; messages.appendChild(node); messages.scrollTop = messages.scrollHeight; };
  document.querySelector("#olivia-launcher").addEventListener("click", () => panel.dataset.open = panel.dataset.open !== "true");
  panel.querySelector(".olivia-close").addEventListener("click", () => panel.dataset.open = "false");
  panel.querySelector(".olivia-consent button").addEventListener("click", () => { accepted = true; localStorage.setItem(`${storageKey}:privacy`, "accepted"); panel.querySelector(".olivia-consent").hidden = true; input.disabled = submit.disabled = false; input.focus(); });

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const message = input.value.trim();
    if (!message || busy || !accepted) return;
    busy = true; submit.disabled = true; input.value = ""; add(message, "user");
    const metadata = { page: location.href, pageTitle: document.title, language, referrer: document.referrer };
    try {
      await fetch(`${API}/api/widget/conversations`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ clientCode: CLIENT, visitorId, content: message, source: "website", language, metadata }) });
      const response = await fetch(`${API}/api/olivia/chat`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ clientCode: CLIENT, message, language, metadata }) });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const result = await response.json();
      const reply = result.reply || copy.error;
      add(reply);
      await fetch(`${API}/api/widget/conversations`, { method: "PATCH", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ clientCode: CLIENT, visitorId, content: reply, model: result.model || "olivia" }) });
    } catch (error) { console.error("Olivia AI", error); add(copy.error, "error"); }
    finally { busy = false; submit.disabled = false; input.focus(); }
  });
})();
