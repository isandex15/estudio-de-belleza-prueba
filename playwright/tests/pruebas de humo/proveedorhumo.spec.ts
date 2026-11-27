import { expect, test } from '@playwright/test';
import {
  abrirModuloAdmin,
  confirmarAlerta,
  eliminarFila,
  filaPorTexto,
  nombreDePrueba,
  numeroDePrueba,
  sufijoUnico,
} from '../admin-test-support';

test('humo del módulo de proveedores', async ({ page }) => {
  await abrirModuloAdmin(page, 'proveedor', 'Proveedores');

  await expect(page.locator('#table1 thead')).toContainText('Cédula');
  await expect(page.locator('#table1 thead')).toContainText('Nombre');

  const nombre = nombreDePrueba('Sumi');
  await page.getByRole('button', { name: 'Registrar proveedor' }).click();

  const modal = page.locator('#modalRegistrar');
  await expect(modal).toBeVisible();
  await page.locator('#cedula').fill(numeroDePrueba(8));
  await page.locator('#nombre').fill(nombre);
  await page.locator('#apellido').fill(nombreDePrueba('Prueba'));
  await page.locator('#rif').fill(`J${numeroDePrueba(9)}`);
  await page.locator('#telefono').fill(numeroDePrueba(11));
  await page.locator('#correo').fill(`test${sufijoUnico()}@example.com`);
  await page.locator('#formRegistrarProveedor button[type="submit"]').click();
  await confirmarAlerta(page);

  const fila = await filaPorTexto(page, nombre);
  await eliminarFila(
    page,
    fila,
    'button[data-bs-target="#modalEliminar"]',
    '#modalEliminar',
    '#formEliminarProveedor button[type="submit"]',
  );
});
