
import { test, expect } from '@playwright/test';


test('humo completo del módulo Especialistas', async ({ page }) => {

    test.setTimeout(60000);

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

    // Acceder al módulo Especialistas.
    const enlaceEspecialistas = page.locator(
        '#menuConfiguracion .submenu a.submenu-link[href="/admin?ruta=especialidad"]'
    );

    await expect(enlaceEspecialistas).toBeVisible();
    await expect(enlaceEspecialistas).toBeEnabled();
    await enlaceEspecialistas.click();

    console.log('Acceso al módulo Especialistas');

    // Comprobar que cargó el módulo y su tabla.
    await expect(page.locator('#table1')).toBeVisible({
        timeout: 15000
    });

    // Abrir y cerrar modal de registro.
    await page.getByRole('button', { name: 'Registrar Especialista' }).click();

    const modalRegistro = page.locator('#primary');
    await expect(modalRegistro).toBeVisible();

    await expect(modalRegistro.locator('#especialista')).toBeVisible();
    await expect(modalRegistro.locator('#searchCedula')).toBeVisible();

    // Cerrar sin registrar el especialista.
    await modalRegistro.getByRole('button', { name: 'Cerrar' }).click();
    await expect(modalRegistro).toBeHidden();

    await expect(page.locator('.modal-backdrop')).toHaveCount(0);

    // Abrir y cerrar modal de edición del primer especialista.
    const botonEditar = page.locator('#table1 .btn-editar').first();

    await expect(botonEditar).toBeVisible();
    await botonEditar.click();

    const modalEditar = page.locator('#editModal');
    await expect(modalEditar).toBeVisible();

    // Comprobar los campos del modal.
    await expect(modalEditar.locator('#edit_especialista')).toBeVisible();
    await expect(modalEditar.locator('#edit_cedula')).toBeVisible();
    await expect(modalEditar.locator('#edit_estado')).toBeVisible();

    await expect(modalEditar.locator('#edit_especialista')).toBeEnabled();
    await expect(modalEditar.locator('#edit_cedula')).toBeEnabled();
    await expect(modalEditar.locator('#edit_estado')).toBeEnabled();

    // Cerrar sin modificar.
    await modalEditar.getByRole('button', { name: 'Cerrar' }).click();
    await expect(modalEditar).toBeHidden();

    await expect(page.locator('.modal-backdrop')).toHaveCount(0);

    console.log('Modal de edición abierto y cerrado');

    // Abrir y cerrar modal de eliminación del primer especialista.
    const botonEliminar = page.locator('#table1 .btn-eliminar').first();

    await expect(botonEliminar).toBeVisible();
    await botonEliminar.click();

    const modalEliminar = page.locator('#deleteModal');
    await expect(modalEliminar).toBeVisible();

    // Comprobar el contenido del modal.
    await expect(
        modalEliminar.getByRole('heading', { name: 'Confirmar Eliminación' })
    ).toBeVisible();

    await expect(modalEliminar.locator('#nombreEliminar')).toBeVisible();

    await expect(
        modalEliminar.getByRole('button', { name: 'No' })
    ).toBeVisible();

    await expect(
        modalEliminar.getByRole('button', { name: 'Eliminar' })
    ).toBeVisible();

    // Cerrar sin eliminar.
    await modalEliminar.getByRole('button', { name: 'No' }).click();
    await expect(modalEliminar).toBeHidden();

    console.log('Prueba de humo completa del módulo Especialistas finalizada');
});




test('humo del módulo de especialistas modal registro', async ({ page }) => {
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

    // Acceder al módulo Especialistas.
    await page.locator('#menuConfiguracion > a.sidebar-link').click();

    const enlaceEspecialistas = page.locator(
        '#menuConfiguracion .submenu a.submenu-link[href="/admin?ruta=especialidad"]'
    );

    await expect(enlaceEspecialistas).toBeVisible();
    await expect(enlaceEspecialistas).toBeEnabled();
    await enlaceEspecialistas.click();


    // Comprobar que se cargó la tabla.
    await expect(page.locator('#table1')).toBeVisible({
        timeout: 15000
    });

    // Abrir modal de registro.
    await page.getByRole('button', { name: 'Registrar Especialista' }).click();

    const modalRegistro = page.locator('#primary');
    await expect(modalRegistro).toBeVisible();

    // Seleccionar especialidad.
    await page.locator('#especialista').selectOption('Ayudante');

    // Buscar cédula del personal.
    await page.locator('#searchCedula').fill('76456336');

    const cedulaPersonal = page.locator('#cedula_reg');

    await expect(cedulaPersonal).toBeVisible();
    await cedulaPersonal.selectOption('76456336');

    // Comprobar los datos seleccionados.
    await expect(page.locator('#especialista')).toHaveValue('Ayudante');
    await expect(cedulaPersonal).toHaveValue('76456336');

    // Cerrar sin registrar el especialista.
    await modalRegistro.getByRole('button', { name: 'Cerrar' }).click();
    await expect(modalRegistro).toBeHidden();

    console.log('Prueba de humo del módulo Especialistas modal registro finalizada');
});


test('humo del módulo de especialistas modal editar', async ({ page }) => {
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

    // Acceder al menú Configuración.
    await page.locator('#menuConfiguracion > a.sidebar-link').click();

    // Acceder al módulo Especialistas.
    const enlaceEspecialistas = page.locator(
        '#menuConfiguracion .submenu a.submenu-link[href="/admin?ruta=especialidad"]'
    );

    await expect(enlaceEspecialistas).toBeVisible();
    await expect(enlaceEspecialistas).toBeEnabled();
    await enlaceEspecialistas.click();

    console.log('Acceso al módulo Especialistas');

    // Comprobar que se cargó la tabla.
    await expect(page.locator('#table1')).toBeVisible({
        timeout: 15000
    });

    // Seleccionar el primer especialista de la tabla.
    const botonEditar = page.locator('#table1 .btn-editar').first();

    await expect(botonEditar).toBeVisible();
    await botonEditar.click();

    // Comprobar que se abrió el modal de edición.
    const modalEditar = page.locator('#editModal');
    await expect(modalEditar).toBeVisible();

    // Comprobar los campos del modal.
    await expect(page.locator('#edit_especialista')).toBeVisible();
    await expect(page.locator('#edit_cedula')).toBeVisible();
    await expect(page.locator('#edit_estado')).toBeVisible();

    // Comprobar que los campos permiten interactuar.
    await expect(page.locator('#edit_especialista')).toBeEnabled();
    await expect(page.locator('#edit_cedula')).toBeEnabled();
    await expect(page.locator('#edit_estado')).toBeEnabled();

    // Cerrar sin modificar el especialista.
    await modalEditar.getByRole('button', { name: 'Cerrar' }).click();
    await expect(modalEditar).toBeHidden();

    console.log('Prueba de humo del módulo Especialistas modal editar finalizada');
});



test('humo del módulo de especialistas modal eliminar', async ({ page }) => {
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

    // Acceder al menú Configuración.
    await page.locator('#menuConfiguracion > a.sidebar-link').click();

    // Acceder al módulo Especialistas.
    const enlaceEspecialistas = page.locator(
        '#menuConfiguracion .submenu a.submenu-link[href="/admin?ruta=especialidad"]'
    );

    await expect(enlaceEspecialistas).toBeVisible();
    await expect(enlaceEspecialistas).toBeEnabled();
    await enlaceEspecialistas.click();


    // Comprobar que se cargó la tabla.
    await expect(page.locator('#table1')).toBeVisible({
        timeout: 15000
    });

    // Seleccionar el primer especialista de la tabla.
    const botonEliminar = page.locator('#table1 .btn-eliminar').first();

    await expect(botonEliminar).toBeVisible();
    await botonEliminar.click();

    // Comprobar que se abrió el modal.
    const modalEliminar = page.locator('#deleteModal');
    await expect(modalEliminar).toBeVisible();

    // Comprobar el título y mensaje de confirmación.
    await expect(
        modalEliminar.getByRole('heading', { name: 'Confirmar Eliminación' })
    ).toBeVisible();

    await expect(
        modalEliminar.locator('#nombreEliminar')
    ).toBeVisible();

    // Comprobar los botones.
    await expect(
        modalEliminar.getByRole('button', { name: 'No' })
    ).toBeVisible();

    await expect(
        modalEliminar.getByRole('button', { name: 'Eliminar' })
    ).toBeVisible();

    // Cerrar sin eliminar el especialista.
    await modalEliminar.getByRole('button', { name: 'No' }).click();
    await expect(modalEliminar).toBeHidden();

    console.log('Prueba de humo del módulo Especialistas modal eliminar finalizada');
});