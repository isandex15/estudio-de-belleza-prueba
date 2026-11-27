
// @ts-check
import { test, expect } from '@playwright/test';

test('editar telefono y direccion de empresa', async ({ page }) => {
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

  console.log('URL actual:', page.url());

  await expect(page.locator('.sidebar-menu')).toBeVisible({
    timeout: 15000
  });

  console.log('Inicio de sesión confirmado: menú visible');

  await page.locator('#menuConfiguracion > a.sidebar-link').click();
  console.log('Menú Configuración desplegado');

  const enlaceEmpresa = page.locator('#enlaceRegistrarEmpresa');

  await expect(enlaceEmpresa).toBeVisible();
  await expect(enlaceEmpresa).toBeEnabled();

  await enlaceEmpresa.click();
  console.log('Acceso al módulo Empresa');

  const botonEditar = page.locator(
    '#contenedorEmpresas button[data-bs-target="#exampleModal"]'
  ).first();

  await expect(botonEditar).toBeVisible();

  const nombre = (await botonEditar.getAttribute('data-nombre')) ?? '';
  const email = (await botonEditar.getAttribute('data-email')) ?? '';
  const descripcion = (await botonEditar.getAttribute('data-descripcion_empresa')) ?? '';

  await botonEditar.click();
  await expect(page.locator('#exampleModal')).toBeVisible();

  await page.locator('#exampleModal #nombre').fill(nombre);
  await page.locator('#exampleModal #email').fill(email);
  await page.locator('#exampleModal #descripcion_empresa').fill(descripcion);

  await page.locator('#exampleModal #telefono').fill('04121234568');
  await page.locator('#exampleModal #direccion').fill('Av. Principal, Centro');

  console.log('Teléfono y dirección modificados');

  await page.locator('#exampleModal button[form="editar"]').click();
  console.log('Botón Editar clickeado');

  await expect(page.locator('#contenedorEmpresas')).toContainText('04121234568');
  await expect(page.locator('#contenedorEmpresas')).toContainText('Av. Principal, Centro');

  console.log('Empresa actualizada correctamente');
});
