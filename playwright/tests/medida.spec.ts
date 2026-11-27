// @ts-check
import { test, expect } from '@playwright/test';



test('registrar medida Kilogramos', async ({ page }) => {
    test.setTimeout(45000);

    await page.goto('http://localhost:5000/admin?ruta=login');

    await page.getByRole('textbox', { name: 'Cédula' }).fill('4723317');
    await page.locator('#login-password').fill('admin123');

    await page.locator('#pow-check').click();
    await page.locator('#pow-answer').fill('AB12CD');
    await page.locator('#pow-verify').click();
    await page.locator('#loginButton').click();

    await expect(page.locator('.sidebar-menu')).toBeVisible({ timeout: 15000 });

    // Acceder a Unidad de Medida
    await page.locator('.sidebar-menu a.sidebar-link')
        .filter({ hasText: 'Unidad de Medida' }).click();

    await page.locator('.sidebar-menu .submenu a.submenu-link')
        .filter({ hasText: 'Medida' }).click();

    // Registrar medida
    await page.locator('button[data-bs-target="#modalRegistrarMedida"]').click();

    await expect(page.locator('#modalRegistrarMedida')).toBeVisible();

    await page.locator('#medida_reg').fill('Kilogramos');

    await page.locator('#formRegistrarMedida button[type="submit"]').click();

    // Verificar registro
    await expect(page.locator('.swal2-popup')).toBeVisible({ timeout: 10000 });
    await page.locator('.swal2-confirm').click();

    await expect(page.locator('#modalRegistrarMedida')).toBeHidden();

    // Esperar la actualización de la tabla
    await expect(
        page.locator('#table1 tbody tr').filter({ hasText: 'Kilogramos' })
    ).toBeVisible({ timeout: 20000 });

    console.log('Medida registrada: Kilogramos');
});


test('medida', async ({ page }) => {
    test.setTimeout(45000);

    await page.goto('http://localhost:5000/admin?ruta=login');

    await page.getByRole('textbox', { name: 'Cédula' }).fill('4723317');
    await page.locator('#login-password').fill('admin123');

    await page.locator('#pow-check').click();
    await page.locator('#pow-answer').fill('AB12CD');
    await page.locator('#pow-verify').click();
    await page.locator('#loginButton').click();

    await expect(page.locator('.sidebar-menu')).toBeVisible({ timeout: 15000 });

    // Acceder a Unidad de Medida
    await page.locator('.sidebar-menu a.sidebar-link')
        .filter({ hasText: 'Unidad de Medida' }).click();

    await page.locator('.sidebar-menu .submenu a.submenu-link')
        .filter({ hasText: 'Medida' }).click();

    // Editar medida
    const filaMedida = page.locator('#table1 tbody tr')
        .filter({ hasText: 'kilogramo' });

    await expect(filaMedida).toBeVisible();

    await filaMedida.locator('.btn-editar').click();

    await expect(page.locator('#modalEditarMedida')).toBeVisible();

    await page.locator('#status_edit').selectOption('0');

    await page.locator('#formEditarMedida button[type="submit"]').click();

    // Verificar actualización
    await expect(page.locator('.swal2-popup')).toBeVisible({ timeout: 10000 });
    await page.locator('.swal2-confirm').click();

    await expect(page.locator('#modalEditarMedida')).toBeHidden();

    await expect(
        page.locator('#table1 tbody tr')
            .filter({ hasText: 'kilogramo' })
            .locator('td').nth(2)
    ).toHaveText('Inactivo', { timeout: 20000 });

    console.log('Medida actualizada: kilogramo, estado: Inactivo');
});
