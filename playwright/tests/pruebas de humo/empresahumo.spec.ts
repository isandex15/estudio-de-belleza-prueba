
import { test, expect } from '@playwright/test';



test('humo del módulo de empresa ', async ({ page }) => {

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

    // Acceder al módulo Empresa.
    const enlaceEmpresa = page.locator(
        '#menuConfiguracion .submenu a.submenu-link[href="/admin?ruta=empresa"]'
    );

    await expect(enlaceEmpresa).toBeVisible();
    await enlaceEmpresa.click();

    // Verificar contenido de Empresa.
    const contenedorEmpresa = page.locator('#contenedorEmpresas');
    await expect(contenedorEmpresa).toBeVisible();

    // Abrir modal de edición.
    const botonEditar = contenedorEmpresa.locator(
        'button[data-bs-target="#exampleModal"]'
    );

    await expect(botonEditar).toBeVisible();
    await botonEditar.click();

    const modalEditar = page.locator('#exampleModal');

    await expect(modalEditar).toBeVisible();

    await expect(
        modalEditar.getByRole('heading', { name: 'Editar Empresa' })
    ).toBeVisible();

    // Verificar formulario.
    await expect(modalEditar.locator('#editar')).toBeVisible();

    // Verificar campos del formulario.
    await expect(modalEditar.locator('#nombre')).toBeVisible();
    await expect(modalEditar.locator('#direccion')).toBeVisible();
    await expect(modalEditar.locator('#telefono')).toBeVisible();
    await expect(modalEditar.locator('#email')).toBeVisible();
    await expect(modalEditar.locator('#descripcion_empresa')).toBeVisible();
    await expect(modalEditar.locator('#logo')).toBeVisible();

    // Verificar que los campos obligatorios estén configurados.
    await expect(modalEditar.locator('#nombre')).toHaveAttribute('required', '');
    await expect(modalEditar.locator('#direccion')).toHaveAttribute('required', '');
    await expect(modalEditar.locator('#telefono')).toHaveAttribute('required', '');
    await expect(modalEditar.locator('#email')).toHaveAttribute('required', '');
    await expect(modalEditar.locator('#descripcion_empresa')).toHaveAttribute('required', '');

    // Verificar elemento de vista previa del logo.
    await expect(modalEditar.locator('#previewLogo')).toBeAttached();

    // Cerrar modal de edición.
    await modalEditar.getByRole('button', { name: 'Cerrar' }).click();

    await expect(modalEditar).toBeHidden();

    console.log('Prueba de humo del módulo Empresa completada');

});
