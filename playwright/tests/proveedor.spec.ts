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
  numeroDePrueba,
  sufijoUnico,
} from './admin-test-support';

const titulo = 'Proveedores';
const modalEliminar = '#modalEliminar';
const botonEliminar = 'button[data-bs-target="#modalEliminar"]';

async function registrarProveedor(page: Parameters<typeof abrirModuloAdmin>[0], nombre: string) {
  const sufijo = sufijoUnico();
  await page.getByRole('button', { name: 'Registrar proveedor' }).click();
  await page.locator('#cedula').fill(numeroDePrueba(8));
  await page.locator('#nombre').fill(nombre);
  await page.locator('#apellido').fill(nombreDePrueba('Prueba'));
  await page.locator('#rif').fill(`J${numeroDePrueba(9)}`);
  await page.locator('#telefono').fill(numeroDePrueba(11));
  await page.locator('#correo').fill(`test${sufijo}@example.com`);
  await page.locator('#formRegistrarProveedor button[type="submit"]').click();
  await confirmarAlerta(page);
  return filaPorTexto(page, nombre);
}

test('registrar proveedor', async ({ page }) => {
  await abrirModuloAdmin(page, 'proveedor', titulo);
  const nombre = nombreDePrueba('Sumi');
  const fila = await registrarProveedor(page, nombre);
  await expect(fila).toContainText(nombre);
  await eliminarFila(page, fila, botonEliminar, modalEliminar, '#formEliminarProveedor button[type="submit"]');
});

test('editar proveedor', async ({ page }) => {
  await abrirModuloAdmin(page, 'proveedor', titulo);
  const nombreOriginal = nombreDePrueba('Sumi');
  const nombreEditado = nombreDePrueba('Edit');
  const filaOriginal = await registrarProveedor(page, nombreOriginal);

  await filaOriginal.locator('button[data-bs-target="#modalEditar"]').click();
  await expect(page.locator('#modalEditar')).toBeVisible();
  await page.locator('#edit_nombre').fill(nombreEditado);
  await page.locator('#formEditarProveedor button[type="submit"]').click();
  await confirmarAlerta(page);

  const filaEditada = await filaPorTexto(page, nombreEditado);
  await eliminarFila(page, filaEditada, botonEliminar, modalEliminar, '#formEliminarProveedor button[type="submit"]');
});

test('consultar proveedores', async ({ page }) => {
  await abrirModuloAdmin(page, 'proveedor', titulo);
  const nombre = nombreDePrueba('Sumi');
  const fila = await registrarProveedor(page, nombre);

  await expect(page.locator('#table1 thead')).toContainText('Cédula');
  await expect(page.locator('#table1 thead')).toContainText('Correo');
  await expect(fila).toContainText(nombre);
  await eliminarFila(page, fila, botonEliminar, modalEliminar, '#formEliminarProveedor button[type="submit"]');
});

test('eliminar proveedor', async ({ page }) => {
  await abrirModuloAdmin(page, 'proveedor', titulo);
  const nombre = nombreDePrueba('Sumi');
  const fila = await registrarProveedor(page, nombre);
  await eliminarFila(page, fila, botonEliminar, modalEliminar, '#formEliminarProveedor button[type="submit"]');
});

test('buscar proveedor', async ({ page }) => {
  await abrirModuloAdmin(page, 'proveedor', titulo);
  const nombre = nombreDePrueba('Sumi');
  const fila = await registrarProveedor(page, nombre);
  const filaEncontrada = await buscarFila(page, nombre);
  await expect(filaEncontrada).toContainText(nombre);
  await eliminarFila(page, fila, botonEliminar, modalEliminar, '#formEliminarProveedor button[type="submit"]');
});

test('validar los campos del formulario de proveedor', async ({ page }) => {
  await abrirModuloAdmin(page, 'proveedor', titulo);
  await page.getByRole('button', { name: 'Registrar proveedor' }).click();

  await page.locator('#cedula').fill('abc');
  await page.locator('#nombre').fill('123');
  await page.locator('#apellido').fill('456');
  await page.locator('#rif').fill('JABC');
  await page.locator('#telefono').fill('telefono');
  await page.locator('#correo').fill('no-es-un-correo');
  await page.locator('#formRegistrarProveedor button[type="submit"]').click();

  for (const selector of ['#cedula', '#nombre', '#apellido', '#rif', '#telefono', '#correo']) {
    await assertInputInvalido(page, selector);
  }
  await expect(page.locator('#modalRegistrar')).toBeVisible();
});