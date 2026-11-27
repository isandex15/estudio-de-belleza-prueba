import { expect, test } from '@playwright/test';
import {
  abrirModuloAdmin,
  confirmarAlerta,
  eliminarFila,
  filaPorTexto,
  nombreDePrueba,
} from '../admin-test-support';

test('humo del módulo de tipos de servicio', async ({ page }) => {
  await abrirModuloAdmin(page, 'tiposervicio', 'Tipos de servicios');

  await expect(page.locator('#table1 thead')).toContainText('Código');
  await expect(page.locator('#table1 thead')).toContainText('Nombre');

  const nombre = nombreDePrueba('Servicio');
  await page.getByRole('button', { name: 'Registrar tipo de servicio' }).click();

  const modal = page.locator('#primary');
  await expect(modal).toBeVisible();
  await page.locator('#nombre_servicio').fill(nombre);
  await page.locator('#precio').fill('99.50');
  await page.locator('#formRegistrartiposservicios button[type="submit"]').click();
  await confirmarAlerta(page);

  const fila = await filaPorTexto(page, nombre);
  await eliminarFila(
    page,
    fila,
    'button[data-bs-target="#modalEliminartiposervicio"]',
    '#modalEliminartiposervicio',
    '#formEliminartiposervicio button[type="submit"]',
  );
});
