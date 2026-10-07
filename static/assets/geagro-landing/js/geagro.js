/* GEAGRO (portada importada de geagro.ar): demo por WhatsApp y FAQ */
(function () {
  const WHATSAPP = '5492494521418';
  document.querySelectorAll('[data-version]').forEach((a) => a.addEventListener('click', () => {
    const radio = document.getElementById('v-' + a.dataset.version);
    if (radio) radio.checked = true;
  }));
  const form = document.getElementById('demoForm');
  const status = document.getElementById('formStatus');
  if (form && status) {
    const say = (text, kind) => { status.textContent = text; status.className = 'ga-form-status' + (kind ? ' ga-' + kind : ''); };
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      const d = Object.fromEntries(new FormData(form).entries());
      if (!(d.nombre || '').trim()) { say('Completá tu nombre.', 'err'); form.nombre.focus(); return; }
      if (!/^\S+@\S+\.\S+$/.test(d.email || '')) { say('Revisá el email: parece incompleto.', 'err'); form.email.focus(); return; }
      const lines = [
        'Hola GENEOS, quiero solicitar una demo de GEAGRO ' + (d.version || '') + '.',
        'Nombre: ' + d.nombre,
        d.empresa && 'Establecimiento: ' + d.empresa,
        'Email: ' + d.email,
        d.telefono && 'Teléfono: ' + d.telefono,
        d.localidad && 'Localidad: ' + d.localidad,
        d.superficie && 'Superficie: ' + d.superficie + ' ha',
        d.mensaje && 'Mensaje: ' + d.mensaje,
      ].filter(Boolean);
      window.open('https://wa.me/' + WHATSAPP + '?text=' + encodeURIComponent(lines.join('\n')), '_blank', 'noopener');
      say('Abrimos WhatsApp con tu pedido listo para enviar.', 'ok');
    });
  }
  document.querySelectorAll('.ga-faq-list').forEach((list) => {
    const items = list.querySelectorAll('details');
    items.forEach((d) => d.addEventListener('toggle', () => {
      if (d.open) items.forEach((o) => { if (o !== d) o.open = false; });
    }));
  });
})();
