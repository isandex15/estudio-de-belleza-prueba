

import { test, expect } from '@playwright/test';


test('humo completo del módulo Presentación', async ({ page }) => {
    await page.goto('http://localhost:5000/admin?ruta=login');

    // Iniciar sesión.
    await page.getByRole('textbox', { name: 'Cédula' }).fill('4723317');
    await page.locator('#login-password').fill('admin123');

    // Verificar CAPTCHA.
    await page.locator('#pow-check').click();
    await expect(page.locator('#pow-image')).toBeVisible();
    await page.locator('#pow-answer').fill('AB12CD');
    await page.locator('#pow-verify').click();

    await page.locator('#loginButton').click();
    console.log('Inicio de sesión realizado');

    await expect(page.locator('.sidebar-menu')).toBeVisible({
        timeout: 15000
    });

    // Acceder al menú Unidad de Medida.
    const menuUnidadMedida = page.locator('.sidebar-menu .sidebar-item.has-sub').filter({
        has: page.getByText('Unidad de Medida', { exact: true })
    });

    await menuUnidadMedida.locator('> a.sidebar-link').click();

    // Acceder al módulo Presentación.
    const enlacePresentacion = page.locator(
        '.sidebar-menu a.submenu-link[href="/admin?ruta=presentacion"]'
    );

    await expect(enlacePresentacion).toBeVisible();
    await expect(enlacePresentacion).toBeEnabled();
    await enlacePresentacion.click();

    console.log('Acceso al módulo Presentación');

    // Comprobar que cargó el módulo y su tabla.
    await expect(page.locator('#table1')).toBeVisible();

    console.log('Tabla de presentaciones cargada');

    // Abrir y cerrar modal de registro.
    await page.getByRole('button', { name: 'Registrar Presentacion' }).click();

    const modalRegistro = page.locator('#modalRegistrarPresentacion');
    await expect(modalRegistro).toBeVisible();

    await expect(modalRegistro.locator('#presentacion_reg')).toBeVisible();

    await modalRegistro.getByRole('button', { name: 'Cerrar' }).click();
    await expect(modalRegistro).toBeHidden();

    console.log('Modal de registro abierto y cerrado');

    // Abrir y cerrar modal de edición del primer registro.
    const botonEditar = page.locator('#table1 .btn-editar').first();

    await expect(botonEditar).toBeVisible();
    await botonEditar.click();

    const modalEditar = page.locator('#modalEditarPresentacion');
    await expect(modalEditar).toBeVisible();

    await expect(modalEditar.locator('#presentacion_edit')).toBeVisible();
    await expect(modalEditar.locator('#status_presentacion_edit')).toBeVisible();

    await modalEditar.getByRole('button', { name: 'Cerrar' }).click();
    await expect(modalEditar).toBeHidden();

    console.log('Modal de edición abierto y cerrado');

    // Abrir y cerrar modal de eliminación del primer registro.
    const botonEliminar = page.locator('#table1 .btn-eliminar').first();

    await expect(botonEliminar).toBeVisible();
    await botonEliminar.click();

    const modalEliminar = page.locator('#modalEliminarPresentacion');
    await expect(modalEliminar).toBeVisible();

    await expect(
        modalEliminar.getByRole('heading', { name: 'Confirmar Eliminación' })
    ).toBeVisible();

    await expect(modalEliminar.locator('#nombre_presentacion')).toBeVisible();

    await expect(
        modalEliminar.getByRole('button', { name: 'No' })
    ).toBeVisible();

    await expect(
        modalEliminar.getByRole('button', { name: 'Eliminar' })
    ).toBeVisible();

    await modalEliminar.getByRole('button', { name: 'No' }).click();
    await expect(modalEliminar).toBeHidden();

    console.log('Modal de eliminación abierto y cerrado');

    console.log('Prueba de humo completa del módulo Presentación finalizada');
});



test('humo del módulo de presentación modal editar', async ({ page }) => {
    await page.goto('http://localhost:5000/admin?ruta=login');

    await page.getByRole('textbox', { name: 'Cédula' }).fill('4723317');
    await page.locator('#login-password').fill('admin123');

    await page.locator('#pow-check').click();
    await expect(page.locator('#pow-image')).toBeVisible();
    await page.locator('#pow-answer').fill('AB12CD');
    await page.locator('#pow-verify').click();

    await page.locator('#loginButton').click();
    console.log('inicio de sesión realizado');

    await expect(page.locator('.sidebar-menu')).toBeVisible({
        timeout: 15000
    });

    // Acceder al menú Unidad de Medida.
    const menuUnidadMedida = page.locator('.sidebar-menu .sidebar-item.has-sub').filter({
        has: page.getByText('Unidad de Medida', { exact: true })
    });

    await menuUnidadMedida.locator('> a.sidebar-link').click();

    // Acceder al módulo Presentación.
    const enlacePresentacion = page.locator(
        '.sidebar-menu a.submenu-link[href="/admin?ruta=presentacion"]'
    );

    await expect(enlacePresentacion).toBeVisible();
    await expect(enlacePresentacion).toBeEnabled();
    await enlacePresentacion.click();

    await expect(page.locator('#table1')).toBeVisible();

    // Abrir modal de edición.
    const botonEditar = page.locator('#table1 .btn-editar').first();

    await expect(botonEditar).toBeVisible();
    await botonEditar.click();

    const modalEditar = page.locator('#modalEditarPresentacion');
    await expect(modalEditar).toBeVisible();

    // Verificar campos.
    await expect(page.locator('#presentacion_edit')).toBeVisible();
    await expect(page.locator('#status_presentacion_edit')).toBeVisible();

    // Cerrar sin modificar.
    await modalEditar.getByRole('button', { name: 'Cerrar' }).click();
    await expect(modalEditar).toBeHidden();

    console.log('Prueba de humo del módulo Presentación modal editar finalizada');

    await page.close();
});


test('humo del módulo de presentación modal eliminar', async ({ page }) => {
    await page.goto('http://localhost:5000/admin?ruta=login');

    await page.getByRole('textbox', { name: 'Cédula' }).fill('4723317');
    await page.locator('#login-password').fill('admin123');

    await page.locator('#pow-check').click();
    await expect(page.locator('#pow-image')).toBeVisible();
    await page.locator('#pow-answer').fill('AB12CD');
    await page.locator('#pow-verify').click();

    await page.locator('#loginButton').click();
    console.log('inicio de sesión realizado');

    await expect(page.locator('.sidebar-menu')).toBeVisible({
        timeout: 15000
    });

    // Acceder al menú Unidad de Medida.
    const menuUnidadMedida = page.locator('.sidebar-menu .sidebar-item.has-sub').filter({
        has: page.getByText('Unidad de Medida', { exact: true })
    });

    await menuUnidadMedida.locator('> a.sidebar-link').click();

    // Acceder al módulo Presentación.
    const enlacePresentacion = page.locator(
        '.sidebar-menu a.submenu-link[href="/admin?ruta=presentacion"]'
    );

    await expect(enlacePresentacion).toBeVisible();
    await expect(enlacePresentacion).toBeEnabled();
    await enlacePresentacion.click();

    await expect(page.locator('#table1')).toBeVisible();

    // Abrir modal de eliminación.
    const botonEliminar = page.locator('#table1 .btn-eliminar').first();

    await expect(botonEliminar).toBeVisible();
    await botonEliminar.click();

    const modalEliminar = page.locator('#modalEliminarPresentacion');
    await expect(modalEliminar).toBeVisible();

    // Verificar el título y el nombre de la presentación.
    await expect(
        modalEliminar.getByRole('heading', { name: 'Confirmar Eliminación' })
    ).toBeVisible();

    await expect(modalEliminar.locator('#nombre_presentacion')).toBeVisible();

    // Comprobar los botones.
    await expect(
        modalEliminar.getByRole('button', { name: 'No' })
    ).toBeVisible();

    await expect(
        modalEliminar.getByRole('button', { name: 'Eliminar' })
    ).toBeVisible();

    // Cerrar sin eliminar la presentación.
    await modalEliminar.getByRole('button', { name: 'No' }).click();
    await expect(modalEliminar).toBeHidden();

    console.log('Prueba de humo del módulo Presentación modal eliminar finalizada');

    await page.close();
});