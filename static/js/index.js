
  // Spinning loading logo
  document.addEventListener('DOMContentLoaded', () => {
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
      form.addEventListener('submit', () => {
        document.getElementById('loadingSpinner').style.display = 'flex';
      });
    });
  });

document.addEventListener("DOMContentLoaded", function () {
  const buttons = document.querySelectorAll(".send-email");

  buttons.forEach((btn) => {
    btn.addEventListener("click", function (e) {
      e.preventDefault();

      const invoiceId = this.dataset.invoiceId;
      const spinner = this.querySelector(".spinner-border");
      spinner.classList.remove("d-none");

      fetch(`/finance/invoice/${invoiceId}/email/`, {
        method: "POST",
        headers: {
          "X-CSRFToken": getCookie("csrftoken"),
          "Content-Type": "application/json",
        },
      })
        .then((response) => {
          spinner.classList.add("d-none");
          if (!response.ok) {
            throw new Error("Email send failed.");
          }
          return response.json();
        })
        .then((data) => {
          alert(data.message);
        })
        .catch((error) => {
          console.error("Error:", error);
          alert("Failed to send invoice email.");
        });
    });
  });
});

// Helper to get CSRF token
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(
          cookie.substring(name.length + 1)
        );
        break;
      }
    }
  }
  return cookieValue;
}
