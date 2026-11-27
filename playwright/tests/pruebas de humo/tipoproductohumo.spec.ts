import { expect, test } from '@playwright/test';
import {
  abrirModuloAdmin,
  confirmarAlerta,
  eliminarFila,
  filaPorTexto,
  nombreDePrueba,
} from '../admin-test-support';

test('humo del módulo de tipos de producto', async ({ page }) => {
  await abrirModuloAdmin(page, 'tipoproducto', 'Tipos de Productos');

  await expect(page.locator('#table1 thead')).toContainText('Código');
  await expect(page.locator('#table1 thead')).toContainText('Nombre');

  const nombre = nombreDePrueba('Tipo');
  await page.getByRole('button', { name: 'Registrar Tipo de Producto' }).click();

  const modal = page.locator('#modalRegistrar');
  await expect(modal).toBeVisible();
  await page.locator('#nombre_tipo_producto').fill(nombre);
  await page.locator('#formRegistrarTipoProducto button[type="submit"]').click();
  await confirmarAlerta(page);

  const fila = await filaPorTexto(page, nombre);
  await eliminarFila(
    page,
    fila,
    'button[data-bs-target="#modalEliminar"]',
    '#modalEliminar',
    '#formEliminarTipoProducto button[type="submit"]',
  );
});
