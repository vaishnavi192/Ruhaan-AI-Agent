// src/Frontend/utils/reminderNotifications.js

export function requestNotificationPermission() {
  if ("Notification" in window && Notification.permission !== "granted") {
    Notification.requestPermission();
  }
}

export function scheduleReminderNotification(reminder) {
  if (!reminder.reminder_time) return;
  const now = new Date();
  let target = null;

  // --- Relative time: e.g. 'in 5 minutes', 'after 2m', 'for 10 mins', 'in 1 hour', 'after 30 seconds' ---
  const relMatch = reminder.reminder_time.match(/(?:in|after|for)\s*(\d+)\s*(seconds?|minutes?|mins?|hours?|h|m|s)/i);
  if (relMatch) {
    let amount = parseInt(relMatch[1], 10);
    let unit = relMatch[2].toLowerCase();
    let ms = 0;
    if (unit.startsWith('h')) ms = amount * 60 * 60 * 1000;
    else if (unit.startsWith('m')) ms = amount * 60 * 1000;
    else if (unit.startsWith('s')) ms = amount * 1000;
    target = new Date(now.getTime() + ms);
  }

  // --- Absolute time: e.g. '2:30pm', '14:45' ---
  if (!target) {
    const timeMatch = reminder.reminder_time.match(/(\d{1,2})(:(\d{2}))? ?([ap]m)?/i);
    if (timeMatch) {
      let hour = parseInt(timeMatch[1], 10);
      let minute = timeMatch[3] ? parseInt(timeMatch[3], 10) : 0;
      let ampm = timeMatch[4] ? timeMatch[4].toLowerCase() : null;
      if (ampm === "pm" && hour < 12) hour += 12;
      if (ampm === "am" && hour === 12) hour = 0;
      target = new Date(now.getFullYear(), now.getMonth(), now.getDate(), hour, minute, 0, 0);
      if (target < now) target.setDate(target.getDate() + 1); // If time has passed, set for tomorrow
    }
  }

  if (target) {
    const delay = target - now;
    setTimeout(() => {
      if (typeof reminder.onToast === "function") {
        reminder.onToast();
      }
      if ("Notification" in window && Notification.permission === "granted") {
        new Notification("Reminder", {
          body: reminder.reminder_text,
        });
      } else {
        alert("Reminder: " + reminder.reminder_text);
      }
    }, delay);
  }
}
