// @ts-check
import { expect, test } from '@playwright/test';
import {
  assertInputInvalido,
  abrirModuloAdmin,
  buscarFila,
  confirmarAlerta,
  eliminarFila,
  filaPorTexto,
  nombreDePrueba,
} from './admin-test-support';

const titulo = 'Tipos de servicios';
const modalEliminar = '#modalEliminartiposervicio';
const botonEliminar = 'button[data-bs-target="#modalEliminartiposervicio"]';

async function registrarTipoServicio(page: Parameters<typeof abrirModuloAdmin>[0], nombre: string) {
  await page.getByRole('button', { name: 'Registrar tipo de servicio' }).click();
  await page.locator('#nombre_servicio').fill(nombre);
  await page.locator('#precio').fill('99.50');
  await page.locator('#formRegistrartiposservicios button[type="submit"]').click();
  await confirmarAlerta(page);
  return filaPorTexto(page, nombre);
}

test('registrar tipo de servicio', async ({ page }) => {
  await abrirModuloAdmin(page, 'tiposervicio', titulo);
  const nombre = nombreDePrueba('Servicio');
  const fila = await registrarTipoServicio(page, nombre);
  await expect(fila).toContainText(nombre);
  await eliminarFila(page, fila, botonEliminar, modalEliminar, '#formEliminartiposervicio button[type="submit"]');
});

test('editar tipo de servicio', async ({ page }) => {
  await abrirModuloAdmin(page, 'tiposervicio', titulo);
  const nombreOriginal = nombreDePrueba('Servicio');
  const nombreEditado = nombreDePrueba('Editado');
  const filaOriginal = await registrarTipoServicio(page, nombreOriginal);

  await filaOriginal.locator('button[data-bs-target="#modalEditar"]').click();
  await expect(page.locator('#modalEditar')).toBeVisible();
  await page.locator('#edit_nombre_servicio').fill(nombreEditado);
  await page.locator('#edit_precio').fill('109.50');
  await page.locator('#formEditarTiposervicio button[type="submit"]').click();
  await confirmarAlerta(page);

  const filaEditada = await filaPorTexto(page, nombreEditado);
  await eliminarFila(page, filaEditada, botonEliminar, modalEliminar, '#formEliminartiposervicio button[type="submit"]');
});

test('consultar tipos de servicio', async ({ page }) => {
  await abrirModuloAdmin(page, 'tiposervicio', titulo);
  const nombre = nombreDePrueba('Servicio');
  const fila = await registrarTipoServicio(page, nombre);

  await expect(page.locator('#table1 thead')).toContainText('Código');
  await expect(page.locator('#table1 thead')).toContainText('Precio');
  await expect(fila).toContainText(nombre);
  await eliminarFila(page, fila, botonEliminar, modalEliminar, '#formEliminartiposervicio button[type="submit"]');
});

test('eliminar tipo de servicio', async ({ page }) => {
  await abrirModuloAdmin(page, 'tiposervicio', titulo);
  const nombre = nombreDePrueba('Servicio');
  const fila = await registrarTipoServicio(page, nombre);
  await eliminarFila(page, fila, botonEliminar, modalEliminar, '#formEliminartiposervicio button[type="submit"]');
});

test('buscar tipo de servicio', async ({ page }) => {
  await abrirModuloAdmin(page, 'tiposervicio', titulo);
  const nombre = nombreDePrueba('Servicio');
  const fila = await registrarTipoServicio(page, nombre);
  const filaEncontrada = await buscarFila(page, nombre);
  await expect(filaEncontrada).toContainText(nombre);
  await eliminarFila(page, fila, botonEliminar, modalEliminar, '#formEliminartiposervicio button[type="submit"]');
});

test('validar los campos del formulario de tipo de servicio', async ({ page }) => {
  await abrirModuloAdmin(page, 'tiposervicio', titulo);
  await page.getByRole('button', { name: 'Registrar tipo de servicio' }).click();

  await expect(page.locator('#nombre_servicio:invalid')).toBeVisible();
  await expect(page.locator('#precio:invalid')).toBeVisible();
  await page.locator('#formRegistrartiposservicios button[type="submit"]').click();

  await page.locator('#nombre_servicio').fill('Servicio');
  const precio = page.locator('#precio');
  await precio.fill('abc');
  await assertInputInvalido(page, '#precio');
  await expect(page.locator('#primary')).toBeVisible();
});