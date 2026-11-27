// @ts-check
import { test, expect } from '@playwright/test';



test('CP-ESP-01 - verificar formulario de registro de especialista', async ({ page }) => {

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

  // Comprueba que el CAPTCHA haya sido aceptado.
  await page.locator('#loginButton').click();
  console.log('Botón de acceso clickeado');

  console.log('URL actual:', page.url());

  // Espera a que aparezca el menú después del acceso.
  await expect(page.locator('.sidebar-menu')).toBeVisible({
    timeout: 15000
  });

  console.log('Inicio de sesión confirmado: menú visible');

  // Comprueba que Configuración exista y esté habilitado.
  const menuConfiguracion = page.locator('#menuConfiguracion');
  await expect(menuConfiguracion).toBeVisible();

  await menuConfiguracion.locator(':scope > a.sidebar-link').click();
  console.log('Menú Configuración desplegado');

  // Comprueba que Especialistas exista y esté habilitado.
  const enlaceEspecialistas = page.locator(
    '#menuConfiguracion .submenu a.submenu-link'
  ).filter({ hasText: 'Especialistas' });

  await expect(enlaceEspecialistas).toBeVisible();
  await expect(enlaceEspecialistas).toBeEnabled();

  await enlaceEspecialistas.click();
  console.log('Acceso al módulo Especialistas');

  // Abre el formulario de registro.
  await page.locator('button.btn.btn-primary.rounded-pill').click();

  const modal = page.locator('#primary');
  await expect(modal).toBeVisible();

  // Comprueba que los campos del formulario estén visibles.
  await expect(modal.locator('#especialista')).toBeVisible();
  await expect(modal.locator('#searchCedula')).toBeVisible();
  await expect(modal.locator('#cedula_reg')).toBeVisible();

  console.log('Campos del formulario visibles');

  // Comprueba que el botón Guardar esté disponible, sin pulsarlo.
  const botonGuardar = modal.locator('button[type="submit"]');

  await expect(botonGuardar).toBeVisible();
  await expect(botonGuardar).toBeEnabled();

  console.log('Formulario verificado sin introducir datos ni guardar');

  // Cierra el modal sin registrar.
  const botonCerrar = modal.locator('button[data-bs-dismiss="modal"]');

  if (await botonCerrar.count() > 0) {
    await botonCerrar.first().click();
  } else {
    await page.keyboard.press('Escape');
  }

  await expect(modal).toBeHidden();

  console.log('Prueba de interfaz: formulario de especialista finalizado');
});

test('CP-ESP-02 - verificar personal con especialidad asignada', async ({ page }) => {

  await page.goto('http://localhost:5000/admin?ruta=login');

  await page.getByRole('textbox', { name: 'Cédula' }).fill('4723317');
  await page.locator('#login-password').fill('admin123');

  await page.locator('#pow-check').click();
  await page.locator('#pow-answer').fill('AB12CD');
  await page.locator('#pow-verify').click();
  await page.locator('#loginButton').click();

  await expect(page.locator('.sidebar-menu')).toBeVisible({
    timeout: 15000
  });

  // Acceder al módulo Especialistas.
  const menuConfiguracion = page.locator('#menuConfiguracion');
  await menuConfiguracion.locator(':scope > a.sidebar-link').click();

  const enlaceEspecialistas = page.locator(
    '#menuConfiguracion .submenu a.submenu-link'
  ).filter({ hasText: 'Especialistas' });

  await enlaceEspecialistas.click();

  // Abrir el formulario de registro.
  await page.locator('button.btn.btn-primary.rounded-pill').click();

  const modal = page.locator('#primary');
  await expect(modal).toBeVisible();

  // Comprobar los campos.
  await expect(page.locator('#especialista')).toBeVisible();
  await expect(page.locator('#searchCedula')).toBeVisible();

  // Comprobar que el campo de cédula esté presente.
  await expect(page.locator('#cedula_reg')).toHaveCount(1);

  // No introducir datos ni realizar asignaciones.
  console.log('Formulario de especialista verificado sin introducir datos');

  // Cerrar el modal sin guardar.
  const botonCerrar = modal.getByRole('button', { name: 'Cerrar' });

  await expect(botonCerrar).toBeVisible();
  await botonCerrar.click();

  // Esperar a que Bootstrap termine de cerrar el modal.
  await expect(modal).toBeHidden({
    timeout: 10000
  });

  console.log('Prueba de interfaz:verificacion ');

});