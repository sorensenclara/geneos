/* GENEOS · interacciones del sitio (sin dependencias) */
(() => {
  const $ = (s, el = document) => el.querySelector(s);
  const $$ = (s, el = document) => [...el.querySelectorAll(s)];

  /* Menú móvil */
  const toggle = $(".nav-toggle");
  const nav = $("#menu");
  if (toggle && nav) {
    toggle.addEventListener("click", () => {
      nav.style.top = `${document.querySelector(".site-header").getBoundingClientRect().bottom}px`;
      const open = nav.classList.toggle("open");
      toggle.setAttribute("aria-expanded", open);
      document.body.classList.toggle("nav-open", open);
    });
  }
  $$(".sub-toggle").forEach((btn) => {
    btn.addEventListener("click", () => {
      const li = btn.closest("li");
      const open = li.classList.toggle("open");
      btn.setAttribute("aria-expanded", open);
    });
  });
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && nav?.classList.contains("open")) toggle.click();
  });

  /* Carruseles de fotos */
  $$(".carousel").forEach((c) => {
    const track = $(".carousel-track", c);
    const step = () => track.clientWidth;
    const go = (dir) => {
      const max = track.scrollWidth - track.clientWidth - 2;
      if (dir > 0 && track.scrollLeft >= max) track.scrollTo({ left: 0 });
      else if (dir < 0 && track.scrollLeft <= 0) track.scrollTo({ left: max });
      else track.scrollBy({ left: dir * step() });
    };
    $(".prev", c)?.addEventListener("click", () => go(-1));
    $(".next", c)?.addEventListener("click", () => go(1));
    const ms = +c.dataset.autoplay;
    if (ms && !matchMedia("(prefers-reduced-motion: reduce)").matches) {
      let t = setInterval(() => go(1), ms);
      c.addEventListener("mouseenter", () => clearInterval(t));
      c.addEventListener("mouseleave", () => (t = setInterval(() => go(1), ms)));
    }
  });

  /* Marquesinas: duplicamos los logos para un loop continuo */
  $$(".marquee-track").forEach((track) => {
    const items = [...track.children];
    items.forEach((li) => {
      const clone = li.cloneNode(true);
      clone.setAttribute("aria-hidden", "true");
      clone.querySelectorAll("a").forEach((a) => (a.tabIndex = -1));
      track.appendChild(clone);
    });
    track.style.setProperty("--marquee-duration", `${items.length * 3.5}s`);
  });

  /* Flip boxes en pantallas táctiles */
  $$(".flip").forEach((f) => f.addEventListener("click", () => f.classList.toggle("flipped")));

  /* Fichas del equipo */
  $$("[data-member]").forEach((btn) => {
    const dlg = document.getElementById(btn.dataset.member);
    if (!dlg) return;
    btn.addEventListener("click", () => dlg.showModal());
    dlg.addEventListener("click", (e) => { if (e.target === dlg || e.target.closest(".member-close")) dlg.close(); });
  });

  /* Video del hero: una sola reproducción; sin animación si el usuario la reduce */
  const heroVideo = $(".hx-hero-video");
  if (heroVideo) {
    if (matchMedia("(prefers-reduced-motion: reduce)").matches) { heroVideo.removeAttribute("autoplay"); heroVideo.pause(); }
    heroVideo.loop = false;
  }

  /* Mensaje tras enviar el formulario */
  if (new URLSearchParams(location.search).has("enviado")) {
    $$(".form-status").forEach((p) => {
      p.hidden = false;
      p.textContent = "¡Gracias! Recibimos tu mensaje y te responderemos a la brevedad.";
    });
  }
})();
