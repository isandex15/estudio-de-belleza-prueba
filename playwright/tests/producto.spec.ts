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

const titulo = 'Productos (Inventario)';
const modalEliminar = '#modalEliminar';
const botonEliminar = 'button[data-bs-target="#modalEliminar"]';

async function registrarProducto(page: Parameters<typeof abrirModuloAdmin>[0], nombre: string) {
  await page.getByRole('button', { name: 'Registrar Producto' }).click();
  await expect(page.locator('#modalRegistrar')).toBeVisible();
  await page.locator('#nombre_producto').fill(nombre);
  await page.locator('#precio_producto').fill('10.50');
  await page.locator('#stock').fill('5');
  await page.locator('#fecha_vencimiento').fill(fechaRelativa(30));

  for (const selector of [
    '#cod_marca',
    '#cod_categoria',
    '#cod_unidad',
    '#cod_presentacion',
    '#cod_tipo_producto',
    '#cod_medida',
  ]) {
    await page.locator(selector).selectOption({ index: 0 });
  }

  await page.locator('#formRegistrarProducto button[type="submit"]').click();
  await confirmarAlerta(page);
  return filaPorTexto(page, nombre);
}

test('registrar producto', async ({ page }) => {
  await abrirModuloAdmin(page, 'producto', titulo);
  const nombre = nombreDePrueba('Producto', 18);
  const fila = await registrarProducto(page, nombre);
  await expect(fila).toContainText(nombre);
  await eliminarFila(page, fila, botonEliminar, modalEliminar, '#formEliminarProducto button.btn-danger');
});

test('editar producto', async ({ page }) => {
  await abrirModuloAdmin(page, 'producto', titulo);
  const nombreOriginal = nombreDePrueba('Producto', 18);
  const nombreEditado = nombreDePrueba('EditProd', 18);
  const filaOriginal = await registrarProducto(page, nombreOriginal);

  await filaOriginal.locator('button[data-bs-target="#modalEditar"]').click();
  await expect(page.locator('#modalEditar')).toBeVisible();
  await page.locator('#edit_nombre_producto').fill(nombreEditado);
  await page.locator('#formEditarProducto button[type="submit"]').click();
  await confirmarAlerta(page);

  const filaEditada = await filaPorTexto(page, nombreEditado);
  await eliminarFila(page, filaEditada, botonEliminar, modalEliminar, '#formEliminarProducto button.btn-danger');
});

test('consultar detalle de producto', async ({ page }) => {
  await abrirModuloAdmin(page, 'producto', titulo);
  const nombre = nombreDePrueba('Producto', 18);
  const fila = await registrarProducto(page, nombre);

  await fila.locator('button[data-bs-target="#modalVer"]').click();
  await expect(page.locator('#modalVer')).toBeVisible();
  await expect(page.locator('#ver_nombre')).toHaveText(nombre);

  await page.goto('http://localhost:5000/admin?ruta=producto');
  const filaActualizada = await filaPorTexto(page, nombre);
  await eliminarFila(page, filaActualizada, botonEliminar, modalEliminar, '#formEliminarProducto button.btn-danger');
});

test('eliminar producto', async ({ page }) => {
  await abrirModuloAdmin(page, 'producto', titulo);
  const nombre = nombreDePrueba('Producto', 18);
  const fila = await registrarProducto(page, nombre);
  await eliminarFila(page, fila, botonEliminar, modalEliminar, '#formEliminarProducto button.btn-danger');
});

test('buscar producto', async ({ page }) => {
  await abrirModuloAdmin(page, 'producto', titulo);
  const nombre = nombreDePrueba('Producto', 18);
  const fila = await registrarProducto(page, nombre);
  const filaEncontrada = await buscarFila(page, nombre);
  await expect(filaEncontrada).toContainText(nombre);
  await eliminarFila(page, fila, botonEliminar, modalEliminar, '#formEliminarProducto button.btn-danger');
});

test('validar los campos del formulario de producto', async ({ page }) => {
  await abrirModuloAdmin(page, 'producto', titulo);
  await page.getByRole('button', { name: 'Registrar Producto' }).click();

  await page.locator('#nombre_producto').fill('Producto@');
  await page.locator('#precio_producto').fill('0');
  await page.locator('#stock').fill('5');
  for (const selector of [
    '#cod_marca',
    '#cod_categoria',
    '#cod_unidad',
    '#cod_presentacion',
    '#cod_tipo_producto',
    '#cod_medida',
  ]) {
    await page.locator(selector).selectOption({ index: 0 });
  }

  await page.locator('#formRegistrarProducto button[type="submit"]').click();
  await assertInputInvalido(page, '#fecha_vencimiento');

  await page.locator('#fecha_vencimiento').fill(fechaRelativa(30));
  await page.locator('#formRegistrarProducto button[type="submit"]').click();
  await assertInputInvalido(page, '#nombre_producto');
  await assertInputInvalido(page, '#precio_producto');

  const stock = page.locator('#stock');
  await stock.fill('2.5');
  await expect(stock).toHaveValue('25');
  await page.locator('#formRegistrarProducto button[type="submit"]').click();
  await expect(page.locator('#modalRegistrar')).toBeVisible();
});