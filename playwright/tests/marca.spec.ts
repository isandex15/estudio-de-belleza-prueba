// @ts-check
import { expect, test } from '@playwright/test';
import {
  abrirModuloAdmin,
  buscarFila,
  confirmarAlerta,
  eliminarFila,
  filaPorTexto,
  nombreDePrueba,
} from './admin-test-support';

const titulo = 'Marcas';
const modalEliminar = '#modalEliminar';
const botonEliminar = 'button[data-bs-target="#modalEliminar"]';

async function registrarMarca(page: Parameters<typeof abrirModuloAdmin>[0], nombre: string) {
  await page.getByRole('button', { name: 'Registrar marca' }).click();
  await page.locator('#nombre_marca').fill(nombre);
  await page.locator('#formRegistrarMarca button[type="submit"]').click();
  await confirmarAlerta(page);
  return filaPorTexto(page, nombre);
}

test('registrar marca', async ({ page }) => {
  await abrirModuloAdmin(page, 'marca', titulo);
  const nombre = nombreDePrueba('Marca');
  const fila = await registrarMarca(page, nombre);
  await expect(fila).toContainText(nombre);
  await eliminarFila(page, fila, botonEliminar, modalEliminar, '#formEliminarMarca button[type="submit"]');
});

test('editar marca', async ({ page }) => {
  await abrirModuloAdmin(page, 'marca', titulo);
  const nombreOriginal = nombreDePrueba('Marca');
  const nombreEditado = nombreDePrueba('Editada');
  const filaOriginal = await registrarMarca(page, nombreOriginal);

  await filaOriginal.locator('button[data-bs-target="#modalEditar"]').click();
  await expect(page.locator('#modalEditar')).toBeVisible();
  await page.locator('#edit_nombre_marca').fill(nombreEditado);
  await page.locator('#formEditarMarca button[type="submit"]').click();
  await confirmarAlerta(page);

  const filaEditada = await filaPorTexto(page, nombreEditado);
  await eliminarFila(page, filaEditada, botonEliminar, modalEliminar, '#formEliminarMarca button[type="submit"]');
});

test('consultar marcas', async ({ page }) => {
  await abrirModuloAdmin(page, 'marca', titulo);
  const nombre = nombreDePrueba('Marca');
  const fila = await registrarMarca(page, nombre);

  await expect(page.locator('#table1 thead')).toContainText('Código');
  await expect(page.locator('#table1 thead')).toContainText('Nombre');
  await expect(fila).toContainText(nombre);
  await eliminarFila(page, fila, botonEliminar, modalEliminar, '#formEliminarMarca button[type="submit"]');
});

test('eliminar marca', async ({ page }) => {
  await abrirModuloAdmin(page, 'marca', titulo);
  const nombre = nombreDePrueba('Marca');
  const fila = await registrarMarca(page, nombre);
  await eliminarFila(page, fila, botonEliminar, modalEliminar, '#formEliminarMarca button[type="submit"]');
});

test('buscar marca', async ({ page }) => {
  await abrirModuloAdmin(page, 'marca', titulo);
  const nombre = nombreDePrueba('Marca');
  const fila = await registrarMarca(page, nombre);
  const filaEncontrada = await buscarFila(page, nombre);
  await expect(filaEncontrada).toContainText(nombre);
  await eliminarFila(page, fila, botonEliminar, modalEliminar, '#formEliminarMarca button[type="submit"]');
});

test('validar los campos del formulario de marca', async ({ page }) => {
  await abrirModuloAdmin(page, 'marca', titulo);
  await page.getByRole('button', { name: 'Registrar marca' }).click();

  const nombre = page.locator('#nombre_marca');
  await expect(page.locator('#nombre_marca:invalid')).toBeVisible();
  await page.locator('#formRegistrarMarca button[type="submit"]').click();
  await nombre.fill('Marca123');
  await expect(nombre).toHaveValue('Marca');
  await nombre.fill('A'.repeat(21));

  await expect(nombre).toHaveValue('A'.repeat(20));
  await expect(nombre).toHaveClass(/is-valid/);
  await expect(page.locator('#modalRegistrar')).toBeVisible();
});