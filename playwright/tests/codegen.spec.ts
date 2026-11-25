import { test, expect } from '@playwright/test';

test('registrar compra codegen', async ({ page }) => {
await page.goto('http://localhost:5000/admin?ruta=login');
await page.getByRole('textbox', { name: 'Cédula' }).click();
await page.getByRole('textbox', { name: 'Cédula' }).fill('4723317');
await page.getByRole('textbox', { name: 'Password' }).click();
await page.getByRole('textbox', { name: 'Password' }).fill('admin123');
await page.getByRole('checkbox', { name: ' No soy un robot Verificació' }).check();
await page.getByRole('textbox', { name: 'Código CAPTCHA de seis' }).fill('AB12Cd');
await page.getByRole('button', { name: ' Verificar código' }).click();
await page.getByRole('button', { name: 'Acceso' }).click();
await page.getByRole('link', { name: ' Compras' }).click();
await page.getByRole('button', { name: 'Registrar Compra' }).click();
await page.locator('#cantidad').click();
await page.locator('#cantidad').fill('2');
await page.getByRole('button', { name: '+' }).click();
await page.getByRole('button', { name: 'Guardar' }).click();

});