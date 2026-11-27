
import { test, expect } from '@playwright/test';




test('humo completo del módulo Clientes', async ({ page }) => {
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

    // Acceder al módulo Clientes.
    const enlaceClientes = page.locator(
        '.sidebar-menu a.sidebar-link[href="/admin?ruta=cliente"]'
    );

    await expect(enlaceClientes).toBeVisible();
    await expect(enlaceClientes).toBeEnabled();
    await enlaceClientes.click();

    console.log('Acceso al módulo Clientes');

    // Comprobar que cargó el módulo y su tabla.
    await expect(page.locator('section[data-modulo="clientes"]')).toBeVisible();
    await expect(page.locator('#table1')).toBeVisible();

    console.log('Tabla de clientes cargada');

    // Abrir y cerrar modal de registro.
    await page.getByRole('button', { name: 'Registrar Clientes' }).click();

    const modalRegistro = page.locator('#modalRegistrarCliente');
    await expect(modalRegistro).toBeVisible();

    await expect(page.locator('#cedula_reg')).toBeVisible();
    await expect(page.locator('#nombre_usuario_reg')).toBeVisible();
    await expect(page.locator('#apellido_usuario_reg')).toBeVisible();
    await expect(page.locator('#telefono_reg')).toBeVisible();
    await expect(page.locator('#direccion_reg')).toBeVisible();
    await expect(page.locator('#correo_reg')).toBeVisible();

    await modalRegistro.getByRole('button', { name: 'Cerrar' }).click();
    await expect(modalRegistro).toBeHidden();

    // Abrir y cerrar modal de edición del primer cliente.
    const botonEditar = page.locator('#table1 .btn-editar').first();

    await expect(botonEditar).toBeVisible();
    await botonEditar.click();

    const modalEditar = page.locator('#modalEditar');
    await expect(modalEditar).toBeVisible();

    await expect(modalEditar.locator('#cedula_edit')).toBeVisible();
    await expect(modalEditar.locator('#nombre_usuario_edit')).toBeVisible();
    await expect(modalEditar.locator('#apellido_usuario_edit')).toBeVisible();
    await expect(modalEditar.locator('#telefono_edit')).toBeVisible();
    await expect(modalEditar.locator('#direccion_edit')).toBeVisible();
    await expect(modalEditar.locator('#correo_edit')).toBeVisible();
    await expect(modalEditar.locator('#status_edit')).toBeVisible();

    await modalEditar.getByRole('button', { name: 'Cerrar' }).click();
    await expect(modalEditar).toBeHidden();



    // Abrir y cerrar modal de eliminación del primer cliente.
    const botonEliminar = page.locator('#table1 .btn-eliminar').first();

    await expect(botonEliminar).toBeVisible();
    await botonEliminar.click();

    const modalEliminar = page.locator('#modalEliminarCliente');

    // Comprobar que el modal se abra.
    await expect(modalEliminar).toBeVisible({
        timeout: 10000
    });

    // Verificar contenido del modal.
    await expect(
        modalEliminar.getByRole('heading', { name: 'Confirmar Eliminación' })
    ).toBeVisible();

    await expect(modalEliminar.locator('#cedula_eliminar')).toBeAttached();
    await expect(modalEliminar.locator('#nombre_usuario')).toBeVisible();

    await expect(
        modalEliminar.getByText('¿Desea eliminar a')
    ).toBeVisible();

    // Cancelar eliminación.
    await modalEliminar.getByRole('button', { name: 'No' }).click();

    await expect(modalEliminar).toBeHidden();

    console.log('Prueba de humo completa del módulo Clientes finalizada');
});


test('humo del módulo de clientes modal registro', async ({ page }) => {
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

    // Acceder al módulo Clientes mediante el menú lateral.
    const enlaceClientes = page.locator(
        '.sidebar-menu a.sidebar-link[href="/admin?ruta=cliente"]'
    );

    await expect(enlaceClientes).toBeVisible();
    await expect(enlaceClientes).toBeEnabled();
    await enlaceClientes.click();

    await expect(page.locator('#table1')).toBeVisible();
    await expect(page.getByRole('heading', { name: 'Clientes' })).toBeVisible();

    // Abrir modal de registro.
    await page.getByRole('button', { name: 'Registrar Clientes' }).click();

    const modalRegistro = page.locator('#modalRegistrarCliente');
    await expect(modalRegistro).toBeVisible();

    // Introducir datos del cliente.
    await page.locator('#cedula_reg').fill('12345678');
    await page.locator('#nombre_usuario_reg').fill('María');
    await page.locator('#apellido_usuario_reg').fill('Pérez');
    await page.locator('#telefono_reg').fill('04141234567');
    await page.locator('#direccion_reg').fill('Av. Principal');
    await page.locator('#correo_reg').fill('maria@gmail.com');

    // Comprobar los datos introducidos.
    await expect(page.locator('#cedula_reg')).toHaveValue('12345678');
    await expect(page.locator('#nombre_usuario_reg')).toHaveValue('María');
    await expect(page.locator('#apellido_usuario_reg')).toHaveValue('Pérez');
    await expect(page.locator('#telefono_reg')).toHaveValue('04141234567');
    await expect(page.locator('#direccion_reg')).toHaveValue('Av. Principal');
    await expect(page.locator('#correo_reg')).toHaveValue('maria@gmail.com');

    // Cerrar sin registrar el cliente.
    await modalRegistro.getByRole('button', { name: 'Cerrar' }).click();
    await expect(modalRegistro).toBeHidden();

    console.log('Prueba de humo del módulo Clientes modal registro finalizada');
});



test('humo del módulo de clientes modal editar', async ({ page }) => {
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

    const enlaceClientes = page.locator(
        '.sidebar-menu a.sidebar-link[href="/admin?ruta=cliente"]'
    );

    await expect(enlaceClientes).toBeVisible();
    await expect(enlaceClientes).toBeEnabled();
    await enlaceClientes.click();

    await expect(page.locator('#table1')).toBeVisible();
    await expect(page.getByRole('heading', { name: 'Clientes' })).toBeVisible();

    // Abrir modal de edición
    const botonEditar = page.locator('#table1 .btn-editar').first();

    await expect(botonEditar).toBeVisible();
    await botonEditar.click();

    const modalEditar = page.locator('#modalEditar');
    await expect(modalEditar).toBeVisible();

    // Verificar campos
    await expect(page.locator('#cedula_edit')).toBeVisible();
    await expect(page.locator('#nombre_usuario_edit')).toBeVisible();
    await expect(page.locator('#apellido_usuario_edit')).toBeVisible();
    await expect(page.locator('#telefono_edit')).toBeVisible();
    await expect(page.locator('#direccion_edit')).toBeVisible();
    await expect(page.locator('#correo_edit')).toBeVisible();
    await expect(page.locator('#status_edit')).toBeVisible();

    // Cerrar sin modificar
    await modalEditar.getByRole('button', { name: 'Cerrar' }).click();
    await expect(modalEditar).toBeHidden();

    console.log('Prueba de humo del módulo Clientes modal editar');
});


test('humo del módulo de clientes modal eliminar', async ({ page }) => {
    await page.goto('http://localhost:5000/admin?ruta=login');

    // Iniciar sesión
    await page.getByRole('textbox', { name: 'Cédula' }).fill('4723317');
    await page.locator('#login-password').fill('admin123');

    // Verificar CAPTCHA
    await page.locator('#pow-check').click();
    await expect(page.locator('#pow-image')).toBeVisible();
    await page.locator('#pow-answer').fill('AB12CD');
    await page.locator('#pow-verify').click();

    await page.locator('#loginButton').click();
    console.log('inicio de sesión realizado');

    await expect(page.locator('.sidebar-menu')).toBeVisible({
        timeout: 15000
    });

    // Entrar al módulo Clientes
    const enlaceClientes = page.locator(
        '.sidebar-menu a.sidebar-link[href="/admin?ruta=cliente"]'
    );

    await expect(enlaceClientes).toBeVisible();
    await expect(enlaceClientes).toBeEnabled();
    await enlaceClientes.click();

    await expect(page.locator('#table1')).toBeVisible();
    await expect(page.getByRole('heading', { name: 'Clientes' })).toBeVisible();

    // Abrir modal de eliminación
    const botonEliminar = page.locator('#table1 .btn-eliminar').first();

    await expect(botonEliminar).toBeVisible();
    await botonEliminar.click();

    const modalEliminar = page.locator('#modalEliminarCliente');
    await expect(modalEliminar).toBeVisible();

    // Verificar contenido del modal
    await expect(
        modalEliminar.getByRole('heading', { name: 'Confirmar Eliminación' })
    ).toBeVisible();

    await expect(modalEliminar.locator('#cedula_eliminar')).toBeAttached();
    await expect(modalEliminar.locator('#nombre_usuario')).toBeVisible();

    await expect(
        modalEliminar.getByText('¿Desea eliminar a')
    ).toBeVisible();

    // Cancelar eliminación
    await modalEliminar.getByRole('button', { name: 'No' }).click();

    await expect(modalEliminar).toBeHidden();

    console.log('Prueba de humo del módulo Clientes modal eliminar');
});
