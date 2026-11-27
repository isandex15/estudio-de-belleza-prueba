import { expect, test } from '@playwright/test';

test('humo del módulo de tipos de pago', async ({ page }) => {
  // CP-TP-20: Verifica el acceso al módulo y la apertura del formulario de tipo de pago.

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

  const enlaceTipoPago = page.locator(
    '#menuConfiguracion .submenu a.submenu-link[href="/admin?ruta=tipopagos"]'
  );
  await expect(enlaceTipoPago).toBeVisible();
  await expect(enlaceTipoPago).toBeEnabled();
  await enlaceTipoPago.click();
  await expect(page.getByRole('heading', { name: 'Tipos de Pagos' })).toBeVisible();
  await expect(page.locator('#table1')).toBeVisible();
  await expect(page.locator('#table1 thead')).toContainText('Codigo');
  await expect(page.locator('#table1 thead')).toContainText('Nombre');
  await expect(page.locator('#table1 thead')).toContainText('Status');

  await page.getByRole('button', { name: 'Registrar Tipo de Pago' }).click();
  const modalRegistro = page.locator('#modalRegistrarTipoPago');
  await expect(modalRegistro).toBeVisible();

  const nombre = page.locator('#nombre_tipo_pago');
  await expect(nombre).toBeVisible();
  await expect(nombre).toHaveAttribute('required', '');
  await expect(nombre).toHaveAttribute('maxlength', '15');

  await modalRegistro
    .locator('.modal-footer')
    .getByRole('button', { name: 'Cerrar' })
    .click();
  await expect(modalRegistro).toBeHidden();

  console.log('Prueba de humo del módulo Tipo de Pago finalizada correctamente');
});
