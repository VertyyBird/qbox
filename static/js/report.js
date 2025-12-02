// Qbox reporting modal handling
(function () {
  const backdrop = document.getElementById('report-modal');
  if (!backdrop) return;

  const form = backdrop.querySelector('form');
  const answerIdInput = form.querySelector('input[name="answer_id"]');
  const closeBtn = backdrop.querySelector('[data-report-close]');

  function openModal(answerId, actionUrl) {
    answerIdInput.value = answerId;
    if (actionUrl) {
      form.setAttribute('action', actionUrl);
    }
    backdrop.classList.add('modal-open');
  }

  function closeModal() {
    backdrop.classList.remove('modal-open');
    form.reset();
  }

  document.querySelectorAll('[data-report-answer]').forEach((btn) => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      const answerId = btn.getAttribute('data-report-answer');
      const actionUrl = btn.getAttribute('data-action');
      if (!answerId) return;
      openModal(answerId, actionUrl);
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
