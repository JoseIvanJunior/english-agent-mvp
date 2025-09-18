self.addEventListener("push", function(event) {
  const data = event.data ? event.data.json() : {title: "Reminder", body: "Time to study!"};
  event.waitUntil(
    self.registration.showNotification(data.title, { body: data.body })
  );
});
