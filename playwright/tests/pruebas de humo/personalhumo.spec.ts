import { expect, test } from '@playwright/test';

test('humo del módulo de personal', async ({ page }) => {
  // CP-PER-30: Verifica el acceso al módulo y la apertura del formulario de personal.

  await page.goto('http://localhost:5000/admin?ruta=login');
  await page.getByRole('textbox', { name: 'Cédula' }).click();
  await page
    .getByRole('textbox', { name: 'Cédula' })
    .fill(process.env.CEDULA!);
  await page.locator('#login-password').fill(process.env.PASSWORD!);
  console.log('Campo de contraseña llenado');

  await page.locator('#pow-check').click();
  await expect(page.locator('#pow-image')).toBeVisible();
  await page.locator('#pow-answer').fill('AB12CD');
  await page.locator('#pow-verify').click();
  console.log('captcha verificado');

  await page.locator('#loginButton').click();
  console.log('inicio de sesión realizado');
  await expect(page.locator('.sidebar-menu')).toBeVisible({
    timeout: 15000,
  });

  const enlacePersonal = page.locator(
    '.sidebar-menu a.sidebar-link[href="/admin?ruta=personal"]'
  );
  await expect(enlacePersonal).toBeVisible();
  await expect(enlacePersonal).toBeEnabled();
  await enlacePersonal.click();
  await expect(page.getByRole('heading', { name: 'Personal' })).toBeVisible();
  await expect(page.locator('#table1')).toBeVisible();
  await expect(page.locator('#table1 thead')).toContainText('Cédula');
  await expect(page.locator('#table1 thead')).toContainText('Nombre');
  await expect(page.locator('#table1 thead')).toContainText('Teléfono');
  await expect(page.locator('#table1 thead')).toContainText('Correo');

  await page.getByRole('button', { name: 'Registrar Personal' }).click();
  const modalRegistro = page.locator('#modalRegistrarPersonal');
  await expect(modalRegistro).toBeVisible();

  const cedula = page.locator('#cedula_reg');
  const nombre = page.locator('#nombre_usuario_reg');
  const apellido = page.locator('#apellido_usuario_reg');
  const telefono = page.locator('#telefono_reg');
  const direccion = page.locator('#direccion_reg');
  const correo = page.locator('#correo_reg');
  await expect(cedula).toBeVisible();
  await expect(nombre).toBeVisible();
  await expect(apellido).toBeVisible();
  await expect(telefono).toBeVisible();
  await expect(direccion).toBeVisible();
  await expect(correo).toBeVisible();
  await expect(cedula).toHaveAttribute('required', '');
  await expect(nombre).toHaveAttribute('required', '');
  await expect(apellido).toHaveAttribute('required', '');
  await expect(telefono).toHaveAttribute('required', '');
  await expect(direccion).toHaveAttribute('required', '');
  await expect(correo).toHaveAttribute('required', '');

  await modalRegistro.getByRole('button', { name: 'Cerrar' }).click();
  await expect(modalRegistro).toBeHidden();

  console.log('Prueba de humo del módulo Personal finalizada correctamente');
});
