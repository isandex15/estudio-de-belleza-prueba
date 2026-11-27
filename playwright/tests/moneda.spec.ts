import { expect, test } from '@playwright/test';

import { abrirModulo, iniciarSesion } from './auth';

test('mostrar formulario de registro de moneda', async ({ page }) => {
  // CP-MON-20: Muestra el formulario de registro de moneda.

  // 1. Iniciar sesión.
  await iniciarSesion(page);

  // 2. Acceder al módulo Moneda.
  await abrirModulo(page, 'moneda');

  // 3. Verificar la tabla y abrir el formulario.
  await expect(page.locator('#table1')).toBeVisible();
  await page.getByRole('button', { name: 'Registrar Moneda' }).click();

  await expect(page.locator('#modalRegistrarMoneda')).toBeVisible();
  await expect(page.locator('#nombre_moneda')).toBeVisible();
});

test('validar caracteres no permitidos en el nombre de moneda', async ({ page }) => {
  // CP-MON-21: Marca caracteres no permitidos en el nombre de moneda.

  // 1. Iniciar sesión.
  await iniciarSesion(page);

  // 2. Acceder al módulo Moneda.
  await abrirModulo(page, 'moneda');

  // 3. Ingresar un nombre con caracteres no permitidos.
  await page.getByRole('button', { name: 'Registrar Moneda' }).click();
  const nombre = page.locator('#nombre_moneda');

  await nombre.fill('MonedaUI123');

  // 4. Comprobar la validación del campo.
  await expect(nombre).toHaveValue('MonedaUI');
  await expect(nombre).toHaveClass(/is-invalid/);
});
