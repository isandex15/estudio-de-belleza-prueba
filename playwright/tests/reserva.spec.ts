
import { test, expect } from '@playwright/test';

test('registrar reserva desde Inicio', async ({ page }) => {
    // 1. Iniciar sesión
    await page.goto('http://localhost:5000/admin?ruta=login');

    await page.getByRole('textbox', { name: 'Cédula' }).fill('4723317');
    await page.locator('#login-password').fill('admin123');

    await page.locator('#pow-check').click();
    await expect(page.locator('#pow-image')).toBeVisible();
    await page.locator('#pow-answer').fill('AB12CD');
    await page.locator('#pow-verify').click();
    await page.locator('#loginButton').click();

    // 2. Esperar el calendario sin utilizar el menú lateral
    await expect(page.locator('#calendar')).toBeVisible({
        timeout: 15000
    });

    // 3. Obtener la fecha actual
    const hoy = new Date();
    const fechaActual = [
        hoy.getFullYear(),
        String(hoy.getMonth() + 1).padStart(2, '0'),
        String(hoy.getDate()).padStart(2, '0')
    ].join('-');

    // 4. Seleccionar la casilla del día actual
    const casillaHoy = page.locator(
        `.fc-daygrid-day[data-date="${fechaActual}"]`
    );

    await expect(casillaHoy).toBeVisible();
    await casillaHoy.click();

    // 5. Verificar que se abrió el modal y se completó la fecha
    const modal = page.locator('#modalRegistrar');
    await expect(modal).toBeVisible();

    await expect(page.locator('#fecha_reserva'))
        .toHaveValue(fechaActual);

    // 6. Escribir el nombre del cliente
    await page.locator('#nombre_usuario').fill('alezanbra');

    // 7. Seleccionar al cliente de la lista
    const cliente = page.locator('.cliente-item').filter({
        hasText: 'alezanbra ttorres'
    });

    await expect(cliente).toBeVisible({ timeout: 10000 });
    await cliente.click();

    // 8. Verificar el nombre y la cédula autocompletados
    await expect(page.locator('#nombre_usuario'))
        .toHaveValue('alezanbra ttorres');

    await expect(page.locator('#cedula'))
        .toHaveValue('65434567');

    // 9. Introducir la hora de la reserva
    await page.locator('#hora_reserva').fill('10:00 AM');

    // 10. Seleccionar el servicio código 7
    await page.locator('#servicio_7').check();

    await expect(page.locator('#servicio_7')).toBeChecked();

    // 11. Seleccionar a la manicurista por su nombre
    await page.locator('#manicurista').selectOption({
        label: 'alonadra martinez'
    });

    // Verificar que corresponde a la cédula indicada
    await expect(page.locator('#manicurista'))
        .toHaveValue('76456336');

    // 12. Seleccionar el producto código 7
    await page.locator('#producto_7').check();

    // 13. Colocar una unidad del producto, porque el stock es 1
    const cantidadProducto = page.locator(
        'input[name="cantidad_producto[7]"]'
    );

    await cantidadProducto.fill('1');

    await expect(cantidadProducto).toHaveValue('1');

    // 14. Verificar que el botón Guardar esté habilitado
    const botonGuardar = modal.getByRole('button', {
        name: 'Guardar'
    });

    await expect(botonGuardar).toBeEnabled();

    // 15. Guardar la reserva
    await botonGuardar.click();

    // 16. Verificar el mensaje de éxito
    await expect(
        page.getByText('La reserva se registró correctamente.')
    ).toBeVisible({ timeout: 15000 });
});





test('reservar', async ({ page }) => {
    // 1. Iniciar sesión
    await page.goto('http://localhost:5000/admin?ruta=login');

    await page.getByRole('textbox', { name: 'Cédula' }).fill('4723317');
    await page.locator('#login-password').fill('admin123');

    await page.locator('#pow-check').click();
    await expect(page.locator('#pow-image')).toBeVisible();
    await page.locator('#pow-answer').fill('AB12CD');
    await page.locator('#pow-verify').click();
    await page.locator('#loginButton').click();

    // 2. Esperar el calendario.
    const calendario = page.locator('#calendar');
    await expect(calendario).toBeVisible({ timeout: 15000 });

    // 3. Obtener la fecha actual.
    const hoy = new Date();
    const fechaActual = [
        hoy.getFullYear(),
        String(hoy.getMonth() + 1).padStart(2, '0'),
        String(hoy.getDate()).padStart(2, '0')
    ].join('-');

    // 4. Seleccionar la casilla del día actual.
    const casillaHoy = calendario.locator(
        `.fc-daygrid-day[data-date="${fechaActual}"]`
    );

    await expect(casillaHoy).toBeVisible({ timeout: 10000 });
    await casillaHoy.locator('.fc-daygrid-day-number').click();

    // 5. Verificar que se abrió el formulario.
    const modal = page.locator('#modalRegistrar');
    await expect(modal).toBeVisible({ timeout: 10000 });

    // 6. Comprobar que los campos estén visibles.
    await expect(modal.locator('#fecha_reserva')).toBeVisible();
    await expect(modal.locator('#nombre_usuario')).toBeVisible();
    await expect(modal.locator('#cedula')).toBeVisible();
    await expect(modal.locator('#hora_reserva')).toBeVisible();
    await expect(modal.locator('#manicurista')).toBeVisible();

    // 7. Comprobar que el botón Guardar esté disponible, sin pulsarlo.
    const botonGuardar = modal.getByRole('button', {
        name: 'Guardar'
    });

    await expect(botonGuardar).toBeVisible();
    await expect(botonGuardar).toBeEnabled();



    // 8. Cerrar el formulario sin registrar.
    const botonCerrar = modal.locator('button[data-bs-dismiss="modal"]');

    await expect(botonCerrar.first()).toBeVisible();
    await botonCerrar.first().click();

    // 9. Comprobar que el modal se haya cerrado.
    await expect(modal).toBeHidden({ timeout: 10000 });

    console.log('Prueba de interfaz de reserva finalizada');
});



test('CP-RES-03 - impedir registrar reserva con cantidad de producto igual a cero', async ({ page }) => {

    await page.goto('http://localhost:5000/admin?ruta=login');

    await page.getByRole('textbox', { name: 'Cédula' }).fill('4723317');
    await page.locator('#login-password').fill('admin123');
    await page.locator('#pow-check').click();
    await page.locator('#pow-answer').fill('AB12CD');
    await page.locator('#pow-verify').click();
    await page.locator('#loginButton').click();

    await expect(page.locator('#calendar')).toBeVisible({ timeout: 15000 });

    const hoy = new Date();
    const fecha = `${hoy.getFullYear()}-${String(hoy.getMonth() + 1).padStart(2, '0')}-${String(hoy.getDate()).padStart(2, '0')}`;

    await page.locator(`.fc-daygrid-day[data-date="${fecha}"]`).click();

    const modal = page.locator('#modalRegistrar');
    await expect(modal).toBeVisible();

    await page.locator('#nombre_usuario').fill('alezanbra');
    await page.locator('.cliente-item').filter({ hasText: 'alezanbra ttorres' }).click();

    await page.locator('#hora_reserva').fill('10:00 AM');
    await page.locator('#servicio_7').check();
    await page.locator('#manicurista').selectOption('76456336');
    await page.locator('#producto_7').check();

    const cantidad = page.locator('input[name="cantidad_producto[7]"]');
    await cantidad.fill('0');

    await expect(cantidad).toHaveValue('1');
    await expect(cantidad).toHaveClass(/is-invalid/);
    await expect(
        cantidad.locator('xpath=..').locator('.mensaje-stock')
    ).toContainText('mayor que 0');
    const guardar = modal.getByRole('button', { name: 'Guardar' });
    await guardar.click();

    await expect(modal).toBeVisible();
    await expect(guardar).toBeEnabled();

});
