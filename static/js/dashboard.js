// ── Gráfica de ventas (Chart.js) ─────────────────
function initGraficaVentas(labels, datos) {
  const ctx = document.getElementById('grafica-ventas');
  if (!ctx) return;

  new Chart(ctx, {
    type: 'line',
    data: {
      labels,
      datasets: [{
        label: 'Ventas (Bs.)',
        data: datos,
        borderColor: '#2355a0',
        backgroundColor: 'rgba(35,85,160,.08)',
        borderWidth: 2.5,
        pointBackgroundColor: '#f5a623',
        pointBorderColor: '#fff',
        pointRadius: 5,
        tension: 0.4,
        fill: true
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: '#0f2042',
          titleColor: '#fff',
          bodyColor: '#7eb8f7',
          padding: 12,
          callbacks: {
            label: ctx => `Bs. ${ctx.parsed.y.toFixed(2)}`
          }
        }
      },
      scales: {
        x: { grid: { display: false }, ticks: { font: { family: 'DM Sans' } } },
        y: {
          grid: { color: 'rgba(0,0,0,.05)' },
          ticks: {
            font: { family: 'DM Sans' },
            callback: v => `Bs. ${v}`
          }
        }
      }
    }
  });
}

// ── Gráfica de productos top (doughnut) ──────────
function initGraficaProductos(labels, datos) {
  const ctx = document.getElementById('grafica-productos');
  if (!ctx) return;

  new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels,
      datasets: [{
        data: datos,
        backgroundColor: [
          '#2355a0','#f5a623','#16a34a','#4a90d9','#fad07a',
          '#1a3460','#f7bc52','#7eb8f7'
        ],
        borderWidth: 2,
        borderColor: '#fff'
      }]
    },
    options: {
      responsive: true,
      cutout: '65%',
      plugins: {
        legend: {
          position: 'bottom',
          labels: { font: { family: 'DM Sans', size: 12 }, padding: 16 }
        }
      }
    }
  });
}

// ── Validar comprobante desde el dashboard ────────
function validarComprobante(idTransaccion, accion) {
  const label = accion === 'aprobar' ? 'aprobar' : 'rechazar';
  if (!confirm(`¿Seguro que quieres ${label} este comprobante?`)) return;

  const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value
                 || getCookie('csrftoken');

  fetch(`/pagos/validar/${idTransaccion}/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': csrfToken
    },
    body: JSON.stringify({ accion })
  })
  .then(r => r.json())
  .then(data => {
    if (data.ok) {
      mostrarToast(data.mensaje);
      // Ocultar la card del comprobante
      document.querySelector(`[data-transaccion="${idTransaccion}"]`)
              ?.remove();
    } else {
      mostrarToast(data.error || 'Error al procesar', 'error');
    }
  })
  .catch(() => mostrarToast('Error de conexión', 'error'));
}

// ── Util: obtener cookie CSRF ────────────────────
function getCookie(name) {
  let valor = null;
  document.cookie.split(';').forEach(c => {
    const [k, v] = c.trim().split('=');
    if (k === name) valor = decodeURIComponent(v);
  });
  return valor;
}