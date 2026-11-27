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

const titulo = 'Tipos de Productos';
const modalEliminar = '#modalEliminar';
const botonEliminar = 'button[data-bs-target="#modalEliminar"]';

async function registrarTipoProducto(page: Parameters<typeof abrirModuloAdmin>[0], nombre: string) {
  await page.getByRole('button', { name: 'Registrar Tipo de Producto' }).click();
  await page.locator('#nombre_tipo_producto').fill(nombre);
  await page.locator('#formRegistrarTipoProducto button[type="submit"]').click();
  await confirmarAlerta(page);
  return filaPorTexto(page, nombre);
}

test('registrar tipo de producto', async ({ page }) => {
  await abrirModuloAdmin(page, 'tipoproducto', titulo);
  const nombre = nombreDePrueba('Tipo');
  const fila = await registrarTipoProducto(page, nombre);
  await expect(fila).toContainText(nombre);
  await eliminarFila(page, fila, botonEliminar, modalEliminar, '#formEliminarTipoProducto button[type="submit"]');
});

test('editar tipo de producto', async ({ page }) => {
  await abrirModuloAdmin(page, 'tipoproducto', titulo);
  const nombreOriginal = nombreDePrueba('Tipo');
  const nombreEditado = nombreDePrueba('Editado');
  const filaOriginal = await registrarTipoProducto(page, nombreOriginal);

  await filaOriginal.locator('button[data-bs-target="#modalEditar"]').click();
  await expect(page.locator('#modalEditar')).toBeVisible();
  await page.locator('#edit_nombre').fill(nombreEditado);
  await page.locator('#formEditarTipoProducto button[type="submit"]').click();
  await confirmarAlerta(page);

  const filaEditada = await filaPorTexto(page, nombreEditado);
  await eliminarFila(page, filaEditada, botonEliminar, modalEliminar, '#formEliminarTipoProducto button[type="submit"]');
});

test('consultar tipos de producto', async ({ page }) => {
  await abrirModuloAdmin(page, 'tipoproducto', titulo);
  const nombre = nombreDePrueba('Tipo');
  const fila = await registrarTipoProducto(page, nombre);

  await expect(page.locator('#table1 thead')).toContainText('Código');
  await expect(page.locator('#table1 thead')).toContainText('Nombre');
  await expect(fila).toContainText(nombre);
  await eliminarFila(page, fila, botonEliminar, modalEliminar, '#formEliminarTipoProducto button[type="submit"]');
});

test('eliminar tipo de producto', async ({ page }) => {
  await abrirModuloAdmin(page, 'tipoproducto', titulo);
  const nombre = nombreDePrueba('Tipo');
  const fila = await registrarTipoProducto(page, nombre);
  await eliminarFila(page, fila, botonEliminar, modalEliminar, '#formEliminarTipoProducto button[type="submit"]');
});

test('buscar tipo de producto', async ({ page }) => {
  await abrirModuloAdmin(page, 'tipoproducto', titulo);
  const nombre = nombreDePrueba('Tipo');
  const fila = await registrarTipoProducto(page, nombre);
  const filaEncontrada = await buscarFila(page, nombre);
  await expect(filaEncontrada).toContainText(nombre);
  await eliminarFila(page, fila, botonEliminar, modalEliminar, '#formEliminarTipoProducto button[type="submit"]');
});

test('validar los campos del formulario de tipo de producto', async ({ page }) => {
  await abrirModuloAdmin(page, 'tipoproducto', titulo);
  await page.getByRole('button', { name: 'Registrar Tipo de Producto' }).click();

  const nombre = page.locator('#nombre_tipo_producto');
  await expect(page.locator('#nombre_tipo_producto:invalid')).toBeVisible();
  await page.locator('#formRegistrarTipoProducto button[type="submit"]').click();
  await nombre.fill('Tipo123');
  await expect(nombre).toHaveValue('Tipo');
  await nombre.fill('A'.repeat(21));

  await expect(nombre).toHaveValue('A'.repeat(20));
  await expect(nombre).toHaveClass(/is-valid/);
  await expect(page.locator('#modalRegistrar')).toBeVisible();
});