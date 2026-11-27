import { expect, test } from '@playwright/test';

import { abrirModulo, iniciarSesion } from '../pruebas de interfaz/auth';

test('Pagos: consultar registros y validar el formulario sin crear transacciones', async ({
  page,
}) => {
  // CP-PAG-15: Consulta pagos y valida el formulario sin registrar una transacción.

  // 1. Iniciar sesión.
  await iniciarSesion(page);

  // 2. Acceder al módulo Pagos.
  await abrirModulo(page, 'pagos');

  // 3. Abrir el formulario de registro.
  await expect(page.locator('#table1')).toBeVisible();
  await page.getByRole('button', { name: 'Registrar Pagos' }).click();

  const modal = page.locator('#modalRegistrarPago');
  const form = page.locator('#formRegistrarPago');

  // 4. Verificar los campos y que no permita enviar el formulario vacío.
  await expect(modal).toBeVisible();
  await expect(page.locator('#cedula_cliente')).toBeVisible();
  await expect(page.locator('#fecha_pago')).toHaveValue(/^\d{4}-\d{2}-\d{2}$/);
  await expect(page.locator('#monto')).toBeVisible();
  await expect(page.locator('#comprobante_pago')).toBeVisible();
  expect(
    await form.evaluate((element) => (element as HTMLFormElement).checkValidity())
  ).toBe(false);
});
