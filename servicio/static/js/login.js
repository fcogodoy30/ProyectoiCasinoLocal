document.addEventListener('DOMContentLoaded', function() {
  document.getElementById('id_rut').focus();
});

let activeInput = null;
let usingVirtualKeyboard = false;

function showKeyboard(inputId) {
  activeInput = document.getElementById(inputId);
  document.getElementById('keyboard').style.display = 'block';
  usingVirtualKeyboard = true;
}

function hideKeyboard() {
  document.getElementById('keyboard').style.display = 'none';
  usingVirtualKeyboard = false;
}

document.querySelectorAll('.keyboard button').forEach(button => {
  button.addEventListener('click', () => handleKeyPress(button.textContent));
});

function handleKeyPress(key) {
  if (!activeInput) return;

  if (key === '⌫') {
      activeInput.value = activeInput.value.slice(0, -1);
  } else if (key === 'Enter') {
      if (activeInput.id === 'id_rut') {
          document.getElementById('password').focus();
          showKeyboard('password');
      } else if (activeInput.id === 'password') {
          document.getElementById('loginForm').submit();
      }
      hideKeyboard();
  } else {
      // Verificar longitud máxima de 4 dígitos para la contraseña
      if (activeInput.id === 'password' && activeInput.value.length >= 4) {
          return;
      }
      activeInput.value += key;
  }

  if (activeInput.id === 'id_rut' && usingVirtualKeyboard) {
      validarRutInput();
  }
}
