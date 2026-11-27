
import { test, expect } from '@playwright/test';

test('humo del módulo de permisos', async ({ page }) => {
    await page.goto('http://localhost:5000/admin?ruta=login');

    await page.getByRole('textbox', { name: 'Cédula' }).click();
    await page.getByRole('textbox', { name: 'Cédula' }).fill('4723317');
    await page.getByRole('textbox', { name: 'Password' }).click();
    await page.getByRole('textbox', { name: 'Password' }).fill('admin123');
    await page.locator('#pow-open').click();
    await page.locator('#pow-answer').fill('AB12CD');
    await page.locator('#pow-verify').click();
    console.log('captcha verificado');
    await page.locator("button[id='loginButton']").click();
    console.log('boton sesion iniciada correctamente');

    await expect(page.locator('.sidebar-menu')).toBeVisible({
        timeout: 15000
    });

    // Acceder al menú Configuración.
    await page.locator('#menuConfiguracion > a.sidebar-link').click();

    const enlacePermisos = page.locator(
        '.sidebar-menu a.submenu-link[href="/admin?ruta=permisos"]'
    );
    await expect(enlacePermisos).toBeVisible();
    await enlacePermisos.click();


    // VERIFICAR CARGA DE LA TABLA
    const tablaPermisos = page.locator('#table1');
    await expect(tablaPermisos).toBeVisible();
    await expect(tablaPermisos.locator('tbody tr').first()).toBeVisible();


    // REGISTRAR PERMISOS
    await page.getByRole('button', { name: 'Registrar Permisos' }).click();

    const modalRegistro = page.locator('#modalPermisos');
    await expect(modalRegistro).toBeVisible();
    await expect(modalRegistro.locator('select[name="cod_rol"]')).toBeVisible();
    await expect(modalRegistro.locator('input[name="permisos"]')).not.toHaveCount(0);

    await modalRegistro.getByRole('button', { name: 'Cerrar' }).click();
    await expect(modalRegistro).toBeHidden();

    console.log('Modal Registrar Permisos abierto y cerrado correctamente');

    // BUSCAR PRIMER REGISTRO
    const primeraFila = tablaPermisos.locator('tbody tr').first();
    await expect(primeraFila).toBeVisible();

    // EDITAR PERMISOS
    await primeraFila.locator('.btn-editar').click();

    const modalEditar = page.locator('#modalEditar');
    await expect(modalEditar).toBeVisible();
    await expect(page.locator('#edit_cedula')).not.toHaveValue('');
    await expect(page.locator('#edit_nombr')).not.toHaveValue('');
    await expect(page.locator('#edit_rol_visual')).toBeVisible();
    await expect(page.locator('#edit_status')).toBeVisible();
    await expect(modalEditar.locator('.permiso-check')).not.toHaveCount(0);

    await modalEditar.getByRole('button', { name: 'Cerrar' }).click();
    await expect(modalEditar).toBeHidden();


    // ELIMINAR PERMISOS
    await primeraFila.locator('.btn-eliminar').click();

    const modalEliminar = page.locator('#modalEliminar');
    await expect(modalEliminar).toBeVisible();
    await expect(page.locator('#cedulaEliminar')).not.toBeEmpty();
    await expect(page.locator('#nombreEliminar')).not.toBeEmpty();
    await expect(page.locator('#rolEliminar')).not.toBeEmpty();

    await modalEliminar.getByRole('button', { name: 'Cancelar' }).click();
    await expect(modalEliminar).toBeHidden();

});
