import { expect, test } from '@playwright/test';

import { abrirModulo, iniciarSesion } from './auth';

test('mostrar formulario de registro de pago', async ({ page }) => {
  // CP-PAG-12: Muestra el formulario de registro de pago.

  // 1. Iniciar sesión.
  await iniciarSesion(page);

  // 2. Acceder al módulo Pagos.
  await abrirModulo(page, 'pagos');

  // 3. Verificar la tabla y abrir el formulario.
  await expect(page.locator('#table1')).toBeVisible();
  await page.getByRole('button', { name: 'Registrar Pagos' }).click();

  const modal = page.locator('#modalRegistrarPago');
  await expect(modal).toBeVisible();
  await expect(page.locator('#cedula_cliente')).toBeVisible();
  await expect(page.locator('#fecha_pago')).toHaveValue(/^\d{4}-\d{2}-\d{2}$/);
  await expect(page.locator('#comprobante_pago')).toBeVisible();
});

test('impedir enviar el formulario de pago incompleto', async ({ page }) => {
  // CP-PAG-13: Impide enviar el formulario de pago incompleto.

  // 1. Iniciar sesión.
  await iniciarSesion(page);

  // 2. Acceder al módulo Pagos.
  await abrirModulo(page, 'pagos');

  // 3. Abrir el formulario sin completar sus campos.
  await page.getByRole('button', { name: 'Registrar Pagos' }).click();
  const modal = page.locator('#modalRegistrarPago');
  const form = page.locator('#formRegistrarPago');

  // 4. Comprobar que los campos obligatorios impiden el envío.
  await expect(modal).toBeVisible();
  expect(
    await form.evaluate((element) => (element as HTMLFormElement).checkValidity())
  ).toBe(false);
});
