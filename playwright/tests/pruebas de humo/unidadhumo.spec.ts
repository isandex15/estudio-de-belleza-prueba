
import { test, expect } from '@playwright/test';


test('humo completo del módulo Unidad', async ({ page }) => {
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

    // Acceder al módulo Unidad.
    const enlaceUnidad = page.locator(
        '.sidebar-menu a.submenu-link[href="/admin?ruta=unidad"]'
    );

    await expect(enlaceUnidad).toBeVisible();
    await expect(enlaceUnidad).toBeEnabled();
    await enlaceUnidad.click();

    console.log('Acceso al módulo Unidad');

    // Comprobar que cargó el módulo y su tabla.
    await expect(page.locator('section[data-modulo="unidad"]')).toBeVisible();
    await expect(page.locator('#table1')).toBeVisible();

    console.log('Tabla de unidades cargada');

    // Abrir y cerrar modal de registro.
    await page.getByRole('button', { name: 'Registrar Unidad' }).click();

    const modalRegistro = page.locator('#modalRegistrarUnidad');
    await expect(modalRegistro).toBeVisible();

    await expect(modalRegistro.locator('#nombre_unidad_reg')).toBeVisible();
    await expect(modalRegistro.locator('#cod_presentacion_reg')).toBeVisible();
    await expect(modalRegistro.locator('#cod_medida_reg')).toBeVisible();

    await modalRegistro.getByRole('button', { name: 'Cerrar' }).click();
    await expect(modalRegistro).toBeHidden();

    console.log('Modal de registro abierto y cerrado');

    // Abrir y cerrar modal de edición del primer registro.
    const botonEditar = page.locator('#table1 .btn-editar').first();

    await expect(botonEditar).toBeVisible();
    await botonEditar.click();

    const modalEditar = page.locator('#modalEditarUnidad');
    await expect(modalEditar).toBeVisible();

    await expect(modalEditar.locator('#cod_unidad_edit')).toBeAttached();
    await expect(modalEditar.locator('#nombre_unidad_edit')).toBeVisible();
    await expect(modalEditar.locator('#cod_presentacion_edit')).toBeVisible();
    await expect(modalEditar.locator('#cod_medida_edit')).toBeVisible();
    await expect(modalEditar.locator('#status_unidad_edit')).toBeVisible();

    await modalEditar.getByRole('button', { name: 'Cerrar' }).click();
    await expect(modalEditar).toBeHidden();

    console.log('Modal de edición abierto y cerrado');

    // Abrir y cerrar modal de eliminación del primer registro.
    const botonEliminar = page.locator('#table1 .btn-eliminar').first();

    await expect(botonEliminar).toBeVisible();
    await botonEliminar.click();

    const modalEliminar = page.locator('#modalEliminarUnidad');
    await expect(modalEliminar).toBeVisible();

    await expect(
        modalEliminar.getByRole('heading', { name: 'Confirmar Eliminación' })
    ).toBeVisible();

    await expect(modalEliminar.locator('#cod_unidad_eliminar')).toBeAttached();
    await expect(modalEliminar.locator('#nombre_unidad')).toBeVisible();

    await modalEliminar.getByRole('button', { name: 'No' }).click();
    await expect(modalEliminar).toBeHidden();

    console.log('Modal de eliminación abierto y cerrado');

    console.log('Prueba de humo completa del módulo Unidad finalizada');
});





test('humo del módulo de unidad modal registro', async ({ page }) => {
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

    // Acceder al módulo Unidad.
    const enlaceUnidad = page.locator(
        '.sidebar-menu a.submenu-link[href="/admin?ruta=unidad"]'
    );

    await expect(enlaceUnidad).toBeVisible();
    await expect(enlaceUnidad).toBeEnabled();
    await enlaceUnidad.click();

    await expect(page.locator('#table1')).toBeVisible();

    // Abrir modal de registro.
    await page.getByRole('button', { name: 'Registrar Unidad' }).click();

    const modalRegistro = page.locator('#modalRegistrarUnidad');
    await expect(modalRegistro).toBeVisible();

 
    // Cerrar sin registrar la unidad.
    await modalRegistro.getByRole('button', { name: 'Cerrar' }).click();
    await expect(modalRegistro).toBeHidden();

    console.log('Prueba de humo del módulo Unidad modal registro finalizada');
});


test('humo del módulo de unidad modal editar', async ({ page }) => {
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

    // Acceder al módulo Unidad.
    const enlaceUnidad = page.locator(
        '.sidebar-menu a.submenu-link[href="/admin?ruta=unidad"]'
    );

    await expect(enlaceUnidad).toBeVisible();
    await expect(enlaceUnidad).toBeEnabled();
    await enlaceUnidad.click();

    await expect(page.locator('#table1')).toBeVisible();

    // Abrir modal de edición.
    const botonEditar = page.locator('#table1 .btn-editar').first();

    await expect(botonEditar).toBeVisible();
    await botonEditar.click();

    const modalEditar = page.locator('#modalEditarUnidad');
    await expect(modalEditar).toBeVisible();

    // Verificar campos.
    await expect(modalEditar.locator('#cod_unidad_edit')).toBeAttached();
    await expect(modalEditar.locator('#nombre_unidad_edit')).toBeVisible();
    await expect(modalEditar.locator('#cod_presentacion_edit')).toBeVisible();
    await expect(modalEditar.locator('#cod_medida_edit')).toBeVisible();
    await expect(modalEditar.locator('#status_unidad_edit')).toBeVisible();

    // Cerrar sin modificar.
    await modalEditar.getByRole('button', { name: 'Cerrar' }).click();
    await expect(modalEditar).toBeHidden();

    console.log('Prueba de humo del módulo Unidad modal editar');
});



test('humo del módulo de unidad modal eliminar', async ({ page }) => {
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
    console.log('inicio de sesión realizado');

    await expect(page.locator('.sidebar-menu')).toBeVisible({
        timeout: 15000
    });

    // Acceder al menú Unidad de Medida.
    const menuUnidadMedida = page.locator('.sidebar-menu .sidebar-item.has-sub').filter({
        has: page.getByText('Unidad de Medida', { exact: true })
    });

    await menuUnidadMedida.locator('> a.sidebar-link').click();

    // Acceder al módulo Unidad.
    const enlaceUnidad = page.locator(
        '.sidebar-menu a.submenu-link[href="/admin?ruta=unidad"]'
    );

    await expect(enlaceUnidad).toBeVisible();
    await expect(enlaceUnidad).toBeEnabled();
    await enlaceUnidad.click();

    await expect(page.locator('#table1')).toBeVisible();

    // Abrir modal de eliminación.
    const botonEliminar = page.locator('#table1 .btn-eliminar').first();

    await expect(botonEliminar).toBeVisible();
    await botonEliminar.click();

    const modalEliminar = page.locator('#modalEliminarUnidad');
    await expect(modalEliminar).toBeVisible();

    // Verificar contenido del modal.
    await expect(
        modalEliminar.getByRole('heading', { name: 'Confirmar Eliminación' })
    ).toBeVisible();

    await expect(modalEliminar.locator('#cod_unidad_eliminar')).toBeAttached();
    await expect(modalEliminar.locator('#nombre_unidad')).toBeVisible();

    await expect(
        modalEliminar.getByText('¿Desea eliminar la unidad')
    ).toBeVisible();

    // Cancelar eliminación.
    await modalEliminar.getByRole('button', { name: 'No' }).click();

    await expect(modalEliminar).toBeHidden();

    console.log('Prueba de humo del módulo Unidad modal eliminar');
});