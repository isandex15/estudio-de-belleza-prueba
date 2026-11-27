
import { test, expect } from '@playwright/test';


test('registrar rol Gerente', async ({ page }) => {
    test.setTimeout(45000);

    await page.goto('http://localhost:5000/admin?ruta=login');

    await page.getByRole('textbox', { name: 'Cédula' }).fill('4723317');
    await page.locator('#login-password').fill('admin123');

    await page.locator('#pow-check').click();
    await page.locator('#pow-answer').fill('AB12CD');
    await page.locator('#pow-verify').click();
    await page.locator('#loginButton').click();

    await expect(page.locator('.sidebar-menu')).toBeVisible({ timeout: 15000 });

    // Acceder a Configuración
    await page.locator('#menuConfiguracion > a.sidebar-link').click();

    await page.locator('#menuConfiguracion .submenu a.submenu-link')
        .filter({ hasText: 'Rol' }).click();

    // Registrar rol
    await page.locator('button[data-bs-target="#Rol"]').click();

    await expect(page.locator('#Rol')).toBeVisible();

    await page.locator('#nombre_rol').fill('Gerente');

    await page.locator('#formRol button[type="submit"]').click();

    // Verificar registro
    await expect(page.locator('.swal2-popup')).toBeVisible({ timeout: 10000 });
    await page.locator('.swal2-confirm').click();

    await expect(page.locator('#Rol')).toBeHidden();

    // Verificar actualización de la tabla
    await expect(
        page.locator('#table1 tbody tr').filter({ hasText: 'Gerente' })
    ).toBeVisible({ timeout: 20000 });

    console.log('Rol registrado: Gerente');
});



test('editar rol Gerente cambiar estado a inactivo', async ({ page }) => {
    test.setTimeout(45000);

    await page.goto('http://localhost:5000/admin?ruta=login');

    await page.getByRole('textbox', { name: 'Cédula' }).fill('4723317');
    await page.locator('#login-password').fill('admin123');

    await page.locator('#pow-check').click();
    await page.locator('#pow-answer').fill('AB12CD');
    await page.locator('#pow-verify').click();
    await page.locator('#loginButton').click();

    await expect(page.locator('.sidebar-menu')).toBeVisible({ timeout: 15000 });

    // Acceder a Configuración
    await page.locator('#menuConfiguracion > a.sidebar-link').click();

    await page.locator('#menuConfiguracion .submenu a.submenu-link')
        .filter({ hasText: 'Rol' }).click();

    // Editar rol
    const filaRol = page.locator('#table1 tbody tr')
        .filter({ hasText: 'Gerente' });

    await expect(filaRol).toBeVisible();

    await filaRol.locator('.btn-editar').click();

    await expect(page.locator('#editModal')).toBeVisible();

    await page.locator('#edit_estado').selectOption('0');

    await page.locator('#formEditRol button[type="submit"]').click();

    // Verificar actualización
    await expect(page.locator('.swal2-popup')).toBeVisible({ timeout: 10000 });
    await page.locator('.swal2-confirm').click();

    await expect(page.locator('#editModal')).toBeHidden();

    await expect(
        page.locator('#table1 tbody tr')
            .filter({ hasText: 'Gerente' })
            .locator('td').nth(2)
    ).toHaveText('Inactivo', { timeout: 20000 });

    console.log('Rol editado: estado cambiado a Inactivo');
});
