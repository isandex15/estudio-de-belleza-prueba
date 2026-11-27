
import { test, expect } from '@playwright/test';

test('Navegación por la página web', async ({ page }) => {

    await page.goto('http://127.0.0.1:5000');

    // Verificar que la página cargue
    await expect(page).toHaveTitle(/.*/);

});

test.use({
    screenshot: 'only-on-failure'
});
test('Navegación por dos botones  de la página web', async ({ page }) => {
    await page.goto('http://127.0.0.1:5000', {
        waitUntil: 'networkidle'
    });

    await expect(page).toHaveTitle(/.*/);
    await page.waitForTimeout(2000);

    // Navegar a Nosotros
    await page.getByRole('link', { name: 'Nosotros', exact: true }).click();
    await page.waitForLoadState('networkidle');
    await expect(page).toHaveURL(/quienesomos/);
    await expect(page.locator('body')).toBeVisible();
    await page.waitForTimeout(3000);

    // Navegar a Servicios
    await page.getByRole('link', { name: 'Servicios', exact: true }).first().click();
    await page.waitForLoadState('networkidle');
    await expect(page).toHaveURL(/servicios/);
    await expect(page.locator('body')).toBeVisible();
    await page.waitForTimeout(3000);
});


test('Navegación por todas las opciones del menú principal', async ({ page }) => {
    test.setTimeout(60000);

    await page.setViewportSize({ width: 1366, height: 768 });

    await page.goto('http://127.0.0.1:5000');
    await page.waitForTimeout(2500);

    // Nosotros
    await page.locator('nav.navbar a[href="/quienesomos"]').click();
    await expect(page).toHaveURL(/quienesomos/);
    await page.waitForTimeout(3000);

    // Servicios
    await page.locator('nav.navbar a[href="/servicios"]').click();
    await expect(page).toHaveURL(/servicios/);
    await page.waitForTimeout(3000);

    // Promociones
    await page.locator('nav.navbar a[href="/promociones"]').click();
    await expect(page).toHaveURL(/promociones/);
    await page.waitForTimeout(3000);

    // Iniciar sesión
    await page.locator('nav.navbar a[href="/acceder"]').click();
    await expect(page).toHaveURL(/admin\?ruta=login/);
    await page.waitForTimeout(3000);

    // Regresar al inicio mediante el logo
    await page.goto('http://127.0.0.1:5000');
    await expect(page).toHaveURL('http://127.0.0.1:5000/');
    await page.waitForTimeout(3000);
});



test('Navegación por las secciones y botones de la página principal', async ({ page }) => {
    test.setTimeout(180000);

    await page.setViewportSize({ width: 1366, height: 768 });

    const inicio = 'http://127.0.0.1:5000/';

    // Cargar página principal
    await page.goto(inicio, { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(3000);

    // Desactivar animaciones
    await page.addStyleTag({
        content: `
            *, *::before, *::after {
                animation: none !important;
                transition: none !important;
                scroll-behavior: auto !important;
            }
        `
    });

    // 1. Abrir Asesor de Imagen IA
    const btnIA = page.locator('#btnAsesorIA');

    await expect(btnIA).toBeVisible();
    await btnIA.dispatchEvent('click');
    await expect(page.locator('#iaChat')).toBeVisible();
    await page.waitForTimeout(3000);

    // Cerrar Asesor de Imagen IA
    await page.locator('#cerrarIA').click();
    await expect(page.locator('#iaChat')).toBeHidden();
    await page.waitForTimeout(2000);

    // 2. Ver servicios desde el inicio
    await page.locator('section.hero .hero-botones a.btn-light').click();
    await expect(page).toHaveURL(/\/servicios/);
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(4000);

    // Regresar a Inicio
    await page.goto(inicio, { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(3000);

    // 3. Reservar cita desde el inicio
    await page.locator('section.hero .hero-botones a.btn-outline-light').click();
    await expect(page).toHaveURL(/admin\?ruta=login/);
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(4000);

    // Regresar a Inicio
    await page.goto(inicio, { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(3000);

    // 4. Bajar a la sección Nuestros servicios
    const seccionServicios = page.locator('section.servicios-seccion');

    await seccionServicios.evaluate(element => {
        element.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await page.waitForTimeout(3000);

    // Pulsar un solo botón Conocer más
    await page.locator('section.servicios-seccion .card-servicio a.btn-servicio').first().click();
    await expect(page).toHaveURL(/\/servicios/);
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(4000);

    // Regresar a Inicio
    await page.goto(inicio, { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(3000);

    // 5. Bajar a la sección Quiénes somos
    const seccionNosotros = page.locator('section.nosotros-seccion');

    await seccionNosotros.evaluate(element => {
        element.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await page.waitForTimeout(3000);

    // Pulsar Conoce más sobre nosotros
    await page.locator('section.nosotros-seccion a.btn-nosotros').click();
    await expect(page).toHaveURL(/\/quienesomos/);
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(4000);

    // Regresar a Inicio
    await page.goto(inicio, { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(3000);

    // 6. Bajar a la sección Reserva Online
    const seccionReserva = page.locator('section.reserva-banner');

    await seccionReserva.evaluate(element => {
        element.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await page.waitForTimeout(3000);

    // Pulsar Reservar ahora
    await page.locator('section.reserva-banner a.btn-reserva').click();
    await expect(page).toHaveURL(/admin\?ruta=login/);
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(4000);
});
