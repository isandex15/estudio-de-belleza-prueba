
import { test, expect } from '@playwright/test';

test('humo completo del módulo Inicio', async ({ page }) => {

    await page.goto('http://localhost:5000/admin?ruta=login');

    await page.getByRole('textbox', { name: 'Cédula' }).click();
    await page.getByRole('textbox', { name: 'Cédula' }).fill('4723317');

    await page.getByRole('textbox', { name: 'Password' }).click();
    await page.getByRole('textbox', { name: 'Password' }).fill('admin123');

    await page.locator('#pow-open').click();
    await page.locator('#pow-answer').fill('AB12CD');
    await page.locator('#pow-verify').click();
    await page.locator('#loginButton').click();

    console.log('Inicio de sesión realizado');

    // Verificar calendario
    await expect(page.getByRole('heading', { name: 'Calendario de Reservas' })).toBeVisible();
    await expect(page.locator('#calendar')).toBeVisible();

    // Abrir modal de registro
    await page.locator('.fc-daygrid-day:not(.fc-day-past)').last().click();

    const modalRegistro = page.locator('#modalRegistrar');

    await expect(modalRegistro).toBeVisible();


    // Cerrar modal
    await modalRegistro.locator('#btnCerrarModal').click();

    await expect(modalRegistro).not.toBeVisible();

    console.log('Modal de registro cerrado correctamente');
});
