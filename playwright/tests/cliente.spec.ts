
// @ts-check
import { test, expect } from '@playwright/test';


test('registrar cliente', async ({ page }) => {
  // CP-CLI-01: Registrar cliente.

  // 1. Iniciar sesión.
  await page.goto('http://localhost:5000/admin?ruta=login');

  await page.getByRole('textbox', { name: 'Cédula' }).fill('4723317');
  await page.locator('#login-password').fill('admin123');

  await page.locator('#pow-check').click();

  await expect(page.locator('#pow-image')).toBeVisible();

  await page.locator('#pow-answer').fill('AB12CD');
  await page.locator('#pow-verify').click();


  await page.locator('#loginButton').click();

  await expect(page.locator('.sidebar-menu')).toBeVisible({
    timeout: 15000
  });

  console.log('Inicio de sesión confirmado: menú visible');

  // 2. Acceder al módulo Clientes.
  const enlaceClientes = page.locator(
    '.sidebar-menu a.sidebar-link[href="/admin?ruta=cliente"]'
  );

  await expect(enlaceClientes).toBeVisible();
  await expect(enlaceClientes).toBeEnabled();
  await enlaceClientes.click();
  console.log('Acceso al módulo Clientes');
  // 3. Verificar que se muestre la tabla.
  await expect(page.locator('#table1')).toBeVisible();

  // 4. Abrir el formulario de registro.
  const botonRegistrar = page.getByRole('button', {
    name: 'Registrar Clientes'
  });

  await expect(botonRegistrar).toBeVisible();
  await expect(botonRegistrar).toBeEnabled();
  await botonRegistrar.click();

  const modal = page.locator('#modalRegistrarCliente');
  await expect(modal).toBeVisible();

  // 5. Verificar que los campos estén visibles.
  await expect(page.locator('#cedula_reg')).toBeVisible();
  await expect(page.locator('#nombre_usuario_reg')).toBeVisible();
  await expect(page.locator('#apellido_usuario_reg')).toBeVisible();
  await expect(page.locator('#telefono_reg')).toBeVisible();
  await expect(page.locator('#direccion_reg')).toBeVisible();
  await expect(page.locator('#correo_reg')).toBeVisible();

  // 6. Completar los datos del cliente.
  await page.locator('#cedula_reg').fill('3196486');
  await page.locator('#nombre_usuario_reg').fill('Carlos');
  await page.locator('#apellido_usuario_reg').fill('Gonzalez');
  await page.locator('#telefono_reg').fill('0412123456');
  await page.locator('#direccion_reg').fill('Av Principal 123');
  await page.locator('#correo_reg').fill('carlogonzalez@gmail.com');

  // 7. Comprobar los datos introducidos.
  await expect(page.locator('#cedula_reg')).toHaveValue('3196486');
  await expect(page.locator('#nombre_usuario_reg')).toHaveValue('Carlos');
  await expect(page.locator('#apellido_usuario_reg')).toHaveValue('Gonzalez');
  await expect(page.locator('#telefono_reg')).toHaveValue('0412123456');
  await expect(page.locator('#direccion_reg')).toHaveValue('Av Principal 123');
  await expect(page.locator('#correo_reg')).toHaveValue('carlogonzalez@gmail.com');

  // 8. Verificar que el botón Guardar esté habilitado.
  const botonGuardar = modal.getByRole('button', {
    name: 'Guardar'
  });

  await expect(botonGuardar).toBeEnabled();

  // 9. Guardar el registro.
  await botonGuardar.click();
  console.log('Cliente registrado correctamente');

  // 10. Verificar el cierre del modal.
  await expect(modal).toBeHidden({
    timeout: 15000
  });

  // 11. Verificar el mensaje de respuesta.
  await expect(page.locator('.swal2-popup')).toBeVisible({
    timeout: 15000
  });

  console.log('Prueba de interfaz: registrar cliente finalizada');
});

test('validar campos obligatorios del cliente', async ({ page }) => {

  // 1. Iniciar sesión.
  await page.goto('http://localhost:5000/admin?ruta=login');

  await page.getByRole('textbox', { name: 'Cédula' }).fill('4723317');
  await page.locator('#login-password').fill('admin123');

  await page.locator('#pow-check').click();

  await expect(page.locator('#pow-image')).toBeVisible();

  await page.locator('#pow-answer').fill('AB12CD');
  await page.locator('#pow-verify').click();

  await page.locator('#loginButton').click();

  await expect(page.locator('.sidebar-menu')).toBeVisible({
    timeout: 15000
  });


  // 2. Acceder al módulo Clientes.
  const enlaceClientes = page.locator(
    '.sidebar-menu a.sidebar-link[href="/admin?ruta=cliente"]'
  );

  await expect(enlaceClientes).toBeVisible();
  await expect(enlaceClientes).toBeEnabled();

  await enlaceClientes.click();

  // 3. Comprobar que se muestre la tabla.
  await expect(page.locator('#table1')).toBeVisible();

  // 4. Abrir el formulario de registro.
  await page.getByRole('button', {
    name: 'Registrar Clientes'
  }).click();

  const modal = page.locator('#modalRegistrarCliente');

  await expect(modal).toBeVisible();
  // 5. Intentar enviar el formulario vacío.
  await page.locator(
    '#formRegistrarCliente button[type="submit"]'
  ).click();

  // 6. Comprobar los errores de los campos obligatorios.
  await expect(page.locator('#cedula_reg')).toHaveClass(/is-invalid/);
  await expect(page.locator('#nombre_usuario_reg')).toHaveClass(/is-invalid/);
  await expect(page.locator('#apellido_usuario_reg')).toHaveClass(/is-invalid/);
  await expect(page.locator('#telefono_reg')).toHaveClass(/is-invalid/);
  await expect(page.locator('#direccion_reg')).toHaveClass(/is-invalid/);
  await expect(page.locator('#correo_reg')).toHaveClass(/is-invalid/);
  // 7. Comprobar que el formulario continúa abierto.
  await expect(modal).toBeVisible();

  console.log('Prueba de interfaz: validación de campos obligatorios finalizada');
});



test('validar cédula de cliente existente', async ({ page }) => {

    // 1. Iniciar sesión.
    await page.goto('http://localhost:5000/admin?ruta=login');

    await page.getByRole('textbox', { name: 'Cédula' }).fill('4723317');
    await page.locator('#login-password').fill('admin123');

    await page.locator('#pow-check').click();

    await expect(page.locator('#pow-image')).toBeVisible();

    await page.locator('#pow-answer').fill('AB12CD');
    await page.locator('#pow-verify').click();

    await page.locator('#loginButton').click();

    await expect(page.locator('.sidebar-menu')).toBeVisible({
        timeout: 15000
    });

    // 2. Acceder al módulo Clientes.
    const enlaceClientes = page.locator(
        '.sidebar-menu a.sidebar-link[href="/admin?ruta=cliente"]'
    );

    await expect(enlaceClientes).toBeVisible();
    await expect(enlaceClientes).toBeEnabled();

    await enlaceClientes.click();

    // 3. Comprobar que se muestre la tabla.
    await expect(page.locator('#table1')).toBeVisible();

    // 4. Abrir el formulario de registro.
    await page.getByRole('button', {
        name: 'Registrar Clientes'
    }).click();

    const modal = page.locator('#modalRegistrarCliente');

    await expect(modal).toBeVisible();

    // 5. Introducir una cédula existente.
    await page.locator('#cedula_reg').fill('3196486');

    // 6. Salir del campo para ejecutar la validación.
    await page.locator('#cedula_reg').press('Tab');

    // 7. Comprobar la alerta.
    await expect(page.locator('.swal2-popup')).toBeVisible();

    await expect(page.locator('.swal2-title')).toHaveText('Advertencia');

    await expect(page.locator('.swal2-html-container'))
        .toHaveText('El cliente ya se encuentra registrado');

    // 8. Comprobar que la alerta se cierre al aceptar.
    await page.getByRole('button', { name: 'Aceptar' }).click();

    await expect(page.locator('.swal2-popup')).toBeHidden();

    // 9. Comprobar que la cédula haya sido limpiada.
    await expect(page.locator('#cedula_reg')).toHaveValue('');

    // 10. Comprobar que el formulario continúe abierto.
    await expect(modal).toBeVisible();

    console.log('Prueba de interfaz: validación de cédula existente finalizada');

});

test('editar cliente', async ({ page }) => {
  // CP-CLI-02: Editar cliente.

  // 1. Iniciar sesión.
  await page.goto('http://localhost:5000/admin?ruta=login');

  await page.getByRole('textbox', { name: 'Cédula' }).fill('4723317');
  await page.locator('#login-password').fill('admin123');
  console.log('Campo de contraseña llenado');

  await page.locator('#pow-check').click();
  console.log('Checkbox CAPTCHA clickeado');

  await expect(page.locator('#pow-image')).toBeVisible();

  await page.locator('#pow-answer').fill('AB12CD');
  await page.locator('#pow-verify').click();
  console.log('Botón de verificación CAPTCHA clickeado');

  await page.locator('#loginButton').click();
  console.log('Botón de acceso clickeado');

  await expect(page.locator('.sidebar-menu')).toBeVisible({
    timeout: 15000
  });

  console.log('Inicio de sesión confirmado: menú visible');

  // 2. Acceder al módulo Clientes.
  const enlaceClientes = page.locator(
    '.sidebar-menu a.sidebar-link[href="/admin?ruta=cliente"]'
  );

  await expect(enlaceClientes).toBeVisible();
  await enlaceClientes.click();
  console.log('Acceso al módulo Clientes');

  // 3. Verificar que la tabla esté visible.
  await expect(page.locator('#table1')).toBeVisible();

  // 4. Buscar el cliente mediante su cédula.
  const filaCliente = page.locator('#table1 tbody tr').filter({
    has: page.locator('td').filter({
      hasText: /^\s*3196486\s*$/
    })
  });

  await expect(filaCliente).toHaveCount(1);

  // 5. Verificar el botón Editar.
  const botonEditar = filaCliente.locator('button.btn-editar');

  await expect(botonEditar).toBeVisible();
  await expect(botonEditar).toBeEnabled();

  // 6. Abrir el formulario de edición.
  const modal = page.locator('#modalEditar');

  await botonEditar.click();
  await expect(modal).toBeVisible();

  // 7. Verificar los campos del formulario.
  await expect(page.locator('#cedula_edit')).toBeVisible();
  await expect(page.locator('#nombre_usuario_edit')).toBeVisible();
  await expect(page.locator('#apellido_usuario_edit')).toBeVisible();
  await expect(page.locator('#telefono_edit')).toBeVisible();
  await expect(page.locator('#direccion_edit')).toBeVisible();
  await expect(page.locator('#correo_edit')).toBeVisible();
  await expect(page.locator('#status_edit')).toBeVisible();

  // 8. Comprobar los datos cargados.
  await expect(page.locator('#cedula_edit')).toHaveValue('3196486');

  // 9. Modificar los datos del cliente.
  await page.locator('#nombre_usuario_edit').fill('Car');
  await page.locator('#apellido_usuario_edit').fill('González');
  await page.locator('#telefono_edit').fill('0414123488');
  await page.locator('#direccion_edit').fill('barquisimeto');
  await page.locator('#correo_edit').fill('carolinaactualizado@gmail.com');
  await page.locator('#status_edit').selectOption('1');

  // 10. Comprobar los datos modificados.
  await expect(page.locator('#nombre_usuario_edit')).toHaveValue('Car');
  await expect(page.locator('#apellido_usuario_edit')).toHaveValue('González');
  await expect(page.locator('#telefono_edit')).toHaveValue('0414123488');
  await expect(page.locator('#direccion_edit')).toHaveValue('barquisimeto');
  await expect(page.locator('#correo_edit')).toHaveValue('carolinaactualizado@gmail.com');
  await expect(page.locator('#status_edit')).toHaveValue('1');

  // 11. Verificar que el botón Editar esté habilitado.
  const botonGuardar = modal.getByRole('button', {
    name: 'Editar'
  });

  await expect(botonGuardar).toBeEnabled();

  // 12. Guardar los cambios.
  await botonGuardar.click();
  console.log('Cliente actualizado correctamente');

  // 13. Verificar el cierre del modal.
  await expect(modal).toBeHidden({
    timeout: 15000
  });

  await expect(page.locator('.swal2-popup')).toBeVisible({
    timeout: 15000
  });

  console.log('Prueba de interfaz: editar cliente finalizada');
});
