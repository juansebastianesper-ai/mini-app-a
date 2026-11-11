const categorySelect = document.querySelector("#category-select");
const fromSelect = document.querySelector("#from-unit");
const toSelect = document.querySelector("#to-unit");
const valueInput = document.querySelector("#input-value");
const resultOutput = document.querySelector("#result-value");
const statusMessage = document.querySelector("#conversion-status");
const copyButton = document.querySelector("#copy-button");

let unitCatalog = {};
let requestNumber = 0;

function setStatus(message, isError = false) {
  statusMessage.textContent = message;
  statusMessage.classList.toggle("error", isError);
}

function populateUnits(category, preferredFrom, preferredTo) {
  const units = unitCatalog[category].units;
  const options = Object.entries(units)
    .map(([code, unit]) => `<option value="${code}">${unit.label}</option>`)
    .join("");

  fromSelect.innerHTML = options;
  toSelect.innerHTML = options;
  fromSelect.value = preferredFrom in units ? preferredFrom : Object.keys(units)[0];
  toSelect.value = preferredTo in units ? preferredTo : Object.keys(units)[1] ?? Object.keys(units)[0];
}

function formatValue(value) {
  return new Intl.NumberFormat("es-ES", {
    maximumSignificantDigits: 10,
  }).format(value);
}

async function convert() {
  const currentRequest = ++requestNumber;
  const rawValue = valueInput.value;
  if (rawValue.trim() === "" || !Number.isFinite(Number(rawValue))) {
    resultOutput.value = "—";
    copyButton.disabled = true;
    setStatus("Introduce un valor numérico válido.", true);
    return;
  }

  try {
    const response = await fetch("/api/convert", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        category: categorySelect.value,
        from_unit: fromSelect.value,
        to_unit: toSelect.value,
        value: Number(rawValue),
      }),
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.detail ?? "No se pudo realizar la conversión.");
    }
    if (currentRequest !== requestNumber) return;

    resultOutput.value = formatValue(data.value);
    copyButton.disabled = false;
    setStatus(`${formatValue(Number(rawValue))} ${fromSelect.value} = ${formatValue(data.value)} ${toSelect.value}`);
  } catch (error) {
    if (currentRequest !== requestNumber) return;
    resultOutput.value = "—";
    copyButton.disabled = true;
    setStatus(error.message || "No se pudo realizar la conversión.", true);
  }
}

async function initialize() {
  try {
    const response = await fetch("/api/units");
    if (!response.ok) throw new Error("No se pudieron cargar las unidades.");
    unitCatalog = await response.json();

    for (const [code, category] of Object.entries(unitCatalog)) {
      categorySelect.add(new Option(category.label, code));
    }
    categorySelect.value = "longitud";
    populateUnits("longitud", "m", "km");
    await convert();
  } catch (error) {
    setStatus(error.message || "No se pudo iniciar el conversor.", true);
    valueInput.disabled = true;
    categorySelect.disabled = true;
    fromSelect.disabled = true;
    toSelect.disabled = true;
  }
}

categorySelect.addEventListener("change", () => populateUnits(categorySelect.value));
categorySelect.addEventListener("change", convert);
fromSelect.addEventListener("change", convert);
toSelect.addEventListener("change", convert);
valueInput.addEventListener("input", convert);

document.querySelector("#swap-button").addEventListener("click", () => {
  const previousFrom = fromSelect.value;
  fromSelect.value = toSelect.value;
  toSelect.value = previousFrom;
  convert();
});

copyButton.addEventListener("click", async () => {
  try {
    await navigator.clipboard.writeText(resultOutput.value);
    setStatus("Resultado copiado al portapapeles.");
  } catch {
    setStatus("No se pudo copiar. Selecciona el resultado para copiarlo.", true);
  }
});

document.querySelector("#conversion-form").addEventListener("submit", (event) => {
  event.preventDefault();
});

initialize();
