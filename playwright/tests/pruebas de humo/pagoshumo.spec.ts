import { expect, test } from '@playwright/test';

test('humo del módulo de pagos', async ({ page }) => {
  // CP-PAG-14: Verifica el acceso al módulo y la apertura del formulario de pago.

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

  const enlacePagos = page.locator(
    '.sidebar-menu a.sidebar-link[href="/admin?ruta=pagos"]'
  );
  await expect(enlacePagos).toBeVisible();
  await expect(enlacePagos).toBeEnabled();
  await enlacePagos.click();
  await expect(page.getByRole('heading', { name: 'Pagos' })).toBeVisible();
  await expect(page.locator('#table1')).toBeVisible();
  await expect(page.locator('#table1 thead')).toContainText('Cliente');
  await expect(page.locator('#table1 thead')).toContainText('Fecha Pago');
  await expect(page.locator('#table1 thead')).toContainText('Monto');
  await expect(page.locator('#table1 thead')).toContainText('Comprobante');

  await page.getByRole('button', { name: 'Registrar Pagos' }).click();
  const modalRegistro = page.locator('#modalRegistrarPago');
  await expect(modalRegistro).toBeVisible();

  const cliente = page.locator('#cedula_cliente');
  const fechaPago = page.locator('#fecha_pago');
  const monto = page.locator('#monto');
  const comprobante = page.locator('#comprobante_pago');
  await expect(cliente).toBeVisible();
  await expect(fechaPago).toHaveValue(/^\d{4}-\d{2}-\d{2}$/);
  await expect(monto).toBeVisible();
  await expect(comprobante).toBeVisible();
  await expect(cliente).toHaveAttribute('required', '');
  await expect(fechaPago).toHaveAttribute('required', '');
  await expect(monto).toHaveAttribute('required', '');
  await expect(comprobante).toHaveAttribute('required', '');
  await expect(page.locator('#cod_servicio')).toHaveAttribute('required', '');
  await expect(page.locator('#cod_moneda')).toHaveAttribute('required', '');
  await expect(page.locator('#cod_tipo_pago')).toHaveAttribute('required', '');

  await modalRegistro
    .locator('.modal-footer')
    .getByRole('button', { name: 'Cerrar' })
    .click();
  await expect(modalRegistro).toBeHidden();

  console.log('Prueba de humo del módulo Pagos finalizada correctamente');
});
