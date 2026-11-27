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

const titulo = 'Categorías';
const modalEliminar = '#modalEliminar';
const botonEliminar = 'button[data-bs-target="#modalEliminar"]';

async function registrarCategoria(page: Parameters<typeof abrirModuloAdmin>[0], nombre: string) {
  await page.getByRole('button', { name: 'Registrar Categoría' }).click();
  await page.locator('#nombre_categoria').fill(nombre);
  await page.locator('#formRegistrarCategoria button[type="submit"]').click();
  await confirmarAlerta(page);
  return filaPorTexto(page, nombre);
}

test('registrar categoría', async ({ page }) => {
  await abrirModuloAdmin(page, 'categoria', titulo);
  const nombre = nombreDePrueba('Categoria');
  const fila = await registrarCategoria(page, nombre);
  await expect(fila).toContainText(nombre);
  await eliminarFila(page, fila, botonEliminar, modalEliminar, '#formEliminarCategoria button[type="submit"]');
});

test('editar categoría', async ({ page }) => {
  await abrirModuloAdmin(page, 'categoria', titulo);
  const nombreOriginal = nombreDePrueba('Categoria');
  const nombreEditado = nombreDePrueba('Editada');
  const filaOriginal = await registrarCategoria(page, nombreOriginal);

  await filaOriginal.locator('button[data-bs-target="#modalEditar"]').click();
  await expect(page.locator('#modalEditar')).toBeVisible();
  await page.locator('#edit_nombre_categoria').fill(nombreEditado);
  await page.locator('#formEditarCategoria button[type="submit"]').click();
  await confirmarAlerta(page);

  const filaEditada = await filaPorTexto(page, nombreEditado);
  await eliminarFila(page, filaEditada, botonEliminar, modalEliminar, '#formEliminarCategoria button[type="submit"]');
});

test('consultar categorías', async ({ page }) => {
  await abrirModuloAdmin(page, 'categoria', titulo);
  const nombre = nombreDePrueba('Categoria');
  const fila = await registrarCategoria(page, nombre);

  await expect(page.locator('#table1 thead')).toContainText('Código');
  await expect(page.locator('#table1 thead')).toContainText('Nombre');
  await expect(fila).toContainText(nombre);
  await eliminarFila(page, fila, botonEliminar, modalEliminar, '#formEliminarCategoria button[type="submit"]');
});

test('eliminar categoría', async ({ page }) => {
  await abrirModuloAdmin(page, 'categoria', titulo);
  const nombre = nombreDePrueba('Categoria');
  const fila = await registrarCategoria(page, nombre);
  await eliminarFila(page, fila, botonEliminar, modalEliminar, '#formEliminarCategoria button[type="submit"]');
});

test('buscar categoría', async ({ page }) => {
  await abrirModuloAdmin(page, 'categoria', titulo);
  const nombre = nombreDePrueba('Categoria');
  const fila = await registrarCategoria(page, nombre);
  const filaEncontrada = await buscarFila(page, nombre);
  await expect(filaEncontrada).toContainText(nombre);
  await eliminarFila(page, fila, botonEliminar, modalEliminar, '#formEliminarCategoria button[type="submit"]');
});

test('validar los campos del formulario de categoría', async ({ page }) => {
  await abrirModuloAdmin(page, 'categoria', titulo);
  await page.getByRole('button', { name: 'Registrar Categoría' }).click();

  const nombre = page.locator('#nombre_categoria');
  await expect(page.locator('#nombre_categoria:invalid')).toBeVisible();
  await page.locator('#formRegistrarCategoria button[type="submit"]').click();
  await nombre.fill('Categoria123');
  await expect(nombre).toHaveValue('Categoria');
  await nombre.fill('A'.repeat(21));

  await assertInputInvalido(page, '#nombre_categoria');
  await expect(page.locator('#modalRegistrar')).toBeVisible();
  await expect(nombre).toHaveValue('A'.repeat(20));
});