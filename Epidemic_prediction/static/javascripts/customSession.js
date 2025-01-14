if (!localStorage.getItem("session_id")) {
    localStorage.setItem("session_id", "session_" + Date.now());
}