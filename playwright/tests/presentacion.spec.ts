// @ts-check
import { test, expect } from '@playwright/test';

test('registrar presentación', async ({ page }) => {

    // Iniciar sesión
    await page.goto('http://localhost:5000/admin?ruta=login');

    await page.getByRole('textbox', { name: 'Cédula' }).fill('4723317');
    await page.locator('#login-password').fill('admin123');
    console.log('Campo de contraseña llenado');

    await page.locator('#pow-check').click();
    console.log('Checkbox CAPTCHA clickeado');

    await expect(page.locator('#pow-image')).toBeVisible();

    await page.locator('#pow-answer').fill('AB12CD');
    await page.locator('#pow-verify').click();
    console.log('Botón de verificación CAPTCHA clickeado');

    await page.locator('#loginButton').click();
    console.log('Botón de acceso clickeado');

    console.log('URL actual:', page.url());

    await expect(page.locator('.sidebar-menu')).toBeVisible({
        timeout: 15000
    });

    console.log('Inicio de sesión confirmado: menú visible');

    // Acceder a Unidad de Medida
    const menuUnidadMedida = page.locator('.sidebar-menu a.sidebar-link')
        .filter({ hasText: 'Unidad de Medida' });

    await expect(menuUnidadMedida).toBeVisible();
    await expect(menuUnidadMedida).toBeEnabled();

    await menuUnidadMedida.click();
    console.log('Menú Unidad de Medida desplegado');

    // Acceder a Presentación
    const enlacePresentacion = page.locator(
        '.sidebar-menu .submenu a.submenu-link'
    ).filter({ hasText: 'Presentación' });

    await expect(enlacePresentacion).toBeVisible();
    await expect(enlacePresentacion).toBeEnabled();

    await enlacePresentacion.click();
    console.log('Acceso al módulo Presentación');

    // Registrar presentación
    await page.locator(
        'button[data-bs-target="#modalRegistrarPresentacion"]'
    ).click();

    console.log('Modal de registro de presentación abierto');

    await expect(page.locator('#modalRegistrarPresentacion')).toBeVisible();

    await page.locator('#presentacion_reg').fill('Ampolla');
    console.log('Campo de presentación llenado con Ampolla');

    await page.locator(
        '#formRegistrarPresentacion button[type="submit"]'
    ).click();

    console.log('Botón Guardar clickeado');

    // Verificar resultado
    await expect(page.locator('.swal2-popup')).toBeVisible({
        timeout: 10000
    });

    await expect(page.locator('.swal2-popup'))
        .toContainText('Registrado con éxito');

    console.log('Mensaje de registro exitoso mostrado');

    await page.locator('.swal2-confirm').click();
    console.log('Alerta de confirmación cerrada');

    await expect(
        page.locator('#modalRegistrarPresentacion')
    ).toBeHidden();

  
    console.log('Prueba CP-PRE-01 finalizada');
});

test('presentacion', async ({ page }) => {

    await page.goto('http://localhost:5000/admin?ruta=login');

    await page.getByRole('textbox', { name: 'Cédula' }).fill('4723317');
    await page.locator('#login-password').fill('admin123');

    await page.locator('#pow-check').click();
    await page.locator('#pow-answer').fill('AB12CD');
    await page.locator('#pow-verify').click();
    await page.locator('#loginButton').click();

    await expect(page.locator('.sidebar-menu')).toBeVisible({ timeout: 15000 });

    // Acceder a Presentación.
    await page.locator('.sidebar-menu a.sidebar-link')
        .filter({ hasText: 'Unidad de Medida' }).click();

    await page.locator('.sidebar-menu .submenu a.submenu-link')
        .filter({ hasText: 'Presentación' }).click();

    // Buscar presentación.
    const filaPresentacion = page.locator('#table1 tbody tr')
        .filter({ hasText: 'ampolla' });

    await expect(filaPresentacion).toBeVisible();

    // Abrir formulario de edición.
    await filaPresentacion.locator('.btn-editar').click();

    const modal = page.locator('#modalEditarPresentacion');

    await expect(modal).toBeVisible();

    // Comprobar el campo de estado sin modificarlo.
    await expect(modal.locator('#status_presentacion_edit')).toBeVisible();

    // Comprobar el botón de edición sin pulsarlo.
    const botonEditar = modal.locator('#formEditarPresentacion button[type="submit"]');

    await expect(botonEditar).toBeVisible();
    await expect(botonEditar).toBeEnabled();

    console.log('Formulario de presentación verificado sin guardar');

    // Cerrar el modal sin modificar datos.
const botonCerrar = modal.getByRole('button', { name: 'Cerrar' });

await expect(botonCerrar).toBeVisible();
await botonCerrar.click();

// Esperar a que Bootstrap termine de cerrar el modal.
await expect(modal).toBeHidden({ timeout: 10000 });

console.log('Modal de presentación cerrado correctamente');

 

});