import { expect, test } from '@playwright/test';
import {
  abrirModuloAdmin,
  confirmarAlerta,
  eliminarFila,
  filaPorTexto,
  nombreDePrueba,
} from '../admin-test-support';

test('humo del módulo de categorías', async ({ page }) => {
  await abrirModuloAdmin(page, 'categoria', 'Categorías');

  await expect(page.locator('#table1 thead')).toContainText('Código');
  await expect(page.locator('#table1 thead')).toContainText('Nombre');

  const nombre = nombreDePrueba('Categoria');
  await page.getByRole('button', { name: 'Registrar Categoría' }).click();

  const modal = page.locator('#modalRegistrar');
  await expect(modal).toBeVisible();
  await page.locator('#nombre_categoria').fill(nombre);
  await page.locator('#formRegistrarCategoria button[type="submit"]').click();
  await confirmarAlerta(page);

  const fila = await filaPorTexto(page, nombre);
  await eliminarFila(
    page,
    fila,
    'button[data-bs-target="#modalEliminar"]',
    '#modalEliminar',
    '#formEliminarCategoria button[type="submit"]',
  );
});
