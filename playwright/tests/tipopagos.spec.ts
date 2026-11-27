import { expect, test } from '@playwright/test';

import { abrirModulo, iniciarSesion } from './auth';

test('mostrar formulario de registro de tipo de pago', async ({ page }) => {
  // CP-TP-18: Muestra el formulario de registro de tipo de pago.

  // 1. Iniciar sesión.
  await iniciarSesion(page);

  // 2. Acceder al módulo Tipo de Pago.
  await abrirModulo(page, 'tipopagos');

  // 3. Verificar la tabla y abrir el formulario.
  await expect(page.locator('#table1')).toBeVisible();
  await page.getByRole('button', { name: 'Registrar Tipo de Pago' }).click();

  await expect(page.locator('#modalRegistrarTipoPago')).toBeVisible();
  await expect(page.locator('#nombre_tipo_pago')).toBeVisible();
});

test('validar caracteres no permitidos en el tipo de pago', async ({ page }) => {
  // CP-TP-19: Marca caracteres no permitidos en el tipo de pago.

  // 1. Iniciar sesión.
  await iniciarSesion(page);

  // 2. Acceder al módulo Tipo de Pago.
  await abrirModulo(page, 'tipopagos');

  // 3. Ingresar un tipo de pago con caracteres no permitidos.
  await page.getByRole('button', { name: 'Registrar Tipo de Pago' }).click();
  const nombre = page.locator('#nombre_tipo_pago');

  await nombre.fill('UITipoPagoXY123');

  // 4. Comprobar la validación del campo.
  await expect(nombre).toHaveValue('UITipoPagoXY');
  await expect(nombre).toHaveClass(/is-invalid/);
});
