document.addEventListener('DOMContentLoaded', () => {
  // Contenitore notifiche
  const notificationsList = document.getElementById('notifications-list');

  // Funzione per creare un elemento notifica
  function createNotificationItem(notif) {
    const li = document.createElement('li');
    li.className = 'notification-item';
    if (!notif.is_read) {
      li.classList.add('unread');
    }
    li.textContent = notif.message;

    // Se c'è un link, rendi cliccabile
    if (notif.link) {
      li.style.cursor = 'pointer';
      li.addEventListener('click', () => {
        // Apri link in nuova scheda
        window.open(notif.link, '_blank');

        // Segna come letta
        markAsRead(notif.id, li);
      });
    } else {
      // Se non c'è link, solo segna come letta al click
      li.addEventListener('click', () => {
        markAsRead(notif.id, li);
      });
    }

    return li;
  }

  // Funzione per marcare come letta (aggiorna frontend e backend)
  function markAsRead(notificationId, element) {
    if (element.classList.contains('unread')) {
      // Aggiorna stile
      element.classList.remove('unread');

      // Chiamata ajax per aggiornare backend (modifica stato is_read)
      fetch(`/petitions/notifications/mark_read/${notificationId}/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCSRFToken(),
        },
      })
      .then(response => {
        if (!response.ok) {
          console.error('Errore nel segnare la notifica come letta');
          // Se vuoi puoi rimettere la classe unread
          element.classList.add('unread');
        }
      })
      .catch(error => {
        console.error('Errore di rete:', error);
        element.classList.add('unread');
      });
    }
  }

  // Funzione per prendere il CSRF token da cookie (Django standard)
  function getCSRFToken() {
    const cookieValue = document.cookie.match('(^|;)\\s*csrftoken\\s*=\\s*([^;]+)');
    return cookieValue ? cookieValue.pop() : '';
  }

  // Fetch notifiche dal backend (se vuoi caricarle via JS)
  // oppure potresti riceverle nel template con un JSON embed

  // Esempio dummy, sostituisci con dati reali o fetch
  const notifications = JSON.parse(document.getElementById('notifications-data').textContent);

  notifications.forEach(notif => {
    const li = createNotificationItem(notif);
    notificationsList.appendChild(li);
  });
});
