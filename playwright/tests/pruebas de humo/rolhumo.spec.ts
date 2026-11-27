
import { test, expect } from '@playwright/test';

test('humo completo del módulo Rol', async ({ page }) => {
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

    // Acceder al menú Configuración.
    await page.locator('#menuConfiguracion > a.sidebar-link').click();

    // Acceder al módulo Rol.
    const enlaceRol = page.locator(
        '#menuConfiguracion .submenu a.submenu-link[href="/admin?ruta=rol"]'
    );

    await expect(enlaceRol).toBeVisible();
    await expect(enlaceRol).toBeEnabled();
    await enlaceRol.click();

    console.log('Acceso al módulo Rol');

    // Comprobar que cargó el módulo y su tabla.
    await expect(page.locator('section[data-modulo="rol"]')).toBeVisible();
    await expect(page.locator('#table1')).toBeVisible();

    console.log('Tabla de roles cargada');

    // Abrir y cerrar modal de registro.
    await page.getByRole('button', { name: 'Registrar Rol' }).click();

    const modalRegistro = page.locator('#Rol');

    await expect(modalRegistro).toBeVisible();
    await expect(modalRegistro.locator('#formRol')).toBeVisible();
    await expect(modalRegistro.locator('#nombre_rol')).toBeVisible();

    await modalRegistro.locator('#btnCerrarModal').click();
    await expect(modalRegistro).toBeHidden();

    console.log('Modal de registro abierto y cerrado');

    // Abrir y cerrar modal de edición del primer rol editable.
    const botonEditar = page.locator('#table1 .btn-editar:not([disabled])').first();

    await expect(botonEditar).toBeVisible();
    await botonEditar.click();

    const modalEditar = page.locator('#editModal');

    await expect(modalEditar).toBeVisible();
    await expect(modalEditar.locator('#formEditRol')).toBeVisible();
    await expect(modalEditar.locator('#edit_cod_rol')).toBeAttached();
    await expect(modalEditar.locator('#edit_rol')).toBeVisible();
    await expect(modalEditar.locator('#edit_estado')).toBeVisible();

    await modalEditar.getByRole('button', { name: 'Cerrar' }).click();
    await expect(modalEditar).toBeHidden();

    console.log('Modal de edición abierto y cerrado');

    // Abrir y cerrar modal de eliminación del primer rol editable.
    const botonEliminar = page.locator('#table1 .btn-eliminar:not([disabled])').first();

    await expect(botonEliminar).toBeVisible();
    await botonEliminar.click();

    const modalEliminar = page.locator('#deleteModal');

    await expect(modalEliminar).toBeVisible();
    await expect(modalEliminar.locator('#elimodal')).toBeVisible();
    await expect(
        modalEliminar.getByRole('heading', { name: 'Confirmar Eliminación' })
    ).toBeVisible();
    await expect(modalEliminar.locator('#rolCodigo')).toBeAttached();
    await expect(modalEliminar.locator('#nombreEliminar')).toBeVisible();

    // Cancelar eliminación.
    await modalEliminar.getByRole('button', { name: 'No' }).click();
    await expect(modalEliminar).toBeHidden();

    console.log('Modal de eliminación abierto y cerrado');

    console.log('Prueba de humo completa del módulo Rol finalizada');
});


test('humo del módulo de rol modal registro', async ({ page }) => {
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

    // Acceder al menú Configuración.
    await page.locator('#menuConfiguracion > a.sidebar-link').click();

    // Acceder al módulo Rol.
    const enlaceRol = page.locator(
        '#menuConfiguracion .submenu a.submenu-link[href="/admin?ruta=rol"]'
    );

    await expect(enlaceRol).toBeVisible();
    await enlaceRol.click();

    console.log('Acceso al módulo Rol');

    // Abrir modal de registro.
    await page.getByRole('button', { name: 'Registrar Rol' }).click();

    const modalRegistro = page.locator('#Rol');

    await expect(modalRegistro).toBeVisible();
    await expect(modalRegistro.locator('#formRol')).toBeVisible();
    await expect(modalRegistro.locator('#nombre_rol')).toBeVisible();

    // Cerrar modal de registro.
    await modalRegistro.locator('#btnCerrarModal').click();
    await expect(modalRegistro).toBeHidden();

    console.log('orueba completa');
});


test('humo del módulo de rol modal editar', async ({ page }) => {
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

    // Acceder al menú Configuración.
    await page.locator('#menuConfiguracion > a.sidebar-link').click();

    // Acceder al módulo Rol.
    const enlaceRol = page.locator(
        '#menuConfiguracion .submenu a.submenu-link[href="/admin?ruta=rol"]'
    );

    await expect(enlaceRol).toBeVisible();
    await enlaceRol.click();

    console.log('Acceso al módulo Rol');

    // Abrir modal de edición.
    const botonEditar = page.locator('#table1 .btn-editar:not([disabled])').first();

    await expect(botonEditar).toBeVisible();
    await botonEditar.click();

    const modalEditar = page.locator('#editModal');

    await expect(modalEditar).toBeVisible();
    await expect(modalEditar.locator('#formEditRol')).toBeVisible();
    await expect(modalEditar.locator('#edit_cod_rol')).toBeAttached();
    await expect(modalEditar.locator('#edit_rol')).toBeVisible();
    await expect(modalEditar.locator('#edit_estado')).toBeVisible();



    // Cerrar modal de edición.
    await modalEditar.locator('#btnCerrar').click();
    await expect(modalEditar).toBeHidden();

    console.log('Modal de edición completa');
});


test('humo del módulo de rol modal eliminar', async ({ page }) => {
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

    // Acceder al menú Configuración.
    await page.locator('#menuConfiguracion > a.sidebar-link').click();

    // Acceder al módulo Rol.
    const enlaceRol = page.locator(
        '#menuConfiguracion .submenu a.submenu-link[href="/admin?ruta=rol"]'
    );

    await expect(enlaceRol).toBeVisible();
    await enlaceRol.click();



    // Abrir modal de eliminación.
    const botonEliminar = page.locator('#table1 .btn-eliminar:not([disabled])').first();

    await expect(botonEliminar).toBeVisible();
    await botonEliminar.click();

    const modalEliminar = page.locator('#deleteModal');

    await expect(modalEliminar).toBeVisible();
    await expect(modalEliminar.locator('#elimodal')).toBeVisible();
    await expect(
        modalEliminar.getByRole('heading', { name: 'Confirmar Eliminación' })
    ).toBeVisible();
    await expect(modalEliminar.locator('#rolCodigo')).toBeAttached();
    await expect(modalEliminar.locator('#nombreEliminar')).toBeVisible();

    console.log('Modal de eliminación abierto');

    // Cancelar eliminación.
    await modalEliminar.getByRole('button', { name: 'No' }).click();
    await expect(modalEliminar).toBeHidden();

    console.log('prueba Modal de eliminación completa');
});
