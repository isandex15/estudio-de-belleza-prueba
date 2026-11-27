// @ts-check
import { expect, test } from '@playwright/test';
import {
  assertInputInvalido,
  abrirModuloAdmin,
  buscarFila,
  confirmarAlerta,
  eliminarFila,
  fechaRelativa,
  filaPorTexto,
  nombreDePrueba,
} from './admin-test-support';

const titulo = 'Promociones';
const modalEliminar = '#modalEliminarPromocion';
const botonEliminar = 'button[data-bs-target="#modalEliminarPromocion"]';

async function registrarPromocion(page: Parameters<typeof abrirModuloAdmin>[0], nombre: string) {
  await page.getByRole('button', { name: 'Registrar Promoción' }).click();
  await page.locator('#nombre_promo').fill(nombre);
  await page.locator('#descripcion_promo').fill('Promoción de prueba automatizada');
  await page.locator('#descuento').fill('15');
  await page.locator('#inicio_promo').fill(fechaRelativa(1));
  await page.locator('#fin_promo').fill(fechaRelativa(10));
  await page.locator('#formRegistrarPromocion button[type="submit"]').click();
  await confirmarAlerta(page);
  return filaPorTexto(page, nombre);
}

test('registrar promoción', async ({ page }) => {
  await abrirModuloAdmin(page, 'promocion', titulo);
  const nombre = nombreDePrueba('Promo');
  const fila = await registrarPromocion(page, nombre);
  await expect(fila).toContainText(nombre);
  await eliminarFila(page, fila, botonEliminar, modalEliminar, '#formEliminarPromocion button[type="submit"]');
});

test('editar promoción', async ({ page }) => {
  await abrirModuloAdmin(page, 'promocion', titulo);
  const nombreOriginal = nombreDePrueba('Promo');
  const nombreEditado = nombreDePrueba('EditPromo');
  const filaOriginal = await registrarPromocion(page, nombreOriginal);

  await filaOriginal.locator('button[data-bs-target="#modalEditarPromocion"]').click();
  await expect(page.locator('#modalEditarPromocion')).toBeVisible();
  await page.locator('#edit_nombre_promo').fill(nombreEditado);
  await page.locator('#edit_descuento').fill('20');
  await page.locator('#edit_inicio_promo').fill(fechaRelativa(1));
  await page.locator('#edit_fin_promo').fill(fechaRelativa(10));
  await page.locator('#formEditarPromocion button[type="submit"]').click();
  await confirmarAlerta(page);

  const filaEditada = await filaPorTexto(page, nombreEditado);
  await eliminarFila(page, filaEditada, botonEliminar, modalEliminar, '#formEliminarPromocion button[type="submit"]');
});

test('consultar detalle de promoción', async ({ page }) => {
  await abrirModuloAdmin(page, 'promocion', titulo);
  const nombre = nombreDePrueba('Promo');
  const fila = await registrarPromocion(page, nombre);

  await fila.locator('button[data-bs-target="#modalVerPromocion"]').click();
  await expect(page.locator('#modalVerPromocion')).toBeVisible();
  await expect(page.locator('#nombre_promocion')).toHaveText(nombre);
  await page.locator('#modalVerPromocion').getByRole('button', { name: 'Cerrar' }).click();
  await expect(page.locator('#modalVerPromocion')).toBeHidden();

  await eliminarFila(page, fila, botonEliminar, modalEliminar, '#formEliminarPromocion button[type="submit"]');
});

test('eliminar promoción', async ({ page }) => {
  await abrirModuloAdmin(page, 'promocion', titulo);
  const nombre = nombreDePrueba('Promo');
  const fila = await registrarPromocion(page, nombre);
  await eliminarFila(page, fila, botonEliminar, modalEliminar, '#formEliminarPromocion button[type="submit"]');
});

test('buscar promoción', async ({ page }) => {
  await abrirModuloAdmin(page, 'promocion', titulo);
  const nombre = nombreDePrueba('Promo');
  const fila = await registrarPromocion(page, nombre);
  const filaEncontrada = await buscarFila(page, nombre);
  await expect(filaEncontrada).toContainText(nombre);
  await eliminarFila(page, fila, botonEliminar, modalEliminar, '#formEliminarPromocion button[type="submit"]');
});

test('validar los campos del formulario de promoción', async ({ page }) => {
  await abrirModuloAdmin(page, 'promocion', titulo);
  await page.getByRole('button', { name: 'Registrar Promoción' }).click();

  const nombre = page.locator('#nombre_promo');
  await nombre.fill('Promo@');
  await assertInputInvalido(page, '#nombre_promo');

  const descuento = page.locator('#descuento');
  await descuento.fill('101');
  await assertInputInvalido(page, '#descuento');

  await page.locator('#inicio_promo').fill(fechaRelativa(5));
  await page.locator('#fin_promo').fill(fechaRelativa(2));
  await assertInputInvalido(page, '#fin_promo');
  await page.locator('#formRegistrarPromocion button[type="submit"]').click();

  await expect(page.locator('#modalRegistrarPromocion')).toBeVisible();
});