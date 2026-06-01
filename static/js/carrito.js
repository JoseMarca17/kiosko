// ── Estado del carrito (persiste en sessionStorage) ──
const Carrito = {
  items: JSON.parse(sessionStorage.getItem('carrito') || '[]'),

  guardar() {
    sessionStorage.setItem('carrito', JSON.stringify(this.items));
    this.actualizarBadge();
    this.renderItems();
  },

  agregar(producto) {
    const existe = this.items.find(i => i.id === producto.id);
    if (existe) {
      existe.cantidad += 1;
    } else {
      this.items.push({ ...producto, cantidad: 1 });
    }
    this.guardar();
    this.abrirSidebar();
    mostrarToast(`${producto.nombre} agregado al carrito`);
  },

  cambiarCantidad(id, delta) {
    const item = this.items.find(i => i.id === id);
    if (!item) return;
    item.cantidad += delta;
    if (item.cantidad <= 0) this.items = this.items.filter(i => i.id !== id);
    this.guardar();
  },

  eliminar(id) {
    this.items = this.items.filter(i => i.id !== id);
    this.guardar();
  },

  vaciar() {
    this.items = [];
    this.guardar();
  },

  total() {
    return this.items.reduce((acc, i) => acc + (i.precio * i.cantidad), 0);
  },

  totalItems() {
    return this.items.reduce((acc, i) => acc + i.cantidad, 0);
  },

  actualizarBadge() {
    const badge = document.querySelector('.cart-badge .badge');
    if (!badge) return;
    const total = this.totalItems();
    badge.textContent = total;
    badge.style.display = total > 0 ? 'flex' : 'none';
  },

  renderItems() {
    const container = document.getElementById('cart-items');
    if (!container) return;

    if (this.items.length === 0) {
      container.innerHTML = `
        <div style="text-align:center;padding:3rem 1rem;color:var(--color-text-muted)">
          <div style="font-size:2.5rem;margin-bottom:.75rem">🛒</div>
          <p>Tu carrito está vacío</p>
        </div>`;
    } else {
      container.innerHTML = this.items.map(item => `
        <div class="cart-item" data-id="${item.id}">
          <img class="cart-item-img"
               src="${item.imagen || '/static/img/placeholder.jpg'}"
               alt="${item.nombre}">
          <div class="cart-item-info">
            <div class="cart-item-name">${item.nombre}</div>
            <div class="cart-item-price">Bs. ${(item.precio * item.cantidad).toFixed(2)}</div>
            <div class="cart-qty" style="margin-top:.4rem">
              <button onclick="Carrito.cambiarCantidad(${item.id}, -1)">−</button>
              <span style="font-weight:600;min-width:20px;text-align:center">${item.cantidad}</span>
              <button onclick="Carrito.cambiarCantidad(${item.id}, +1)">+</button>
            </div>
          </div>
          <button onclick="Carrito.eliminar(${item.id})"
                  style="background:none;border:none;color:var(--color-text-muted);cursor:pointer;font-size:1.1rem;padding:.25rem">✕</button>
        </div>
      `).join('');
    }

    const totalEl = document.getElementById('cart-total');
    if (totalEl) totalEl.textContent = `Bs. ${this.total().toFixed(2)}`;
  },

  abrirSidebar() {
    document.getElementById('cart-sidebar')?.classList.add('open');
    document.getElementById('cart-overlay')?.classList.add('active');
  },

  cerrarSidebar() {
    document.getElementById('cart-sidebar')?.classList.remove('open');
    document.getElementById('cart-overlay')?.classList.remove('active');
  }
};

// ── Toast ────────────────────────────────────────
function mostrarToast(mensaje, tipo = 'success') {
  let wrap = document.getElementById('toast-wrap');
  if (!wrap) {
    wrap = document.createElement('div');
    wrap.id = 'toast-wrap';
    wrap.style.cssText = `
      position:fixed;bottom:1.5rem;right:1.5rem;
      display:flex;flex-direction:column;gap:.5rem;z-index:999`;
    document.body.appendChild(wrap);
  }
  const toast = document.createElement('div');
  toast.style.cssText = `
    background:var(--blue-900);color:var(--white);
    padding:.75rem 1.25rem;border-radius:var(--radius-md);
    font-size:.875rem;font-family:var(--font-display);
    box-shadow:var(--shadow-lg);animation:toastIn .25s ease;
    border-left:4px solid var(--color-accent);
    max-width:300px;`;
  toast.textContent = mensaje;
  wrap.appendChild(toast);
  setTimeout(() => toast.remove(), 3000);
}

const style = document.createElement('style');
style.textContent = `
  @keyframes toastIn {
    from { opacity:0; transform:translateX(20px); }
    to   { opacity:1; transform:translateX(0); }
  }`;
document.head.appendChild(style);

document.addEventListener('DOMContentLoaded', () => {
  Carrito.actualizarBadge();
  Carrito.renderItems();

  document.getElementById('cart-overlay')?.addEventListener('click', () => {
    Carrito.cerrarSidebar();
  });
});