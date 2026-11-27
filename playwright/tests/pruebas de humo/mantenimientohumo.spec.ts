import { expect, test } from '@playwright/test';

test('humo del módulo de mantenimiento', async ({ page }) => {
  // CP-MAN-18: Verifica que las opciones de mantenimiento estén disponibles.

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

  const menuConfiguracion = page.locator(
    '#menuConfiguracion > a.sidebar-link'
  );
  await expect(menuConfiguracion).toBeVisible();
  await menuConfiguracion.click();

  const enlaceMantenimiento = page.locator(
    '#menuConfiguracion .submenu a.submenu-link[href="/admin?ruta=mantenimiento"]'
  );
  await expect(enlaceMantenimiento).toBeVisible();
  await expect(enlaceMantenimiento).toBeEnabled();
  await enlaceMantenimiento.click();
  await expect(page.getByRole('heading', { name: 'Mantenimiento' })).toBeVisible();
  await expect(page.locator('#table1')).toBeVisible();
  await expect(page.locator('#table1 thead')).toContainText('Nombre');
  await expect(page.locator('#table1 thead')).toContainText('Base de datos');
  await expect(page.locator('#table1 thead')).toContainText('Tamaño');
  await expect(page.locator('#table1 thead')).toContainText('Fecha');
  await expect(page.locator('#btnCrearBackup')).toBeVisible();
  await expect(
    page.locator('#formRestaurarBackup input[name="backup_file"]')
  ).toHaveAttribute('accept', '.sql');
  await expect(
    page.locator('#formRestaurarBackup input[name="backup_file"]')
  ).toHaveAttribute('required', '');

  console.log('Prueba de humo del módulo Mantenimiento finalizada correctamente');
});
