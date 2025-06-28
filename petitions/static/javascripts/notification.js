document.addEventListener('DOMContentLoaded', () => {
  const notificationsList = document.getElementById('notifications-list');
  const filterStatus = document.getElementById('filter-status');
  const sortOrder = document.getElementById('sort-order');
  const markAllReadBtn = document.getElementById('mark-all-read');

  function createNotificationItem(notif) {
    const li = document.createElement('li');
    li.className = 'notification-item';
    if (!notif.is_read) {
      li.classList.add('unread');
    }
    li.dataset.id = notif.id;

    const messageSpan = document.createElement('span');
    messageSpan.textContent = notif.message;

    const dateSpan = document.createElement('small');
    dateSpan.textContent = new Date(notif.created_at).toLocaleString('it-IT', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });

    if (notif.link) {
      const link = document.createElement('a');
      link.href = notif.link;
      link.target = '_blank';
      link.appendChild(messageSpan);
      li.appendChild(link);
    } else {
      li.appendChild(messageSpan);
    }

    li.appendChild(dateSpan);

    li.addEventListener('click', () => {
      markAsRead(notif.id, li);
      if (notif.link) {
        window.open(notif.link, '_blank');
      }
    });

    return li;
  }

  function markAsRead(notificationId, element) {
    fetch(`${MARK_NOTIFICATION_URL}/${notificationId}/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCSRFToken(),
      },
      credentials: 'same-origin',
    })
    .then(response => {
      if (!response.ok) throw new Error('Errore nel segnare come letta');
      return response.json();
    })
    .then(data => {
      if (data.status === 'ok' && element.classList.contains('unread')) {
        element.classList.remove('unread');
        element.style.fontWeight = 'normal';

        const unreadCountElement = document.getElementById('unread-count');
        if (unreadCountElement) {
          let count = parseInt(unreadCountElement.textContent) || 0;
          count = Math.max(0, count - 1);
          unreadCountElement.textContent = count;
          if (count === 0) unreadCountElement.classList.add('hidden');

          const notificationBell = document.getElementById('notification-bell');
          if (notificationBell && count === 0) {
            notificationBell.classList.remove('has-notifications');
          }
        }
      }
    })
    .catch(error => console.error('Errore:', error));
  }

  function getCSRFToken() {
    const match = document.cookie.match(/csrftoken=([^;]+)/);
    return match ? match[1] : '';
  }

  function filterAndSortNotifications(notifications) {
    let filtered = [...notifications];

    const statusFilter = filterStatus.value;
    if (statusFilter === 'unread') filtered = filtered.filter(n => !n.is_read);
    else if (statusFilter === 'read') filtered = filtered.filter(n => n.is_read);

    const sort = sortOrder.value;
    filtered.sort((a, b) => sort === 'oldest'
      ? new Date(a.created_at) - new Date(b.created_at)
      : new Date(b.created_at) - new Date(a.created_at)
    );

    return filtered;
  }

  function renderNotifications(notifications) {
    notificationsList.innerHTML = '';
    notifications.forEach(notif => {
      const li = createNotificationItem(notif);
      notificationsList.appendChild(li);
    });
  }

  const notificationsData = document.getElementById('notifications-data');
  if (notificationsData) {
    let notifications = JSON.parse(notificationsData.textContent);
    renderNotifications(filterAndSortNotifications(notifications));

    filterStatus.addEventListener('change', () => {
      renderNotifications(filterAndSortNotifications(notifications));
    });

    sortOrder.addEventListener('change', () => {
      renderNotifications(filterAndSortNotifications(notifications));
    });

    markAllReadBtn.addEventListener('click', () => {
      const unread = notifications.filter(n => !n.is_read);
      if (!unread.length) return;

      markAllReadBtn.disabled = true;
      let completed = 0;

      unread.forEach(notif => {
        fetch(`${MARK_NOTIFICATION_URL}/${notif.id}/`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken(),
          },
          credentials: 'same-origin',
        })
        .then(response => response.ok ? response.json() : Promise.reject())
        .then(data => {
          if (data.status === 'ok') {
            notif.is_read = true;
            completed++;
            if (completed === unread.length) {
              renderNotifications(filterAndSortNotifications(notifications));
              updateBadgeAndBell(notifications);
            }
          }
        })
        .catch(() => {
          completed++;
          if (completed === unread.length) {
            renderNotifications(filterAndSortNotifications(notifications));
            updateBadgeAndBell(notifications);
          }
        });
      });
    });

    function updateBadgeAndBell(notifications) {
      const unreadCountElement = document.getElementById('unread-count');
      const notificationBell = document.getElementById('notification-bell');
      const unreadCount = notifications.filter(n => !n.is_read).length;

      if (unreadCountElement) {
        unreadCountElement.textContent = unreadCount;
        unreadCountElement.classList.toggle('hidden', unreadCount === 0);
      }
      if (notificationBell && unreadCount === 0) {
        notificationBell.classList.remove('has-notifications');
      }

      markAllReadBtn.disabled = false;
    }
  } else {
    console.warn('Elemento notifications-data non trovato');
  }
});
