// ── Upload de comprobante ────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  const zona = document.getElementById('upload-zone');
  const input = document.getElementById('comprobante-input');
  const preview = document.getElementById('comprobante-preview');

  if (!zona || !input) return;

  // Click en zona
  zona.addEventListener('click', () => input.click());

  // Drag & drop
  zona.addEventListener('dragover', e => {
    e.preventDefault();
    zona.classList.add('dragover');
  });
  zona.addEventListener('dragleave', () => zona.classList.remove('dragover'));
  zona.addEventListener('drop', e => {
    e.preventDefault();
    zona.classList.remove('dragover');
    const archivo = e.dataTransfer.files[0];
    if (archivo) procesarArchivo(archivo);
  });

  // Input file
  input.addEventListener('change', () => {
    if (input.files[0]) procesarArchivo(input.files[0]);
  });

  function procesarArchivo(archivo) {
    if (!archivo.type.startsWith('image/')) {
      mostrarToast('Solo se permiten imágenes', 'error');
      return;
    }
    if (archivo.size > 5 * 1024 * 1024) {
      mostrarToast('La imagen no debe superar 5MB', 'error');
      return;
    }
    const reader = new FileReader();
    reader.onload = e => {
      if (preview) {
        preview.src = e.target.result;
        preview.style.display = 'block';
        zona.style.display = 'none';
      }
    };
    reader.readAsDataURL(archivo);

    // Crear un DataTransfer para asignar al input real del form
    const dt = new DataTransfer();
    dt.items.add(archivo);
    input.files = dt.files;
  }
});

// ── Copiar código de pedido ──────────────────────
function copiarCodigo(codigo) {
  navigator.clipboard.writeText(codigo).then(() => {
    mostrarToast(`Código ${codigo} copiado`);
  });
}

// ── Confirmar cancelación ────────────────────────
function confirmarCancelacion(url) {
  if (confirm('¿Seguro que quieres cancelar este pedido?')) {
    window.location.href = url;
  }
}