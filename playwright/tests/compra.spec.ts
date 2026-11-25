// @ts-check
import { test, expect } from '@playwright/test';


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



test('registrar compra mobile', async ({ page }) => {
await page.goto('http://localhost:5000/admin?ruta=login');
await page.getByRole('textbox', { name: 'Cédula' }).click();
await page.getByRole('textbox', { name: 'Cédula' }).fill('4723317');
await page.getByRole('textbox', { name: 'Password' }).click();
await page.getByRole('textbox', { name: 'Password' }).fill('admin123');
await page.getByRole('checkbox', { name: ' No soy un robot Verificació' }).check();
await page.getByRole('textbox', { name: 'Código CAPTCHA de seis' }).fill('AB12Cd');
await page.getByRole('button', { name: ' Verificar código' }).click();
await page.getByRole('button', { name: 'Acceso' }).click();
await page.locator('#burger-btn').click();
await page.getByRole('link', { name: ' Compras' }).click();
await page.getByRole('button', { name: 'Registrar Compra' }).click();
await page.locator('#cantidad').click();
await page.locator('#cantidad').fill('2');
await page.getByRole('button', { name: '+' }).click();
await page.getByRole('button', { name: 'Guardar' }).click();
});