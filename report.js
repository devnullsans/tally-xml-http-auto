window.addEventListener("load", () => {
  const data = {
    url: location.href,
    userAgent: navigator.userAgent,
    timing: performance.timing,
    timestamp: Date.now(),
  };
  fetch("https://postsinn.vercel.app/api/report", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
});
