import { expect, test } from '@playwright/test';
import {
  abrirModuloAdmin,
  confirmarAlerta,
  eliminarFila,
  fechaRelativa,
  filaPorTexto,
  nombreDePrueba,
} from '../admin-test-support';

test('humo del módulo de promociones', async ({ page }) => {
  await abrirModuloAdmin(page, 'promocion', 'Promociones');

  await expect(page.locator('#table1 thead')).toContainText('Código');
  await expect(page.locator('#table1 thead')).toContainText('Nombre');

  const nombre = nombreDePrueba('Promo');
  await page.getByRole('button', { name: 'Registrar Promoción' }).click();

  const modal = page.locator('#modalRegistrarPromocion');
  await expect(modal).toBeVisible();
  await page.locator('#nombre_promo').fill(nombre);
  await page.locator('#descripcion_promo').fill('Promocion de prueba automatizada');
  await page.locator('#descuento').fill('15');
  await page.locator('#inicio_promo').fill(fechaRelativa(1));
  await page.locator('#fin_promo').fill(fechaRelativa(10));
  await page.locator('#formRegistrarPromocion button[type="submit"]').click();
  await confirmarAlerta(page);

  const fila = await filaPorTexto(page, nombre);
  await eliminarFila(
    page,
    fila,
    'button[data-bs-target="#modalEliminarPromocion"]',
    '#modalEliminarPromocion',
    '#formEliminarPromocion button[type="submit"]',
  );
});
