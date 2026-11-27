


import { test, expect } from '@playwright/test';

test('humo completo del módulo Reservas', async ({ page }) => {

    // Iniciar sesión.
    await page.goto('http://localhost:5000/admin?ruta=login');

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

    // Acceder al módulo Reservas.
    const enlaceReservas = page.locator(
        '.sidebar-menu a.sidebar-link[href="/admin?ruta=reserva"]'
    );

    await enlaceReservas.click();

    const seccionReservas = page.locator('section[data-modulo="reservas"]');
    await expect(seccionReservas).toBeVisible();
    await expect(page.locator('#table1')).toBeVisible();



    // Verificar acceso al registro de reservas.
    await page.getByRole('link', { name: 'Registrar reserva' }).click();

    await expect(page).toHaveURL(/admin\?ruta=inicio/);
    console.log('Acceso al registro de reservas');

    // Regresar al módulo Reservas.
    await page.goto('http://localhost:5000/admin?ruta=reserva');

    await expect(seccionReservas).toBeVisible();

    // Verificar modal de edición.
    const botonEditar = page.locator(
        '#table1 button[data-bs-target="#editModalReserva"]'
    ).first();

    await expect(botonEditar).toBeVisible();
    await botonEditar.click();

    const modalEditar = page.locator('#editModalReserva');

    await expect(modalEditar).toBeVisible();
    await expect(modalEditar.locator('#formEditReserva')).toBeVisible();
    await expect(modalEditar.locator('#edit_cod_reserva')).toBeAttached();
    await expect(modalEditar.locator('#edit_cedula')).toBeVisible();
    await expect(modalEditar.locator('#edit_nombre')).toBeVisible();
    await expect(modalEditar.locator('#edit_fecha')).toBeVisible();
    await expect(modalEditar.locator('#edit_hora')).toBeVisible();
    await expect(modalEditar.locator('#status_edit')).toBeVisible();
    await expect(modalEditar.locator('#tablaServicios')).toBeVisible();

    await modalEditar.getByRole('button', { name: 'Cerrar' }).click();
    await expect(modalEditar).toBeHidden();


    // Verificar modal de cancelar/eliminar reserva.
    const botonEliminar = page.locator(
        '#table1 button[data-bs-target="#deleteModalReservas"]'
    ).first();

    await expect(botonEliminar).toBeVisible();
    await botonEliminar.click();

    const modalEliminar = page.locator('#deleteModalReservas');

    await expect(modalEliminar).toBeVisible();
    await expect(modalEliminar.locator('#formDeleteReserva')).toBeVisible();
    await expect(modalEliminar.locator('#cod_reserva_eliminar')).toBeAttached();
    await expect(modalEliminar.locator('#nombreEliminar')).toBeVisible();
    await expect(
        modalEliminar.getByRole('heading', { name: 'Confirmar Eliminación' })
    ).toBeVisible();

    await modalEliminar.getByRole('button', { name: 'No' }).click();
    await expect(modalEliminar).toBeHidden();

    console.log('Prueba de humo completa del módulo Reservas');
});




test('humo del módulo de reservas modal editar', async ({ page }) => {
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

    // Acceder al módulo Reservas.
    const enlaceReservas = page.locator(
        '.sidebar-menu a.sidebar-link[href="/admin?ruta=reserva"]'
    );

    await expect(enlaceReservas).toBeVisible();
    await enlaceReservas.click();

    console.log('Acceso al módulo Reservas');

    // Abrir modal de edición de la primera reserva activa.
    const botonEditar = page.locator(
        '#table1 button[data-bs-target="#editModalReserva"]'
    ).first();

    await expect(botonEditar).toBeVisible();
    await botonEditar.click();

    const modalEditar = page.locator('#editModalReserva');

    await expect(modalEditar).toBeVisible();
    await expect(modalEditar.locator('#formEditReserva')).toBeVisible();
    await expect(modalEditar.locator('#edit_cod_reserva')).toBeAttached();
    await expect(modalEditar.locator('#edit_cedula')).toBeVisible();
    await expect(modalEditar.locator('#edit_nombre')).toBeVisible();
    await expect(modalEditar.locator('#edit_fecha')).toBeVisible();
    await expect(modalEditar.locator('#edit_hora')).toBeVisible();
    await expect(modalEditar.locator('#status_edit')).toBeVisible();
    await expect(modalEditar.locator('#tablaServicios')).toBeVisible();
    // Cerrar modal de edición.
    await modalEditar.getByRole('button', { name: 'Cerrar' }).click();
    await expect(modalEditar).toBeHidden();

    console.log('Modal de edición prueba finalizada');
});
