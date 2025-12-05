document.addEventListener("DOMContentLoaded", function () {
  // Mở modal
  document.querySelectorAll(".js-open-review-modal").forEach(function (btn) {
    btn.addEventListener("click", function () {
      const id = btn.getAttribute("data-review-modal");
      const backdrop = document.getElementById("review-modal-" + id);
      if (backdrop) {
        backdrop.classList.add("is-visible");
      }
    });
  });

  // Đóng modal (nút Hủy & nút X)
  document.querySelectorAll(".js-close-review-modal").forEach(function (btn) {
    btn.addEventListener("click", function () {
      const id = btn.getAttribute("data-review-modal");
      const backdrop = document.getElementById("review-modal-" + id);
      if (backdrop) {
        backdrop.classList.remove("is-visible");
      }
    });
  });

  // Click ra ngoài khung modal cũng đóng
  document.querySelectorAll(".review-modal-backdrop").forEach(function (backdrop) {
    backdrop.addEventListener("click", function (e) {
      if (e.target === backdrop) {
        backdrop.classList.remove("is-visible");
      }
    });
  });
});
