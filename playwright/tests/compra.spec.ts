// @ts-check
import { test, expect, type Page } from '@playwright/test';

async function abrirTablaCompras(page: Page) {
  await page.goto('http://localhost:5000/admin?ruta=login');
  await page.getByRole('textbox', { name: 'Cédula' }).fill('4723317');
  await page.getByRole('textbox', { name: 'Password' }).fill('admin123');
  await page.locator('#pow-open').click();
  await page.locator('#pow-answer').fill('AB12CD');
  await page.locator('#pow-verify').click();
  await page.locator('#loginButton').click();

  await expect(page.locator('.sidebar-menu')).toBeVisible();
  await page.locator("ul[class='menu']").getByText('Compras').click();
  await expect(page.getByRole('heading', { name: 'Compras' })).toBeVisible();
}





test('registrar compra', async ({ page }) => {
  await page.goto('http://localhost:5000/admin?ruta=login')

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
  await expect(page.locator('div[class=\'sidebar-menu\']')).toBeVisible();
  console.log('sidebar menu visible');

  await page.locator("ul[class='menu']").getByText("Compras").click();
  await page.locator("button[class='btn btn-primary rounded-pill']").click();
  await page.locator('input[id=\'cantidad\']').fill('2');
  await page.locator("button[id='agregarProducto']").click();
  await page.getByRole('button', { name: 'Guardar' }).click();
  console.log("Compra registrada Correctamente")
  

});

test('consultar detalle compra', async ({ page }) => {
  await page.goto('http://localhost:5000/admin?ruta=login')

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
  await expect(page.locator('div[class=\'sidebar-menu\']')).toBeVisible();
  console.log('sidebar menu visible');
  await page.locator("ul[class='menu']").getByText("Compras").click()
  await page.getByTitle('Ver factura').first().click();
  await page.evaluate(() => {
  Object.defineProperty(window, 'print', {
    configurable: true,
    value: () => {}
  });
});

await page.locator('#btnDescargarFactura').click();
  console.log("Detalle de compra mostrado correctamente")
  
});

test('cancelar compra', async ({ page }) => {
  await page.goto('http://localhost:5000/admin?ruta=login')

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
  await expect(page.locator('div[class=\'sidebar-menu\']')).toBeVisible();
  console.log('sidebar menu visible');
  await page.locator("ul[class='menu']").getByText("Compras").click()
  await page.getByRole('button').nth(4).click();
  await page.getByRole('button', { name: 'Sí' }).click();
  await page.locator('#formEliminarCompra').getByText('No').click()
  
  console.log("modal y boton de compra funcionan correctamente")
  
});

test('mostrar la tabla de compras', async ({ page }) => {
  await abrirTablaCompras(page);

  const tablaCompras = page.locator('#table1');
  await expect(tablaCompras).toBeVisible();
  await expect(tablaCompras.locator('thead')).toContainText('Código');
  await expect(tablaCompras.locator('thead')).toContainText('Proveedor');
  await expect(tablaCompras.locator('thead')).toContainText('Total');
});

test('buscar una compra en la tabla', async ({ page }) => {
  await abrirTablaCompras(page);

  const tablaCompras = page.locator('#table1');
  await expect(tablaCompras).toBeVisible();

  const botonDetalle = tablaCompras.locator('.btnDetalleCompra').first();
  await expect(botonDetalle).toBeVisible();
  const codigoCompra = await botonDetalle.getAttribute('data-id');
  if (!codigoCompra) {
    throw new Error('La fila de compra no tiene un código para buscar.');
  }

  const buscador = page.locator('#table1_filter input');
  await expect(buscador).toBeVisible();
  await buscador.fill(codigoCompra);

  await expect(tablaCompras.locator('tbody tr')).toHaveCount(1);
  await expect(tablaCompras.locator('tbody tr')).toContainText(codigoCompra);
});

