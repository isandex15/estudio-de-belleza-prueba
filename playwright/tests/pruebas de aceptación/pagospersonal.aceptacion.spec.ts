import { expect, test } from '@playwright/test';

import { abrirModulo, iniciarSesion } from '../auth';

test('PagosPersonal: consultar registros y validar porcentaje mínimo', async ({
  page,
}) => {
  // CP-PP-23: Consulta pagos de personal y valida el porcentaje mínimo.

  // 1. Iniciar sesión.
  await iniciarSesion(page);

  // 2. Acceder al módulo PagosPersonal.
  await abrirModulo(page, 'pagospersonal');

  // 3. Abrir el formulario de pago personal.
  await expect(page.locator('#pagospersonalTable')).toBeVisible();
  await page.getByRole('button', { name: 'Registrar Pago Personal' }).click();

  const modal = page.locator('#modalRegistrarPagoPersonal');

  // 4. Verificar campos y validar el porcentaje mínimo.
  await expect(modal).toBeVisible();
  await expect(page.locator('#cod_servicio_personal')).toBeVisible();
  await expect(page.locator('#fecha_pago_personal')).toHaveValue(
    /^\d{4}-\d{2}-\d{2}$/
  );
  await expect(page.locator('#referencia_pago_personal')).toBeVisible();

  const porcentaje = page.locator('#porcentaje_personal');
  await porcentaje.fill('0');
  expect(
    await porcentaje.evaluate(
      (element) => (element as HTMLInputElement).validity.rangeUnderflow
    )
  ).toBe(true);
});
