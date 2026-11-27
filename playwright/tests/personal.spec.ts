import { expect, test } from '@playwright/test';

import { abrirModulo, iniciarSesion } from './auth';

test('mostrar formulario de registro de personal', async ({ page }) => {
  // CP-PER-28: Muestra el formulario de registro de personal.

  // 1. Iniciar sesión.
  await iniciarSesion(page);

  // 2. Acceder al módulo Personal.
  await abrirModulo(page, 'personal');

  // 3. Verificar la tabla y abrir el formulario.
  await expect(page.locator('#table1')).toBeVisible();
  await page.getByRole('button', { name: 'Registrar Personal' }).click();

  await expect(page.locator('#modalRegistrarPersonal')).toBeVisible();
  await expect(page.locator('#cedula_reg')).toBeVisible();
  await expect(page.locator('#nombre_usuario_reg')).toBeVisible();
  await expect(page.locator('#correo_reg')).toBeVisible();
});

test('rechazar correo con dominio no permitido', async ({ page }) => {
  // CP-PER-29: Rechaza un correo con dominio no permitido.

  // 1. Iniciar sesión.
  await iniciarSesion(page);

  // 2. Acceder al módulo Personal.
  await abrirModulo(page, 'personal');

  // 3. Ingresar un correo con dominio no permitido.
  await page.getByRole('button', { name: 'Registrar Personal' }).click();
  const correo = page.locator('#correo_reg');

  await correo.fill('persona@example.org');

  // 4. Comprobar el mensaje de validación.
  await expect(correo).toHaveClass(/is-invalid/);
  await expect(correo.locator('xpath=following-sibling::div[1]')).toContainText(
    'Ingrese un correo válido'
  );
});
