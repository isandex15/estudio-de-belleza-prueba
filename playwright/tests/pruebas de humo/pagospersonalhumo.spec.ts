import { expect, test } from '@playwright/test';

test('humo del módulo de pagos de personal', async ({ page }) => {
  // CP-PP-22: Verifica el acceso al módulo y la apertura del formulario de pago personal.

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

  const enlacePagosPersonal = page.locator(
    '.sidebar-menu a.sidebar-link[href="/admin?ruta=pagospersonal"]'
  );
  await expect(enlacePagosPersonal).toBeVisible();
  await expect(enlacePagosPersonal).toBeEnabled();
  await enlacePagosPersonal.click();
  await expect(page.getByRole('heading', { name: 'Pagos Personal' })).toBeVisible();
  await expect(page.locator('#pagospersonalTable')).toBeVisible();
  await expect(page.locator('#pagospersonalTable thead')).toContainText('Servicio');
  await expect(page.locator('#pagospersonalTable thead')).toContainText('Especialista');
  await expect(page.locator('#pagospersonalTable thead')).toContainText('Monto a Pagar');

  await page.getByRole('button', { name: 'Registrar Pago Personal' }).click();
  const modalRegistro = page.locator('#modalRegistrarPagoPersonal');
  await expect(modalRegistro).toBeVisible();

  const servicio = page.locator('#cod_servicio_personal');
  const fechaPago = page.locator('#fecha_pago_personal');
  const porcentaje = page.locator('#porcentaje_personal');
  const referencia = page.locator('#referencia_pago_personal');
  const comprobante = page.locator('#comprobante_pago_personal');
  await expect(servicio).toBeVisible();
  await expect(fechaPago).toHaveValue(/^\d{4}-\d{2}-\d{2}$/);
  await expect(porcentaje).toBeVisible();
  await expect(referencia).toBeVisible();
  await expect(comprobante).toBeVisible();
  await expect(servicio).toHaveAttribute('required', '');
  await expect(fechaPago).toHaveAttribute('required', '');
  await expect(porcentaje).toHaveAttribute('required', '');
  await expect(page.locator('#cod_tipo_pago_personal')).toHaveAttribute(
    'required',
    ''
  );
  await expect(page.locator('#banco_pago_personal')).toHaveAttribute(
    'required',
    ''
  );
  await expect(page.locator('#tasa_pago_personal')).toHaveAttribute(
    'required',
    ''
  );
  await expect(referencia).toHaveAttribute('required', '');
  await expect(comprobante).toHaveAttribute('required', '');

  await modalRegistro
    .locator('.modal-footer')
    .getByRole('button', { name: 'Cerrar' })
    .click();
  await expect(modalRegistro).toBeHidden();

  console.log('Prueba de humo del módulo Pagos de Personal finalizada correctamente');
});
