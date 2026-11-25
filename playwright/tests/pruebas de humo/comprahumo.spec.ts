import { test, expect } from '@playwright/test';

test('humo del módulo de compras', async ({ page }) => {
    await page.goto('http://localhost:5000/admin?ruta=login');

   await page.getByRole('textbox', { name: 'Cédula' }).click();
  await page.getByRole('textbox', { name: 'Cédula' }).fill('4723317');
  await page.getByRole('textbox', { name: 'Password' }).click();
  await page.getByRole('textbox', { name: 'Password' }).fill('admin123');
  await page.locator('#pow-open').click();
  await page.locator('#pow-answer').fill('AB12CD');
  await page.locator('#pow-verify').click();
  console.log('captcha verificado');
  await page.locator('button[id=\'loginButton\']').click();
  console.log('boton sesion iniciada correctamente');

    const enlaceCompras = page.locator(
        '.sidebar-menu a.sidebar-link[href="/admin?ruta=compra"]'
    );
    await expect(enlaceCompras).toBeVisible();
    await enlaceCompras.click();

    await expect(page.getByRole('heading', { name: 'Compras' })).toBeVisible();
    await expect(page.locator('#table1')).toBeVisible();
    await expect(page.locator('#table1 thead')).toContainText('Proveedor');
    await expect(page.locator('#table1 thead')).toContainText('Total');

    await page.getByRole('button', { name: 'Registrar Compra' }).click();

    const modalRegistro = page.locator('#modalRegistrarCompra');
    await expect(modalRegistro).toBeVisible();
    await expect(page.locator('#fecha_compra')).toHaveValue(/^\d{4}-\d{2}-\d{2}$/);

    const producto = page.locator('#producto');
    await expect(producto.locator('option')).not.toHaveCount(0);

    const opcionProducto = producto.locator('option').first();
    const precio = Number(await opcionProducto.getAttribute('data-precio'));
    expect(precio).toBeGreaterThan(0);

    await producto.selectOption({ index: 0 });
    await page.locator('#cantidad').fill('2');
    await page.locator('#precio').fill(String(precio));
    await page.locator('#agregarProducto').click();

    await expect(page.locator('#detalleCompra tbody tr')).toHaveCount(1);
    await expect(page.locator('#total')).toHaveValue((precio * 2).toFixed(2));

    await modalRegistro.getByRole('button', { name: 'Cerrar' }).click();
    await expect(modalRegistro).toBeHidden();
});