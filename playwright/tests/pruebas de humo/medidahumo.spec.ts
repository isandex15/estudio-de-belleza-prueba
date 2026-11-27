
import { test, expect } from '@playwright/test';


test('humo completo del módulo Medida', async ({ page }) => {
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

    // Acceder al módulo Medida.
    const enlaceMedida = page.locator(
        '.sidebar-menu a.submenu-link[href="/admin?ruta=unidadmedida"]'
    );

    await expect(enlaceMedida).toBeVisible();
    await expect(enlaceMedida).toBeEnabled();
    await enlaceMedida.click();

    console.log('Acceso al módulo Medida');

    // Comprobar que cargó el módulo y su tabla.
    await expect(page.locator('section[data-modulo="unidadmedida"]')).toBeVisible();
    await expect(page.locator('#table1')).toBeVisible();

    console.log('Tabla de medidas cargada');

    // Abrir y cerrar modal de registro.
    await page.getByRole('button', { name: 'Registrar medida' }).click();

    const modalRegistro = page.locator('#modalRegistrarMedida');
    await expect(modalRegistro).toBeVisible();

    await expect(modalRegistro.locator('#medida_reg')).toBeVisible();

    await modalRegistro.getByRole('button', { name: 'Cerrar' }).click();
    await expect(modalRegistro).toBeHidden();
    await expect(page.locator('.modal-backdrop')).toHaveCount(0);

    console.log('Modal de registro abierto y cerrado');

    // Abrir y cerrar modal de edición del primer registro.
    const botonEditar = page.locator('#table1 .btn-editar').first();

    await expect(botonEditar).toBeVisible();
    await botonEditar.click();

    const modalEditar = page.locator('#modalEditarMedida');
    await expect(modalEditar).toBeVisible();

    await expect(modalEditar.locator('#cod_medida_edit')).toBeAttached();
    await expect(modalEditar.locator('#medida_edit')).toBeVisible();
    await expect(modalEditar.locator('#status_edit')).toBeVisible();

    await modalEditar.getByRole('button', { name: 'Cerrar' }).click();
    await expect(modalEditar).toBeHidden();
    await expect(page.locator('.modal-backdrop')).toHaveCount(0);

    console.log('Modal de edición abierto y cerrado');

    // Abrir y cerrar modal de eliminación del primer registro.
    const botonEliminar = page.locator('#table1 .btn-eliminar').first();

    await expect(botonEliminar).toBeVisible();
    await expect(botonEliminar).toBeEnabled();
    await botonEliminar.click();

    const modalEliminar = page.locator('#modalEliminarMedida');
    await expect(modalEliminar).toBeVisible();

    await expect(
        modalEliminar.getByRole('heading', { name: 'Confirmar Eliminación' })
    ).toBeVisible();

    await expect(modalEliminar.locator('#cod_medida_eliminar')).toBeAttached();
    await expect(modalEliminar.locator('#nombre_medida')).toBeVisible();

    await expect(
        modalEliminar.getByRole('button', { name: 'No' })
    ).toBeVisible();

    await expect(
        modalEliminar.getByRole('button', { name: 'Eliminar' })
    ).toBeVisible();

    await modalEliminar.getByRole('button', { name: 'No' }).click();
    await expect(modalEliminar).toBeHidden();
    await expect(page.locator('.modal-backdrop')).toHaveCount(0);


    console.log('Prueba de humo completa del módulo Medida finalizada');
});


test('humo del módulo Medida modal registro', async ({ page }) => {
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

    // Acceder al módulo Medida.
    const enlaceMedida = page.locator(
        '.sidebar-menu a.submenu-link[href="/admin?ruta=unidadmedida"]'
    );

    await expect(enlaceMedida).toBeVisible();
    await expect(enlaceMedida).toBeEnabled();
    await enlaceMedida.click();


    // Comprobar que cargó el módulo.
    await expect(page.locator('section[data-modulo="unidadmedida"]')).toBeVisible();
    await expect(page.locator('#table1')).toBeVisible();

    // Abrir modal de registro.
    await page.getByRole('button', { name: 'Registrar medida' }).click();

    const modalRegistro = page.locator('#modalRegistrarMedida');

    await expect(modalRegistro).toBeVisible();
    await expect(modalRegistro.locator('#formRegistrarMedida')).toBeVisible();
    await expect(modalRegistro.locator('#medida_reg')).toBeVisible();
    await expect(modalRegistro.locator('#medida_reg')).toBeEnabled();


    // Cerrar modal sin guardar.
    await modalRegistro.getByRole('button', { name: 'Cerrar' }).click();

    await expect(modalRegistro).toBeHidden();

    console.log('Prueba de humo del modal de registro de Medida finalizada');
});


test('humo del módulo Medida modal edición', async ({ page }) => {
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

    // Acceder al módulo Medida.
    const enlaceMedida = page.locator(
        '.sidebar-menu a.submenu-link[href="/admin?ruta=unidadmedida"]'
    );

    await expect(enlaceMedida).toBeVisible();
    await expect(enlaceMedida).toBeEnabled();
    await enlaceMedida.click();


    // Comprobar tabla.
    await expect(page.locator('#table1')).toBeVisible();

    // Abrir modal de edición.
    const botonEditar = page.locator('#table1 .btn-editar').first();

    await expect(botonEditar).toBeVisible();
    await botonEditar.click();

    const modalEditar = page.locator('#modalEditarMedida');

    await expect(modalEditar).toBeVisible();
    await expect(modalEditar.locator('#formEditarMedida')).toBeVisible();
    await expect(modalEditar.locator('#cod_medida_edit')).toBeAttached();
    await expect(modalEditar.locator('#medida_edit')).toBeVisible();
    await expect(modalEditar.locator('#status_edit')).toBeVisible();


    // Cerrar modal sin guardar cambios.
    await modalEditar.getByRole('button', { name: 'Cerrar' }).click();

    await expect(modalEditar).toBeHidden();

    console.log('Prueba de humo del modal de edición de Medida finalizada');
});

test('humo del módulo Medida modal eliminación', async ({ page }) => {
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

    // Acceder al módulo Medida.
    const enlaceMedida = page.locator(
        '.sidebar-menu a.submenu-link[href="/admin?ruta=unidadmedida"]'
    );

    await expect(enlaceMedida).toBeVisible();
    await expect(enlaceMedida).toBeEnabled();
    await enlaceMedida.click();


    // Comprobar tabla.
    await expect(page.locator('#table1')).toBeVisible();

    // Abrir modal de eliminación.
    const botonEliminar = page.locator('#table1 .btn-eliminar').first();

    await expect(botonEliminar).toBeVisible();
    await botonEliminar.click();

    const modalEliminar = page.locator('#modalEliminarMedida');

    await expect(modalEliminar).toBeVisible();
    await expect(modalEliminar.locator('#formEliminarMedida')).toBeVisible();

    await expect(
        modalEliminar.getByRole('heading', { name: 'Confirmar Eliminación' })
    ).toBeVisible();

    await expect(modalEliminar.locator('#cod_medida_eliminar')).toBeAttached();
    await expect(modalEliminar.locator('#nombre_medida')).toBeVisible();

    await expect(
        modalEliminar.getByRole('button', { name: 'No' })
    ).toBeVisible();

    await expect(
        modalEliminar.getByRole('button', { name: 'Eliminar' })
    ).toBeVisible();


    // Cancelar eliminación.
    await modalEliminar.getByRole('button', { name: 'No' }).click();

    await expect(modalEliminar).toBeHidden();

    console.log('Prueba de humo del modal de eliminación de Medida finalizada');
});