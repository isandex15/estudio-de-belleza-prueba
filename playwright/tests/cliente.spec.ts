
// @ts-check
import { test, expect } from '@playwright/test';

test('registrar cliente', async ({ page }) => {
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

    // Comprueba que el CAPTCHA haya sido aceptado.
    await page.locator('#loginButton').click();
    console.log('Botón de acceso clickeado');

    console.log('URL actual:', page.url());

    // Espera a que aparezca el menú después del acceso.
    await expect(page.locator('.sidebar-menu')).toBeVisible({
        timeout: 15000
    });

    console.log('Inicio de sesión confirmado: menú visible');

    //   el enlace del módulo Clientes exista y esté habilitado.
    const enlaceClientes = page.locator(
        '.sidebar-menu a.sidebar-link[href="/admin?ruta=cliente"]'
    );

    await expect(enlaceClientes).toBeVisible();
    await expect(enlaceClientes).toBeEnabled();

    // Accede al módulo Clientes.
    await enlaceClientes.click();

    console.log('Acceso al módulo Clientes');

    // Abre el formulario de registro.
    await page.getByRole('button', { name: 'Registrar Clientes' }).click();

    await expect(page.locator('#modalRegistrarCliente')).toBeVisible();

    console.log('Formulario Registrar Cliente abierto');

    // Completar los datos del cliente.
    await page.locator('#cedula_reg').fill('3196486');
    await page.locator('#nombre_usuario_reg').fill('Carlos');
    await page.locator('#apellido_usuario_reg').fill('Gonzalez');
    await page.locator('#telefono_reg').fill('0412123456');
    await page.locator('#direccion_reg').fill('Av Principal 123');
    await page.locator('#correo_reg').fill('carlogonzalez@gmail.com');

    console.log('Datos del cliente completados');

    // Guarda el registro
    await page.getByRole('button', { name: 'Guardar' }).click();

    console.log('Botón Guardar clickeado');
});




test('editar cliente', async ({ page }) => {
    await page.goto('http://localhost:5000/admin?ruta=login');

    await page.getByRole('textbox', { name: 'Cédula' }).fill('4723317');
    await page.locator('#login-password').fill('admin123');

    await page.locator('#pow-check').click();
    await expect(page.locator('#pow-image')).toBeVisible();

    await page.locator('#pow-answer').fill('AB12CD');
    await page.locator('#pow-verify').click();

    await page.locator('#loginButton').click();

    // Espera a que aparezca el menú después del acceso.
    await expect(page.locator('.sidebar-menu')).toBeVisible({
        timeout: 15000
    });

    console.log('Sesión iniciada correctamente');

    const enlaceClientes = page.locator(
        '.sidebar-menu a.sidebar-link[href="/admin?ruta=cliente"]'
    );

    await enlaceClientes.click();

    await expect(page.locator('#table1')).toBeVisible();

    const filaCliente = page.locator('#table1 tbody tr').filter({
        has: page.locator('td').filter({
            hasText: /^\s*3196486\s*$/
        })
    });

    await expect(filaCliente).toHaveCount(1);

    console.log('Cliente 3196486 encontrado');

    const botonEditar = filaCliente.locator('button.btn-editar');
    const modal = page.locator('#modalEditar');

    await botonEditar.click();
    await expect(modal).toBeVisible();

    await expect(page.locator('#cedula_edit')).toHaveValue('3196486');

    await page.locator('#nombre_usuario_edit').fill('Car');
    await page.locator('#apellido_usuario_edit').fill('González');
    await page.locator('#telefono_edit').fill('0414123488');
    await page.locator('#direccion_edit').fill('barquisimeto ');
    await page.locator('#correo_edit').fill('carolinaactualizado@gmail.com');
    await page.locator('#status_edit').selectOption('1');

    console.log('Datos de edición completados');

    await modal.getByRole('button', { name: 'Editar' }).click();

    console.log('Botón Editar clickeado');

    await expect(modal).toBeHidden();

    console.log('Modal cerrado después de guardar');
});
