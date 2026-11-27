
import { test, expect } from '@playwright/test';


test('humo completo del módulo Usuarios', async ({ page }) => {
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

    // Acceder al módulo Usuarios.
    const enlaceUsuarios = page.locator(
        '#menuConfiguracion .submenu a.submenu-link[href="/admin?ruta=usuarios"]'
    );

    await expect(enlaceUsuarios).toBeVisible();
    await expect(enlaceUsuarios).toBeEnabled();
    await enlaceUsuarios.click();

    // Comprobar que cargó el módulo y su tabla.
    await expect(page.locator('section[data-modulo="usuarios"]')).toBeVisible();
    await expect(page.locator('#table1')).toBeVisible();

    console.log('Tabla de usuarios cargada');

    // Abrir y cerrar modal de registro.
    await page.getByRole('button', { name: 'Registrar Usuarios' }).click();

    const modalRegistro = page.locator('#primary');

    await expect(modalRegistro).toBeVisible();
    await expect(modalRegistro.locator('#fromUsuarios')).toBeVisible();
    await expect(modalRegistro.locator('#cedula')).toBeVisible();
    await expect(modalRegistro.locator('#nombre_usuario')).toBeVisible();
    await expect(modalRegistro.locator('#apellido_usuario_reg')).toBeVisible();
    await expect(modalRegistro.locator('#telefono_reg')).toBeVisible();
    await expect(modalRegistro.locator('#direccion_reg')).toBeVisible();
    await expect(modalRegistro.locator('#correo_reg')).toBeVisible();
    await expect(modalRegistro.locator('#password')).toBeVisible();
    await expect(modalRegistro.locator('#cod_rol_edit')).toBeVisible();

    await modalRegistro.getByRole('button', { name: 'Cerrar' }).click();
    await expect(modalRegistro).toBeHidden();

    console.log('Modal de registro abierto y cerrado');

    // Abrir y cerrar modal de edición del primer usuario.
    const botonEditar = page.locator('#table1 .btn-editar').first();

    await expect(botonEditar).toBeVisible();
    await botonEditar.click();

    const modalEditar = page.locator('#editModal');

    await expect(modalEditar).toBeVisible();
    await expect(modalEditar.locator('#formEditarusuario')).toBeVisible();
    await expect(modalEditar.locator('#cedula_edit')).toBeVisible();
    await expect(modalEditar.locator('#nombre_usuario_edit')).toBeVisible();
    await expect(modalEditar.locator('#apellido_usuario_edit')).toBeVisible();
    await expect(modalEditar.locator('#telefono_edit')).toBeVisible();
    await expect(modalEditar.locator('#direccion_edit')).toBeVisible();
    await expect(modalEditar.locator('#correo_edit')).toBeVisible();
    await expect(modalEditar.locator('#changePasswordBtn')).toBeVisible();
    await expect(modalEditar.locator('#cod_rol_edit')).toBeVisible();
    await expect(modalEditar.locator('#status_edit')).toBeVisible();

    await modalEditar.getByRole('button', { name: 'Cerrar' }).click();
    await expect(modalEditar).toBeHidden();

    // Abrir y cerrar modal de eliminación del primer usuario.
    const botonEliminar = page.locator('#table1 .btn-eliminar').first();

    await expect(botonEliminar).toBeVisible();
    await botonEliminar.click();

    const modalEliminar = page.locator('#deleteModal');

    await expect(modalEliminar).toBeVisible();
    await expect(modalEliminar.locator('#elimodal')).toBeVisible();

    await expect(
        modalEliminar.getByRole('heading', { name: 'Confirmar Eliminación' })
    ).toBeVisible();

    await expect(modalEliminar.locator('#usuariosdCedula')).toBeAttached();
    await expect(modalEliminar.locator('#nombreEliminar')).toBeVisible();

    // Cancelar eliminación.
    await modalEliminar.getByRole('button', { name: 'No' }).click();
    await expect(modalEliminar).toBeHidden();


    console.log('Prueba de humo completa del módulo Usuarios finalizada');
});


test('humo del módulo de usuarios modal registro', async ({ page }) => {

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

    // Acceder al módulo Usuario.
    const enlaceUsuario = page.locator(
        '#menuConfiguracion .submenu a.submenu-link[href="/admin?ruta=usuarios"]'
    );

    await expect(enlaceUsuario).toBeVisible();
    await enlaceUsuario.click();


    // Abrir modal de registro.
    await page.getByRole('button', { name: 'Registrar Usuarios' }).click();

    const modalRegistro = page.locator('#primary');

    await expect(modalRegistro).toBeVisible();

    // Verificar formulario.
    await expect(modalRegistro.locator('#fromUsuarios')).toBeVisible();

    // Verificar campos del formulario.
    await expect(modalRegistro.locator('#cedula')).toBeVisible();
    await expect(modalRegistro.locator('#nombre_usuario')).toBeVisible();
    await expect(modalRegistro.locator('#apellido_usuario_reg')).toBeVisible();
    await expect(modalRegistro.locator('#telefono_reg')).toBeVisible();
    await expect(modalRegistro.locator('#direccion_reg')).toBeVisible();
    await expect(modalRegistro.locator('#correo_reg')).toBeVisible();
    await expect(modalRegistro.locator('#password')).toBeVisible();
    await expect(modalRegistro.locator('#cod_rol_edit')).toBeVisible();

    // Cerrar modal de registro.
    await modalRegistro.locator('#btnCerrarModal').click();

    await expect(modalRegistro).toBeHidden();

    console.log('Prueba de humo del módulo Usuario completada');

});


test('humo del módulo de usuarios modal edición', async ({ page }) => {

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

    // Acceder al módulo Usuario.
    const enlaceUsuario = page.locator(
        '#menuConfiguracion .submenu a.submenu-link[href="/admin?ruta=usuarios"]'
    );

    await expect(enlaceUsuario).toBeVisible();
    await enlaceUsuario.click();


    // Abrir modal de edición del primer usuario.
    const botonEditar = page.locator('#table1 .btn-editar').first();

    await expect(botonEditar).toBeVisible();
    await botonEditar.click();

    const modalEditar = page.locator('#editModal');

    await expect(modalEditar).toBeVisible();

    // Verificar formulario.
    await expect(modalEditar.locator('#formEditarusuario')).toBeVisible();

    // Verificar campos del formulario.
    await expect(modalEditar.locator('#cedula_edit')).toBeVisible();
    await expect(modalEditar.locator('#nombre_usuario_edit')).toBeVisible();
    await expect(modalEditar.locator('#apellido_usuario_edit')).toBeVisible();
    await expect(modalEditar.locator('#telefono_edit')).toBeVisible();
    await expect(modalEditar.locator('#direccion_edit')).toBeVisible();
    await expect(modalEditar.locator('#correo_edit')).toBeVisible();

    // Verificar botón para cambiar contraseña.
    await expect(modalEditar.locator('#changePasswordBtn')).toBeVisible();

    // Verificar campos de contraseña.
    await expect(modalEditar.locator('#passwordField')).toBeHidden();

    // Verificar selector de rol y estado.
    await expect(modalEditar.locator('#cod_rol_edit')).toBeVisible();
    await expect(modalEditar.locator('#status_edit')).toBeVisible();

    // Verificar botón Editar.
    await expect(
        modalEditar.getByRole('button', { name: 'Editar' })
    ).toBeVisible();

    // Cerrar modal de edición.
    await modalEditar.locator('#btnCerrar').click();

    await expect(modalEditar).toBeHidden();

    console.log('Prueba de humo del módulo Usuario modal edición completada');

});