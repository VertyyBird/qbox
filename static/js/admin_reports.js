// Qbox admin report details modal
(function () {
  const backdrop = document.getElementById('report-detail-modal');
  if (!backdrop) return;

  const closeBtn = backdrop.querySelector('[data-report-detail-close]');
  const list = backdrop.querySelector('[data-report-detail-list]');

  function openModal(reportsJson) {
    list.innerHTML = '';
    try {
      const reports = JSON.parse(reportsJson);
      reports.forEach((item) => {
        const li = document.createElement('li');
        li.textContent = `${item.reason || 'No reason provided.'} (${item.created_at || 'unknown'})`;
        list.appendChild(li);
      });
    } catch (e) {
      const li = document.createElement('li');
      li.textContent = 'Unable to load report reasons.';
      list.appendChild(li);
    }
    backdrop.classList.add('modal-open');
  }

  function closeModal() {
    backdrop.classList.remove('modal-open');
    list.innerHTML = '';
  }

  document.querySelectorAll('[data-report-detail]').forEach((btn) => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      const payload = btn.getAttribute('data-report-detail');
      if (payload) {
        openModal(payload);
      }
    });
  });

  backdrop.addEventListener('click', (e) => {
    if (e.target === backdrop) {
      closeModal();
    }
  });

  if (closeBtn) {
    closeBtn.addEventListener('click', (e) => {
      e.preventDefault();
      closeModal();
    });
  }
})();
