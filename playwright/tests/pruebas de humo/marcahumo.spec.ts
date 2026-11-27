import { expect, test } from '@playwright/test';
import {
  abrirModuloAdmin,
  confirmarAlerta,
  eliminarFila,
  filaPorTexto,
  nombreDePrueba,
} from '../admin-test-support';

test('humo del módulo de marcas', async ({ page }) => {
  await abrirModuloAdmin(page, 'marca', 'Marcas');

  await expect(page.locator('#table1 thead')).toContainText('Código');
  await expect(page.locator('#table1 thead')).toContainText('Nombre');

  const nombre = nombreDePrueba('Marca');
  await page.getByRole('button', { name: 'Registrar marca' }).click();

  const modal = page.locator('#modalRegistrar');
  await expect(modal).toBeVisible();
  await page.locator('#nombre_marca').fill(nombre);
  await page.locator('#formRegistrarMarca button[type="submit"]').click();
  await confirmarAlerta(page);

  const fila = await filaPorTexto(page, nombre);
  await eliminarFila(
    page,
    fila,
    'button[data-bs-target="#modalEliminar"]',
    '#modalEliminar',
    '#formEliminarMarca button[type="submit"]',
  );
});
