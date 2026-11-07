// Love Flower (ЛавФловер) UI Scripts

document.addEventListener("DOMContentLoaded", () => {
  // 1. Управление переключением типа доставки (Самовывоз / Курьер)
  const deliveryRadios = document.querySelectorAll('input[name="delivery_type"]');
  const addressGroup = document.getElementById("address-form-group");

  if (deliveryRadios.length && addressGroup) {
    const updateAddressVisibility = () => {
      const selected = document.querySelector('input[name="delivery_type"]:checked');
      if (selected && selected.value === "pickup") {
        addressGroup.style.display = "none";
        const input = addressGroup.querySelector("input");
        if (input) input.removeAttribute("required");
      } else {
        addressGroup.style.display = "block";
        const input = addressGroup.querySelector("input");
        if (input) input.setAttribute("required", "required");
      }
    };

    deliveryRadios.forEach((r) => r.addEventListener("change", updateAddressVisibility));
    updateAddressVisibility();
  }

  // 2. Маска ввода для российского номера телефона
  const phoneInputs = document.querySelectorAll('input[type="tel"]');
  phoneInputs.forEach((input) => {
    input.addEventListener("input", (e) => {
      let val = input.value.replace(/\D/g, "");
      if (!val) {
        input.value = "";
        return;
      }
      if (val[0] === "8" || val[0] === "7") {
        val = val.substring(1);
      }
      let formatted = "+7";
      if (val.length > 0) {
        formatted += " (" + val.substring(0, 3);
      }
      if (val.length >= 4) {
        formatted += ") " + val.substring(3, 6);
      }
      if (val.length >= 7) {
        formatted += "-" + val.substring(6, 8);
      }
      if (val.length >= 9) {
        formatted += "-" + val.substring(8, 10);
      }
      input.value = formatted;
    });
  });

  // 3. Быстрая сортировка в каталоге
  const sortSelect = document.getElementById("catalog-sort-select");
  if (sortSelect) {
    sortSelect.addEventListener("change", () => {
      const url = new URL(window.location.href);
      url.searchParams.set("sort", sortSelect.value);
      window.location.href = url.toString();
    });
  }

  // 4. Чекбокс «Можно сегодня»
  const readyTodayCheckbox = document.getElementById("ready-today-filter");
  if (readyTodayCheckbox) {
    readyTodayCheckbox.addEventListener("change", () => {
      const url = new URL(window.location.href);
      if (readyTodayCheckbox.checked) {
        url.searchParams.set("ready_today", "1");
      } else {
        url.searchParams.delete("ready_today");
      }
      window.location.href = url.toString();
    });
  }
});
