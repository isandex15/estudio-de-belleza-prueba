import { expect, test } from '@playwright/test';

test('humo del módulo de moneda', async ({ page }) => {
  // CP-MON-22: Verifica el acceso al módulo y la apertura del formulario de moneda.

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

  const enlaceMoneda = page.locator(
    '#menuConfiguracion .submenu a.submenu-link[href="/admin?ruta=moneda"]'
  );
  await expect(enlaceMoneda).toBeVisible();
  await expect(enlaceMoneda).toBeEnabled();
  await enlaceMoneda.click();
  await expect(page.getByRole('heading', { name: 'Moneda' })).toBeVisible();
  await expect(page.locator('#table1')).toBeVisible();
  await expect(page.locator('#table1 thead')).toContainText('Codigo');
  await expect(page.locator('#table1 thead')).toContainText('Nombre');
  await expect(page.locator('#table1 thead')).toContainText('Valor Bs');
  await expect(page.locator('#table1 thead')).toContainText('Valor $');

  await page.getByRole('button', { name: 'Registrar Moneda' }).click();
  const modalRegistro = page.locator('#modalRegistrarMoneda');
  await expect(modalRegistro).toBeVisible();

  const nombre = page.locator('#nombre_moneda');
  await expect(nombre).toBeVisible();
  await expect(nombre).toHaveAttribute('required', '');
  await expect(nombre).toHaveAttribute('maxlength', '15');

  await modalRegistro
    .locator('.modal-footer')
    .getByRole('button', { name: 'Cerrar' })
    .click();
  await expect(modalRegistro).toBeHidden();

  console.log('Prueba de humo del módulo Moneda finalizada correctamente');
});
