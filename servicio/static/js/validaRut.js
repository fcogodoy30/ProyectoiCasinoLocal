function validarRut(rut) {
  rut = rut.replace(/\./g, "").replace(/-/g, "").toUpperCase();

  if (!/^\d{7,8}[0-9K]$/.test(rut)) {
      return false;
  }

  let cuerpo = rut.slice(0, -1);
  let dv = rut.slice(-1);

  let suma = 0;
  let multiplo = 2;

  for (let i = cuerpo.length - 1; i >= 0; i--) {
      suma += parseInt(cuerpo.charAt(i)) * multiplo;
      multiplo = multiplo === 7 ? 2 : multiplo + 1;
  }

  let resto = suma % 11;
  let dvCalculado = resto === 1 ? 'K' : (11 - resto).toString();
  dvCalculado = resto === 0 ? '0' : dvCalculado;

  return dv === dvCalculado;
}

function formatearRut(rut) {
  rut = rut.replace(/\./g, "").replace(/-/g, "");
  return rut.replace(/^(\d{1,2})(\d{3})(\d{3})([0-9K])$/, "$1.$2.$3-$4");
}

function validarRutInput() {
  const rutInput = document.getElementById('id_rut');
  const rutValue = rutInput.value;
  const validationMessage = document.getElementById('rut-validation-message');

  // Formatear el RUT y actualizar el valor del input
  const rutFormateado = formatearRut(rutValue);
  rutInput.value = rutFormateado;

  if (validarRut(rutFormateado)) {
      rutInput.setCustomValidity('');
      rutInput.style.borderColor = 'green';
      validationMessage.textContent = 'RUT válido';
      validationMessage.style.color = 'green';
  } else {
      rutInput.setCustomValidity('RUT inválido');
      rutInput.style.borderColor = 'red';
      validationMessage.textContent = 'RUT inválido';
      validationMessage.style.color = 'red';
  }
}

document.addEventListener('DOMContentLoaded', function () {
  const rutInput = document.getElementById('id_rut');
  rutInput.addEventListener('input', validarRutInput);
});
