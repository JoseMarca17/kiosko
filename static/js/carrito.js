// ── Toast Notificación Premium (Definida primero) ────────────────────────────────────────
function mostrarToast(mensaje, tipo = 'success') {
  let wrap = document.getElementById('toast-wrap');
  if (!wrap) {
    wrap = document.createElement('div');
    wrap.id = 'toast-wrap';
    wrap.className = 'fixed bottom-6 right-6 flex flex-col gap-2 z-[9999]';
    document.body.appendChild(wrap);
  }
  const toast = document.createElement('div');
  toast.className = 'bg-emi-900 text-white px-5 py-3.5 rounded-xl text-xs font-bold shadow-2xl border-l-4 border-emi-gold flex items-center gap-2.5 min-w-[250px] transition-all transform translate-x-0 duration-300';
  
  // Icon
  const icon = document.createElement('i');
  icon.className = 'fa-solid fa-circle-check text-emi-gold text-sm';
  toast.appendChild(icon);
  
  // Text
  const text = document.createElement('span');
  text.textContent = mensaje;
  toast.appendChild(text);
  
  wrap.appendChild(toast);
  setTimeout(() => {
    toast.classList.add('opacity-0', 'translate-x-10');
    setTimeout(() => toast.remove(), 300);
  }, 3000);
}

// ── Estado del carrito (persiste en sessionStorage con sanitización) ──
const Carrito = {
  items: (() => {
    try {
      const stored = sessionStorage.getItem('carrito');
      if (!stored) return [];
      const parsed = JSON.parse(stored);
      if (Array.isArray(parsed)) {
        return parsed.map(item => ({
          id: parseInt(item.id),
          nombre: item.nombre || '',
          precio: parseFloat(item.precio.toString().replace(',', '.')) || 0,
          imagen: item.imagen || '',
          cantidad: parseInt(item.cantidad) || 1,
          notas: item.notas || ''
        }));
      }
    } catch(e) {
      console.error("Error parsing cart storage:", e);
    }
    return [];
  })(),

  guardar() {
    sessionStorage.setItem('carrito', JSON.stringify(this.items));
    this.actualizarBadge();
    this.renderItems();
  },

  agregar(producto, cantidad = 1) {
    const qty = parseInt(cantidad) || 1;
    const existe = this.items.find(i => i.id === producto.id);
    if (existe) {
      existe.cantidad += qty;
      // Combinar notas si existen y son diferentes
      if (producto.notas && existe.notas !== producto.notas) {
        existe.notas = existe.notas ? `${existe.notas}, ${producto.notas}` : producto.notas;
      }
    } else {
      this.items.push({ ...producto, cantidad: qty });
    }
    this.guardar();
    this.abrirSidebar();
    mostrarToast(`${producto.nombre} (${qty}) agregado al carrito`);
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
    const badge = document.getElementById('cart-count');
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
        <div class="text-center py-20 text-gray-400 opacity-60">
          <i class="fa-solid fa-box-open text-4xl mb-3 block"></i>
          <p class="text-sm font-medium">Tu carrito está vacío</p>
        </div>`;
    } else {
      container.innerHTML = this.items.map(item => `
        <div class="flex items-center gap-4 bg-gray-50 border border-gray-100 p-3 rounded-2xl relative" data-id="${item.id}">
          <div class="w-12 h-12 rounded-lg bg-white overflow-hidden border border-gray-100 flex-shrink-0">
            ${item.imagen ? `<img src="${item.imagen}" class="w-full h-full object-cover">` : `<div class="w-full h-full flex items-center justify-center text-gray-300 text-lg"><i class="fa-solid fa-burger"></i></div>`}
          </div>
          <div class="flex-1 min-w-0">
            <div class="text-xs font-bold text-gray-800 truncate leading-tight">${item.nombre}</div>
            <div class="text-xs font-black text-emi-900 mt-1">Bs. ${(item.precio * item.cantidad).toFixed(2)}</div>
            ${item.notas ? `<div class="text-[9px] text-gray-400 italic mt-0.5 truncate max-w-[150px]">Nota: ${item.notas}</div>` : ''}
            <div class="flex items-center gap-2 mt-2 bg-white border border-gray-200 rounded-lg p-1 inline-flex">
              <button onclick="Carrito.cambiarCantidad(${item.id}, -1)" class="w-6 h-6 flex items-center justify-center text-xs font-bold text-emi-600 hover:bg-gray-100 rounded transition-colors">−</button>
              <span class="text-xs font-bold text-gray-800 min-w-[15px] text-center">${item.cantidad}</span>
              <button onclick="Carrito.cambiarCantidad(${item.id}, 1)" class="w-6 h-6 flex items-center justify-center text-xs font-bold text-emi-600 hover:bg-gray-100 rounded transition-colors">+</button>
            </div>
          </div>
          <button onclick="Carrito.eliminar(${item.id})" class="absolute top-2 right-2 text-gray-400 hover:text-red-500 text-xs transition-colors p-1">
            ✕
          </button>
        </div>
      `).join('');
    }

    const totalEl = document.getElementById('cart-total');
    if (totalEl) totalEl.textContent = `Bs. ${this.total().toFixed(2)}`;
  },

  abrirSidebar() {
    const sidebar = document.getElementById('cart-sidebar');
    const overlay = document.getElementById('cart-overlay');
    if (sidebar && overlay) {
      sidebar.classList.remove('translate-x-full');
      sidebar.classList.add('translate-x-0');
      overlay.classList.remove('hidden');
      setTimeout(() => overlay.classList.remove('opacity-0'), 10);
    }
  },

  cerrarSidebar() {
    const sidebar = document.getElementById('cart-sidebar');
    const overlay = document.getElementById('cart-overlay');
    if (sidebar && overlay) {
      sidebar.classList.remove('translate-x-0');
      sidebar.classList.add('translate-x-full');
      overlay.classList.add('opacity-0');
      setTimeout(() => overlay.classList.add('hidden'), 300);
    }
  }
};

document.addEventListener('DOMContentLoaded', () => {
  Carrito.actualizarBadge();
  Carrito.renderItems();

  document.getElementById('cart-overlay')?.addEventListener('click', () => {
    Carrito.cerrarSidebar();
  });
});