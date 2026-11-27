import { expect, test } from '@playwright/test';

import { abrirModulo, iniciarSesion } from './auth';

test('mostrar formulario de registro de pago personal', async ({ page }) => {
  // CP-PP-20: Muestra el formulario de registro de pago personal.

  // 1. Iniciar sesión.
  await iniciarSesion(page);

  // 2. Acceder al módulo Pagos de Personal.
  await abrirModulo(page, 'pagospersonal');

  // 3. Verificar la tabla y abrir el formulario.
  await expect(page.locator('#pagospersonalTable')).toBeVisible();
  await page.getByRole('button', { name: 'Registrar Pago Personal' }).click();

  const modal = page.locator('#modalRegistrarPagoPersonal');
  await expect(modal).toBeVisible();
  await expect(page.locator('#cod_servicio_personal')).toBeVisible();
  await expect(page.locator('#fecha_pago_personal')).toHaveValue(
    /^\d{4}-\d{2}-\d{2}$/
  );
  await expect(page.locator('#porcentaje_personal')).toBeVisible();
  await expect(page.locator('#referencia_pago_personal')).toBeVisible();
});

test('rechazar porcentaje menor al mínimo permitido', async ({ page }) => {
  // CP-PP-21: Rechaza un porcentaje menor al mínimo permitido.

  // 1. Iniciar sesión.
  await iniciarSesion(page);

  // 2. Acceder al módulo Pagos de Personal.
  await abrirModulo(page, 'pagospersonal');

  // 3. Ingresar un porcentaje inferior al mínimo.
  await page.getByRole('button', { name: 'Registrar Pago Personal' }).click();
  const porcentaje = page.locator('#porcentaje_personal');

  await porcentaje.fill('0');

  // 4. Comprobar que el valor no es válido.
  expect(
    await porcentaje.evaluate(
      (element) => (element as HTMLInputElement).validity.rangeUnderflow
    )
  ).toBe(true);
});
