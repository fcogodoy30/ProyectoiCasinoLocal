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
    if (activeInput.id === 'id_password1') {
      document.getElementById('id_password2').focus();
      showKeyboard('id_password2');
    } else if (activeInput.id === 'id_password2') {
      hideKeyboard();
    }
  } else {
    // Verificar longitud máxima de 4 dígitos para la contraseña
    if ((activeInput.id === 'id_password1' || activeInput.id === 'id_password2') && activeInput.value.length >= 4) {
      return;
    }
    activeInput.value += key;
  }
}

document.getElementById('Form').addEventListener('submit', function () {
  document.getElementById('password').value = document.getElementById('id_password1').value;
});

document.getElementById('Form').addEventListener('submit', function (event) {
  var loginButton = document.getElementById('guardar');
  var spinner = document.getElementById('spinner');

  loginButton.style.display = 'none';
  spinner.style.display = 'block';
});

document.addEventListener('DOMContentLoaded', function() {
  document.getElementById('id_password1').focus();
});

document.addEventListener('DOMContentLoaded', function() {
  var password1Input = document.getElementById('id_password1');
  var password2Input = document.getElementById('id_password2');
  var mensajeError = document.getElementById('mensaje-error');
  var passwordPattern = /^[0-9]{4}$/;

  password2Input.addEventListener('focus', function() {
    if (!usingVirtualKeyboard) return;
    showKeyboard('id_password2');
  });

});

function validatePasswords() {
  var password1 = document.getElementById('id_password1').value;
  var password2 = document.getElementById('id_password2').value;
  if (password1 !== password2) {
    document.getElementById('mensaje-error').textContent = 'Las contraseñas no coinciden.';
    return false;
  }
  return true;
}
